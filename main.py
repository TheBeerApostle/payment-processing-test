#TODO: заменить хардкод на БД
from fastapi import FastAPI
from app.routers.v1.payments import router as payment_router


app = FastAPI()
app.include_router(payment_router, prefix="/api/v1/payments")





