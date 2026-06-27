#TODO: заменить хардкод на БД
from fastapi import FastAPI
from app.routers.v1.payments import router as payment_router
from app.database import Base, engine


app = FastAPI()
app.include_router(payment_router, prefix="/api/v1/payments")
Base.metadata.create_all(bind=engine)





