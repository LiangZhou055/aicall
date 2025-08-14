import os
import asyncio
from fastapi import FastAPI, Request, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
from .db import Base, engine, get_db
from . import crud, gpt

app = FastAPI()

# ----------------------------
# Retry database connection & create tables
# ----------------------------
async def init_db(retries=5, delay=3):
    for i in range(retries):
        try:
            Base.metadata.create_all(bind=engine)
            print("Database tables created successfully.")
            return
        except OperationalError as e:
            print(f"Database not ready, retrying in {delay}s... ({i+1}/{retries})")
            await asyncio.sleep(delay)
    raise Exception("Could not connect to the database after multiple retries.")

@app.on_event("startup")
async def startup_event():
    await init_db()

# ----------------------------
# Incoming Twilio Call
# ----------------------------
@app.post("/incoming_call", response_class=PlainTextResponse)
async def incoming_call(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    caller_number = form.get("From", "Unknown")
    call_session = crud.create_call_session(db, caller_number)

    twiml = f"""
<Response>
    <Connect>
        <Stream url="wss://{os.getenv('WS_PUBLIC_URL')}/ws/{call_session.id}" />
    </Connect>
</Response>
""".strip()
    return PlainTextResponse(twiml)

# ----------------------------
# WebSocket for real-time conversation
# ----------------------------
@app.websocket("/ws/{call_session_id}")
async def websocket_endpoint(websocket: WebSocket, call_session_id: str, db: Session = Depends(get_db)):
    await websocket.accept()
    history = []
    try:
        while True:
            data = await websocket.receive_text()
            crud.add_message(db, call_session_id, "user", data)
            history.append({"role": "user", "content": data})

            reply = gpt.ask_gpt(history)
            crud.add_message(db, call_session_id, "assistant", reply)
            history.append({"role": "assistant", "content": reply})

            await websocket.send_text(reply)
    except WebSocketDisconnect:
        print(f"WebSocket disconnected: {call_session_id}")
