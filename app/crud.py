from sqlalchemy.orm import Session
from . import models

def create_call_session(db: Session, caller_number: str):
    session = models.CallSession(caller_number=caller_number)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

def add_message(db: Session, call_session_id, sender, text):
    message = models.Message(
        call_session_id=call_session_id,
        sender=sender,
        text=text
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message
