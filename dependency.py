from app.database import SessionLocal
from typing import Generator
from sqlalchemy.orm import Session


def db_connection() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()