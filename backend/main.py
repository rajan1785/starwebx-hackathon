from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from auth_routes import router as auth_router
from dashboard_routes import router as dashboard_router
from notifications_routes import router as notifications_router
from health_routes import router as health_router
from stage1_routes import router as stage1_router
from stage2_routes import router as stage2_router

app = FastAPI(title="Coding Ka Big Boss - Hackathon Platform")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============== INCLUDE ROUTERS ==============

app.include_router(auth_router)
app.include_router(dashboard_router)
app.include_router(notifications_router)
app.include_router(health_router)
app.include_router(stage1_router)
app.include_router(stage2_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)