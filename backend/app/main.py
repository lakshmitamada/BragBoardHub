from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import routers
from .routers import router as auth_router
from .routers import admin_router
from .routers import router as test_db_router  # optional if you have test routes
from .routers import router  # existing routes

from .database import engine
from .models import Base

app = FastAPI()

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # original default port
        "http://127.0.0.1:5173",  # localhost IP variant
        "http://localhost:5174",  # added because frontend switched to 5174
        "http://localhost:3000",  # existing allowed origin
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["Auth"])   # /auth/login, /auth/me
app.include_router(admin_router, prefix="/admin", tags=["Admin"])
app.include_router(router)              # existing routes
app.include_router(test_db_router)      # optional

# Startup event to create tables
@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
