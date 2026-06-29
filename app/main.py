from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.routers.v1 import payments
from app.database import engine
from app.models import Base
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup - создаем таблицы
    logger.info("Starting up...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created successfully")

    yield

    # Shutdown
    logger.info("Shutting down...")
    await engine.dispose()
    logger.info("Cleanup completed")


app = FastAPI(
    title="Payment Service",
    description="Payment processing service with outbox pattern",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(payments.router, prefix="/api/v1/payments", tags=["payments"])


@app.get("/")
async def root():
    return {"message": "Payment Service API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "payment-api"}

