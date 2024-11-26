from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, Date, Float, Text
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from sqlalchemy.dialects.postgresql import UUID
from dotenv import load_dotenv
import uuid
import sys
import os

load_dotenv()
Base = declarative_base()

def connect():
    connection_string = os.getenv("DATABASE_URI_POSTGRESQL")
    try:
        engine = create_engine(connection_string)
        Session = sessionmaker(bind=engine)
        session = Session()
        return session, engine
    except Exception as e:
        print(f"Error connecting to database: {e}", file=sys.stderr)
        sys.exit(1)

class User(Base):
    __tablename__ = 'users'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False)
    last_name = Column(String)
    first_name = Column(String)
    password_hash = Column(Text)
    role = Column(String)

if __name__ == '__main__':
    session, engine = None, None
    try:
        session, engine = connect()
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
    finally:
        if session:
            session.close()
