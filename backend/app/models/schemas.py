from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class PlaceActivity(BaseModel):
    name: str
    type: str
    description: str
    duration_hours: float
    cost: float
    rating: Optional[float] = None


class DayPlan(BaseModel):
    day: int
    date: str
    location: str
    activities: List[PlaceActivity]
    hotel: Optional[str] = None
    meals_cost: float
    transport_cost: float
    activities_cost: float
    day_total: float


class BudgetBreakdown(BaseModel):
    accommodation_total: float
    food_total: float
    transport_total: float
    activities_total: float
    grand_total: float
    currency: str = "USD"


class OptimizedRoute(BaseModel):
    sequence: List[str]
    total_distance_km: float
    estimated_travel_hours: float
    route_details: List[Dict[str, Any]]


class TripItinerary(BaseModel):
    destination: str
    total_days: int
    travel_style: str
    summary: str
    days: List[DayPlan]
    budget: BudgetBreakdown
    optimized_route: Optional[OptimizedRoute] = None
    recommendations: List[str] = []
    tips: List[str] = []


class TripRequest(BaseModel):
    destination: str
    days: int
    budget_range: str  # e.g. "budget", "mid-range", "luxury"
    preferences: Optional[str] = ""
    start_date: Optional[str] = ""


class ChatMessage(BaseModel):
    message: str
    history: Optional[List[Dict[str, str]]] = []


class RouteRequest(BaseModel):
    locations: List[str]
    start_location: Optional[str] = None
