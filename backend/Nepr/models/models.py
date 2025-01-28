from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base
import uuid
from sqlalchemy.schema import ForeignKey
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False)
    last_name = Column(String)
    first_name = Column(String)
    password_hash = Column(Text)
    role = Column(String)

class UserHistory(Base):
    __tablename__ = 'user_history'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_email = Column(String, ForeignKey('users.email', ondelete='CASCADE'), nullable=False)
    article_url = Column(Text, nullable=False)
    date_accessed = Column(DateTime, nullable=False, default=datetime.now())
