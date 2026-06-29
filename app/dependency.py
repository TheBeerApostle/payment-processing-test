from fastapi import Header, HTTPException
from typing import Generator
from app.database import AsyncSessionLocal
from sqlalchemy.ext.asyncio import AsyncSession

# API Key authentication
async def verify_api_key(x_api_key: str = Header(...)):
    # В production нужно брать из конфига или БД
    VALID_API_KEY = "test-api-key-12345"
    if x_api_key != VALID_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key

# Устаревший синхронный метод заменяем на асинхронный
# Теперь используем get_db из database.py