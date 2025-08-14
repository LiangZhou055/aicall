import os
from fastapi import FastAPI, Request, Depends, WebSocket
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
from .db import Base, engine, get_db
from . import crud, gpt

app = FastAPI()
Base.metadata.create_all(bind=engine)

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

@app.websocket("/ws/{call_session_id}")
async def websocket_endpoint(websocket: WebSocket, call_session_id: str, db: Session = Depends(get_db)):
    await websocket.accept()
    history = []
    while True:
        data = await websocket.receive_text()
        crud.add_message(db, call_session_id, "user", data)
        history.append({"role": "user", "content": data})

        reply = gpt.ask_gpt(history)
        crud.add_message(db, call_session_id, "assistant", reply)
        history.append({"role": "assistant", "content": reply})

        await websocket.send_text(reply)
