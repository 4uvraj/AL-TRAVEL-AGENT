"""
Multi-Agent System using LangGraph — Step 3
Agents:
  1. Planner Agent         – breaks query into structured itinerary skeleton
  2. Places Retrieval Agent (RAG) – fetches places/hotels from ChromaDB
  3. Budget Agent          – estimates cost breakdown
  4. Route Optimization Agent – calls DSA service with real GPS
  5. Weather + Country Agent  – fetches live weather & country info
  6. Explainer Agent       – produces human-friendly summary

All agents share a typed AgentState dict passed through the LangGraph StateGraph.
"""
import os, json
from typing import TypedDict, List, Optional, Any
from dotenv import load_dotenv

load_dotenv(override=True)

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END

from app.services.route_optimizer import optimize_route
from app.services.weather_service import get_weather_forecast
from app.services.country_service import get_country_info
from app.services.geo_service import geocode_city
from app.rag.mock_data import MOCK_PLACES


# ── Shared State ──────────────────────────────────────────────────────────────

class AgentState(TypedDict):
    destination: str
    days: int
    budget_range: str
    preferences: str
    start_date: str
    # outputs accumulated across agents
    planner_output: Optional[dict]
    places_output: Optional[List[dict]]
    budget_output: Optional[dict]
    route_output: Optional[dict]
    weather_output: Optional[List[dict]]
    country_output: Optional[dict]
    destination_coords: Optional[tuple]
    final_itinerary: Optional[dict]
    error: Optional[str]


# ── LLM Factory ───────────────────────────────────────────────────────────────

def _get_llm(temperature: float = 0.3) -> ChatOpenAI:
    return ChatOpenAI(
        model="gpt-4o-mini",
        temperature=temperature,
        api_key=os.getenv("OPENAI_API_KEY", ""),
    )


# ── Agent 1: Planner ──────────────────────────────────────────────────────────

def planner_agent(state: AgentState) -> AgentState:
    """Generate a structured day-by-day itinerary with REAL place and hotel names."""
    llm = _get_llm()
    budget_map = {
        "budget": "budget traveler (hostels, local dhabas, autos/buses, free attractions)",
        "mid-range": "mid-range traveler (3-star hotels, good restaurants, taxis/Ola)",
        "luxury": "luxury traveler (5-star hotels, fine dining, private transfers)"
    }
    budget_desc = budget_map.get(state['budget_range'], state['budget_range'])

    prompt = f"""You are an expert travel planner with encyclopedic knowledge of real hotels, restaurants, and attractions worldwide.

Create a detailed {state['days']}-day itinerary for a {budget_desc} visiting {state['destination']}.
User preferences: {state['preferences'] or 'general sightseeing, local food, culture'}
Start date: {state['start_date'] or 'flexible'}

CRITICAL RULES:
- ABSOLUTELY NO HALLUCINATIONS: You must guarantee that every single place, hotel, and attraction actually exists exactly in or directly adjacent to {state['destination']}.
- If you don't confidently know 3 real places for a day, use major verified regional landmarks. Do not invent names.
- meals_cost and transport_cost MUST be realistic INR amounts for {state['destination']} (e.g. Goa beach shack meal ≈ ₹300-800, auto ≈ ₹100-300)
- Each day should have a unique theme and real named places to visit
- Hotel must actually exist in {state['destination']}
- DO NOT use placeholder names like "place1" or "Hotel ABC"

Return ONLY valid JSON (no markdown, no extra text):
{{
  "travel_style": "{state['budget_range']}",
  "summary": "string — 2-3 sentences describing this specific trip to {state['destination']}",
  "days": [
    {{
      "day": 1,
      "date": "{state['start_date'] or 'Day 1'}",
      "location": "{state['destination']}",
      "theme": "string — specific theme for this day (e.g. 'North Goa Beaches & Nightlife')",
      "planned_places": ["Real Place Name 1", "Real Place Name 2", "Real Place Name 3"],
      "hotel_name": "Real existing hotel name in {state['destination']}",
      "meals_cost": <realistic INR integer for {state['destination']} {state['budget_range']}>,
      "transport_cost": <realistic INR integer>
    }}
  ],
  "top_tips": ["Specific actionable tip for {state['destination']}", "tip2", "tip3", "tip4"]
}}"""

    try:
        response = llm.invoke([
            SystemMessage(content="You are a precise travel planning assistant. Always use real, verified place names. Return ONLY valid JSON."),
            HumanMessage(content=prompt)
        ])
        raw = response.content.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        state["planner_output"] = json.loads(raw)
    except Exception as e:
        state["error"] = f"Planner agent failed: {e}"
        state["planner_output"] = _fallback_plan(state)
    return state


def _fallback_plan(state: AgentState) -> dict:
    """Return a deterministic fallback plan when LLM is unavailable."""
    days = []
    for d in range(1, state["days"] + 1):
        days.append({
            "day": d, "date": f"Day {d}", "location": state["destination"],
            "theme": "City Exploration", "planned_places": ["City Center", "Local Market", "Museum"],
            "hotel_name": "Central Hotel", "meals_cost": 2000, "transport_cost": 500
        })
    return {
        "travel_style": state["budget_range"],
        "summary": f"A {state['days']}-day trip to {state['destination']}.",
        "days": days,
        "top_tips": ["Book hotels in advance", "Use public transport", "Try local cuisine"]
    }


# ── Agent 2: Places Retrieval (RAG) ──────────────────────────────────────────

def places_retrieval_agent(state: AgentState) -> AgentState:
    """Generate real-world places, hotels, and restaurants using LLM knowledge."""
    # Always use LLM for real-world accuracy — ignore the tiny mock dataset
    try:
        llm = _get_llm(0.2)
        budget_map = {
            "budget": "budget (₹500-2000/night hotels, cheap eats)",
            "mid-range": "mid-range (₹3000-8000/night hotels, good restaurants)",
            "luxury": "luxury (₹15000+/night 5-star hotels, fine dining)"
        }
        budget_desc = budget_map.get(state['budget_range'], state['budget_range'])

        prompt = f"""Generate detailed real-world travel information for {state['destination']} for a {budget_desc} traveler.

Return ONLY a valid JSON array of 6-8 items mixing attractions, hotels, and restaurants.
Each item MUST be a real, existing place in or near {state['destination']}.

Schema:
[
  {{
    "name": "Exact real name of the place (e.g. 'Baga Beach', 'Taj Fort Aguada Resort', 'Thalassa Greek Restaurant')",
    "type": "attraction" | "hotel" | "restaurant" | "beach" | "temple" | "market" | "museum" | "park",
    "location": "{state['destination']}",
    "description": "2-3 sentence real description of this specific place",
    "cost": <realistic INR cost: entry fee for attraction, avg nightly rate for hotel, avg meal cost for restaurant. 0 if free>,
    "rating": <real approximate rating 3.5-5.0>
  }}
]

IMPORTANT:
1. Include a mix of at least 2 attractions/beaches, 2 hotels matching {state['budget_range']} budget, and 2 restaurants/food spots.
2. ABSOLUTELY NO HALLUCINATIONS. Every name must be a REAL verifiable place that exists exactly in {state['destination']}. Do not include places from neighboring cities unless it's a common day-trip."""

        response = llm.invoke([
            SystemMessage(content="You are a travel data expert. Return only a valid JSON array of real places. No placeholders."),
            HumanMessage(content=prompt)
        ])
        raw = response.content.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        relevant = json.loads(raw)
        for i, p in enumerate(relevant):
            p["id"] = f"real_{i}"
    except Exception as e:
        print(f"[places_retrieval] LLM generation failed: {e}")
        # Final fallback: generic but labelled correctly
        relevant = [
            {"id": "fb_0", "name": f"{state['destination']} City Tour", "type": "attraction",
             "location": state["destination"], "description": "Guided city tour covering main landmarks.",
             "cost": 500, "rating": 4.0},
            {"id": "fb_1", "name": f"Hotel Central {state['destination']}", "type": "hotel",
             "location": state["destination"], "description": "Centrally located comfortable hotel.",
             "cost": 3500, "rating": 3.8},
        ]

    state["places_output"] = relevant
    return state


# ── Agent 3: Budget ───────────────────────────────────────────────────────────

BUDGET_MULTIPLIERS_INR = {"budget": 0.6, "mid-range": 1.0, "luxury": 2.5}

def budget_agent(state: AgentState) -> AgentState:
    """Calculate realistic city-aware cost breakdown in INR."""
    plan = state.get("planner_output") or {}
    multiplier = BUDGET_MULTIPLIERS_INR.get(state["budget_range"], 1.0)
    days_data = plan.get("days", [])

    # Use costs from LLM planner (city-specific) rather than hardcoded defaults
    food_total      = sum(d.get("meals_cost", 1500) for d in days_data) * multiplier
    transport_total = sum(d.get("transport_cost", 400) for d in days_data) * multiplier

    # Use actual hotel costs from places data if available
    places = state.get("places_output") or []
    hotel_places = [p for p in places if p.get("type") == "hotel"]
    if hotel_places:
        avg_hotel_cost = sum(p.get("cost", 3500) for p in hotel_places) / len(hotel_places)
        accommodation_total = avg_hotel_cost * state["days"]
    else:
        base_hotel = {"budget": 1500, "mid-range": 4500, "luxury": 18000}.get(state["budget_range"], 4500)
        accommodation_total = base_hotel * state["days"]

    # Sum entry fees / activity costs from non-hotel places
    activity_places = [p for p in places if p.get("type") != "hotel"]
    activities_total = sum(p.get("cost", 300) for p in activity_places[:6]) * multiplier

    grand_total = food_total + transport_total + accommodation_total + activities_total

    state["budget_output"] = {
        "accommodation_total": round(accommodation_total, 2),
        "food_total":          round(food_total, 2),
        "transport_total":     round(transport_total, 2),
        "activities_total":    round(activities_total, 2),
        "grand_total":         round(grand_total, 2),
        "currency":            "INR",
        "per_day_average":     round(grand_total / max(state["days"], 1), 2),
    }
    return state


# ── Agent 4: Route Optimization ───────────────────────────────────────────────

def route_optimization_agent(state: AgentState) -> AgentState:
    """Run nearest-neighbor TSP on the planned places using real GPS coordinates."""
    plan = state.get("planner_output") or {}
    all_places: List[str] = []
    for day in plan.get("days", []):
        all_places.extend(day.get("planned_places", []))

    # Deduplicate while preserving order
    seen, unique = set(), []
    for p in all_places:
        if p not in seen:
            seen.add(p)
            unique.append(p)

    if unique:
        state["route_output"] = optimize_route(unique, city_hint=state["destination"])
    else:
        state["route_output"] = {"sequence": [], "total_distance_km": 0, "estimated_travel_hours": 0, "route_details": []}
    return state


# ── Agent 5: Weather + Country ────────────────────────────────────────────────

def weather_country_agent(state: AgentState) -> AgentState:
    """Fetch real-time weather forecast and country info for the destination."""
    destination = state["destination"]

    # 1. Geocode the destination city to get lat/lon
    coords = geocode_city(destination)
    state["destination_coords"] = coords

    # 2. Fetch weather forecast
    if coords:
        forecast = get_weather_forecast(coords[0], coords[1], days=state["days"])
        state["weather_output"] = forecast
    else:
        state["weather_output"] = []

    # 3. Fetch country info — try to extract country from destination (heuristic)
    # We no longer ask LLM for this to prevent unnecessary API rate limits!
    # Instead, we just assume the destination string has enough info (e.g. "Paris, France" -> "France")
    # Or rely on our RAG/Country API's fuzzy matching.
    
    country_hint = destination.split(",")[-1].strip() if "," in destination else destination
    state["country_output"] = get_country_info(country_hint) or {}
    return state


# ── Agent 6: Explainer (Synthesizer) ─────────────────────────────────────────

def explainer_agent(state: AgentState) -> AgentState:
    """Combine all agent outputs into the final structured itinerary."""
    plan    = state.get("planner_output") or _fallback_plan(state)
    budget  = state.get("budget_output")  or {}
    route   = state.get("route_output")   or {}
    places  = state.get("places_output")  or []
    weather = state.get("weather_output") or []
    country = state.get("country_output") or {}

    route_sequence = route.get("sequence", [])

    # Build enriched day objects
    enriched_days = []
    for i, d in enumerate(plan.get("days", [])):
        day_places = d.get("planned_places", [])
        
        # 1. Reorder day_places to match the optimal TSP sequence route
        ordered_day_places = []
        for loc in route_sequence:
            if loc in day_places:
                ordered_day_places.append(loc)
        # Append any leftover places that weren't in the route somehow
        for place in day_places:
            if place not in ordered_day_places:
                ordered_day_places.append(place)
                
        # 2. Build activity objects matching RAG data fuzzily
        activities = []
        for p_name in ordered_day_places:
            # Try to find a match in the places array (case-insensitive substring)
            match = next((p for p in places if p["name"].lower() in p_name.lower() or p_name.lower() in p["name"].lower()), None)
            
            if match:
                activities.append({
                    "name": p_name,
                    "type": match.get("type", "attraction"),
                    "description": match.get("description", "A highly recommended spot to visit."),
                    "duration_hours": 2.0,
                    "cost": match.get("cost", 300),
                    "rating": match.get("rating", 4.5),
                })
            else:
                activities.append({
                    "name": p_name,
                    "type": "attraction",
                    "description": f"Explore {p_name}, a highly recommended spot in {state['destination']}.",
                    "duration_hours": 2.0,
                    "cost": 250, # fallback cost
                    "rating": 4.5,
                })

        # Attach weather for this day index (if available)
        day_weather = weather[i] if i < len(weather) else None

        multiplier = BUDGET_MULTIPLIERS_INR.get(state["budget_range"], 1.0)
        enriched_days.append({
            "day": d["day"],
            "date": d["date"],
            "location": d["location"],
            "theme": d.get("theme", "Exploration"),
            "activities": activities,
            "hotel": d.get("hotel_name", "Local Hotel"),
            "meals_cost": round(d.get("meals_cost", 2000) * multiplier, 2),
            "transport_cost": round(d.get("transport_cost", 500) * multiplier, 2),
            "activities_cost": round(sum(a["cost"] for a in activities), 2),
            "day_total": round(
                d.get("meals_cost", 2000) * multiplier +
                d.get("transport_cost", 500) * multiplier +
                sum(a["cost"] for a in activities), 2
            ),
            "weather": day_weather,
        })

    state["final_itinerary"] = {
        "destination": state["destination"],
        "total_days": state["days"],
        "travel_style": plan.get("travel_style", state["budget_range"]),
        "summary": plan.get("summary", f"Your {state['days']}-day trip to {state['destination']}."),
        "days": enriched_days,
        "budget": budget,
        "optimized_route": route,
        "recommendations": [p["name"] for p in places],
        "tips": plan.get("top_tips", ["Book in advance", "Carry local currency"]),
        "country_info": country,
    }
    return state


# ── Build and Compile the StateGraph ─────────────────────────────────────────

def build_travel_graph() -> Any:
    workflow = StateGraph(AgentState)

    workflow.add_node("planner",           planner_agent)
    workflow.add_node("places_retrieval",  places_retrieval_agent)
    workflow.add_node("budget",            budget_agent)
    workflow.add_node("route_optimization",route_optimization_agent)
    workflow.add_node("weather_country",   weather_country_agent)
    workflow.add_node("explainer",         explainer_agent)

    # Pipeline: planner → retrieval → budget → route → weather+country → explainer → END
    workflow.set_entry_point("planner")
    workflow.add_edge("planner",            "places_retrieval")
    workflow.add_edge("places_retrieval",   "budget")
    workflow.add_edge("budget",             "route_optimization")
    workflow.add_edge("route_optimization", "weather_country")
    workflow.add_edge("weather_country",    "explainer")
    workflow.add_edge("explainer",          END)

    return workflow.compile()


# Singleton graph (compiled once on import)
travel_graph = build_travel_graph()


def run_travel_planner(destination: str, days: int, budget_range: str,
                       preferences: str = "", start_date: str = "") -> dict:
    """Public interface to invoke the LangGraph pipeline."""
    initial_state: AgentState = {
        "destination": destination,
        "days": days,
        "budget_range": budget_range,
        "preferences": preferences,
        "start_date": start_date,
        "planner_output": None,
        "places_output": None,
        "budget_output": None,
        "route_output": None,
        "weather_output": None,
        "country_output": None,
        "destination_coords": None,
        "final_itinerary": None,
        "error": None,
    }
    result = travel_graph.invoke(initial_state)
    return result.get("final_itinerary") or {}

def stream_travel_planner(destination: str, days: int, budget_range: str,
                       preferences: str = "", start_date: str = ""):
    """Stream LangGraph progress updates and the final result using SSE format."""
    initial_state = {
        "destination": destination, "days": days, "budget_range": budget_range,
        "preferences": preferences, "start_date": start_date,
        "planner_output": None, "places_output": None, "budget_output": None,
        "route_output": None, "weather_output": None, "country_output": None,
        "destination_coords": None, "final_itinerary": None, "error": None,
    }
    
    status_map = {
        "planner": "🧠 Planner Agent: Designing your logical day-by-day outline...",
        "places_retrieval": "🔍 RAG Agent: Fetching verified hotels, restaurants & attractions...",
        "budget": "💰 Budget Agent: Calculating realistic city-specific costs...",
        "route_optimization": "🗺️ Route Agent: Optimizing route sequence using GPS logic...",
        "weather_country": "🌦️ Weather Agent: Syncing live forecast & country metadata...",
        "explainer": "✨ Explainer Agent: Assembling your final travel portfolio...",
    }

    try:
        import json
        for event in travel_graph.stream(initial_state, {"recursion_limit": 50}):
            node_name = list(event.keys())[0]
            if node_name in status_map:
                yield f"data: {json.dumps({'type': 'progress', 'message': status_map[node_name]})}\n\n"
            
            if node_name == "explainer":
                final_itinerary = event[node_name].get("final_itinerary") or {}
                yield f"data: {json.dumps({'type': 'complete', 'result': final_itinerary})}\n\n"
    except Exception as e:
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
