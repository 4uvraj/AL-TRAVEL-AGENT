from fastapi import APIRouter, HTTPException
from app.models.schemas import TripRequest, ChatMessage, RouteRequest
from app.agents.travel_graph import run_travel_planner
from app.services.route_optimizer import optimize_route
from app.services.chat_service import run_chat

router = APIRouter()


from fastapi.responses import StreamingResponse

@router.post("/plan-trip")
def plan_trip(request: TripRequest):
    """
    Invoke the full LangGraph multi-agent pipeline and stream progress.
    """
    try:
        from app.agents.travel_graph import stream_travel_planner
        generator = stream_travel_planner(
            destination=request.destination,
            days=request.days,
            budget_range=request.budget_range,
            preferences=request.preferences or "",
            start_date=request.start_date or "",
        )
        return StreamingResponse(generator, media_type="text/event-stream")
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
