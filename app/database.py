#file handles the database connection

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import time
import psycopg2
from psycopg2.extras import RealDictCursor
from .config import settings
# Url format--> SQLALCHEMY_DATABASE_URL = 'postgresql://<username>:<password>@<ipaddress>/<hostname>/<database_name >'
#SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:1996@localhost/fastapi'
SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)  #responsible for connecting SqlAlchemy to Postgres database

SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)  # in order to talk to the database we need to create a session

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


"""
while True:
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="fastapi",
            user="postgres",
            password="1996",
            cursor_factory=RealDictCursor,
        )  # cursor_factory parameter is used to obtain the name of the columns while using Postgres from python app hence the .extra imports
        cursor = conn.cursor()  # cursor is used to make changes to database
        print("Database connection established...")
        break  # breaks out of the while loop if succesfully connected otherwise retries
    except Exception as error:
        print("No connection to database available, retrying in 2 secs")
        print(f"Error reported {error}")
        time.sleep(2)
"""