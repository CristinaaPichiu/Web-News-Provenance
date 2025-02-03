# db_postgresql_conn.py
import logging

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
        logging.error(f"Error connecting to database: {e}", file=sys.stderr)
        sys.exit(1)

def close(session,engine):
    try:
        if session.is_active:
            session.commit()
        session.close()
        engine.dispose()
        logging.info("Session successfully closed.")
    except Exception as e:
        logging.error(f"Error while closing the session: {str(e)}")
        session.rollback()  # Rollback if any error occurred
        logging.error("Session rollback completed due to error.")


