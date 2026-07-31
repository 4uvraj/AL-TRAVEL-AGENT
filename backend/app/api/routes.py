from fastapi import APIRouter, HTTPException
from app.models.schemas import TripRequest, ChatMessage, RouteRequest
from app.agents.travel_graph import run_travel_planner
from app.services.route_optimizer import optimize_route
from app.services.chat_service import run_chat

router = APIRouter()


import json
from fastapi.responses import StreamingResponse

# Simple in-memory cache for ultra-fast repeated searches
_TRIP_CACHE = {}

@router.post("/plan-trip")
def plan_trip(request: TripRequest):
    """
    Invoke the full LangGraph multi-agent pipeline and stream progress.
    """
    try:
        cache_key = f"{request.destination}_{request.days}_{request.budget_range}_{request.preferences}_{request.start_date}".lower().strip()
        
        if cache_key in _TRIP_CACHE:
            # Return cached result instantly by yielding the complete event
            def cached_stream():
                yield f"data: {json.dumps({'type': 'progress', 'message': 'Loaded from cache...'})}\n\n"
                yield f"data: {json.dumps({'type': 'complete', 'result': _TRIP_CACHE[cache_key]})}\n\n"
            return StreamingResponse(cached_stream(), media_type="text/event-stream")

        from app.agents.travel_graph import stream_travel_planner
        
        # We need a wrapper generator to cache the final result
        def caching_generator():
            generator = stream_travel_planner(
                destination=request.destination,
                days=request.days,
                budget_range=request.budget_range,
                preferences=request.preferences or "",
                start_date=request.start_date or "",
            )
            for chunk in generator:
                if chunk.startswith("data: "):
                    try:
                        data = json.loads(chunk[6:])
                        if data.get("type") == "complete":
                            _TRIP_CACHE[cache_key] = data["result"]
                    except:
                        pass
                yield chunk

        return StreamingResponse(caching_generator(), media_type="text/event-stream")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat")
def chat(request: ChatMessage):
    """
    Conversational travel assistant endpoint.
    """
    try:
        reply = run_chat(message=request.message, history=request.history)
        return {"status": "success", "reply": reply}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/optimize-route")
def optimize_route_endpoint(request: RouteRequest):
    """
    Standalone DSA route optimization — accepts a list of locations and
    returns the optimized visiting sequence using the nearest-neighbour TSP.
    """
    try:
        result = optimize_route(
            locations=request.locations,
            start_location=request.start_location,
        )
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
