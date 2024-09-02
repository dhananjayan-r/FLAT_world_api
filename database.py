# database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()
# # Database connection parameters
# hostname = '34.121.45.231'
# port = '5432'
# username = 'test_user'
# password = 'test_pass'
# database = 'test'

# # Update with your actual PostgreSQL credentials
# DATABASE_URL = "postgresql://username:password@localhost:5432/yourdatabase"
# DATABASE_URL = f"postgresql://{username}:{password}@{hostname}:{port}/{database}"

DATABASE_URL = os.getenv("DATABASE_URL")
#DATABASE_URL="postgresql://test_user:test_pass@34.121.45.231:5432/test"

# Create the engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
