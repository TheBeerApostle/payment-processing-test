import sqlalchemy
from sqlalchemy.orm import sessionmaker, declarative_base
DATABASE_URL = "sqlite:///./transactions"
engine = sqlalchemy.create_engine(DATABASE_URL, connect_args={"check_same_thread":False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
