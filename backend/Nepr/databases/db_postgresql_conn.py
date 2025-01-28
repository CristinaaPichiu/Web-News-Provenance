# db_postgresql_conn.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

import os
import sys

load_dotenv()

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
