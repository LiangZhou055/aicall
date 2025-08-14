import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .db import Base

class CallSession(Base):
    __tablename__ = "call_sessions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    caller_number = Column(String, nullable=False)
    start_time = Column(DateTime, default=datetime.utcnow)
    messages = relationship("Message", back_populates="call_session")

class Message(Base):
    __tablename__ = "messages"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    call_session_id = Column(UUID(as_uuid=True), ForeignKey("call_sessions.id"))
    sender = Column(String, nullable=False)  # 'user' or 'assistant'
    text = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    call_session = relationship("CallSession", back_populates="messages")
