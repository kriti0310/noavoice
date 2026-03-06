from fastapi import FastAPI
from app.config.database import init_db
from app.api.v1.router import router
from contextlib import asynccontextmanager
from app.config.logging import logger
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from app.config.settings import settings
from dotenv import load_dotenv

load_dotenv()

@asynccontextmanager
async def lifespan(app:FastAPI):
    try:
        logger.info(" Starting application...")

        logger.info("Initializing database...")
        await init_db()

        logger.info(" Application startup complete!")

        yield   

        logger.info(" Shutting down application...")

    except Exception as e:
        logger.error(f" Startup failed: {e}")
        raise
    
app = FastAPI(
    title="Agent API",
    lifespan=lifespan)

@app.get("/")
async def root():
    return {"status": "ok"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    same_site="lax",
    https_only=False,  # True in production with HTTPS
)
app.include_router(router)

@app.get("/")
async def root():
    return {"status": "API is running "}
