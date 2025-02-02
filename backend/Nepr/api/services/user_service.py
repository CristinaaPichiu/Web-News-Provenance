import logging
from datetime import datetime
from databases.db_postgresql_conn import connect
from models.models import UserHistory
from sqlalchemy.orm import Session

class UserService:
    def add_user_history(self,session: Session, email: str, url: str):
        """
        Adds an entry to the user's history.
        """
        date = datetime.now()
        user_history = UserHistory(user_email=email, article_url=url, date_accessed=date)
        try:
            session.add(user_history)
            session.commit()
            return True
        except Exception as e:
            logging.error(e)
            return None

    def get_user_history(self, session: Session, email: str):
        """
        Returns a list of article URLs from the user's history.
        """
        try:
            user_history = session.query(UserHistory).filter_by(user_email=email).all()
            return [history.article_url for history in user_history] if user_history else None
        except Exception as e:
            logging.error(e)
            return None

    def get_user_top_history(self, session: Session, email: str, limit: int = 10):
        """
        Returns the top article URLs from the user's history.
        """
        try:
            user_history = session.query(UserHistory).filter_by(user_email=email).order_by(
                UserHistory.date_accessed.desc()).limit(limit).all()
            return [history.article_url for history in user_history] if user_history else None
        except Exception as e:
            logging.error(e)
            return None
