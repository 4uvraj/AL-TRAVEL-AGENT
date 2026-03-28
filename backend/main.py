from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as api_router

app = FastAPI(title="AI Travel Copilot API", version="1.0.0")

# Configure CORS to allow the frontend to access the API remotely
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, this allows requests from your randomized Vercel domain
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to AI Travel Copilot API"}
