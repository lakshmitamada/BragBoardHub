from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Correct imports of routers
from .routers import router as auth_router
from .routers import admin_router
from .test_db_router import router as test_db_router

from .database import engine
from .models import Base

app = FastAPI()

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)       # /auth routes
app.include_router(admin_router)      # /admin routes
app.include_router(test_db_router)    # /test-db routes

# Startup event to create tables
@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
