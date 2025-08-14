import os
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import PlainTextResponse
from . import gpt

app = FastAPI()

# ----------------------------
# Welcome Page
# ----------------------------
@app.get("/welcome", response_class=PlainTextResponse)
async def welcome():
    return "Welcome! This is the Twilio GPT Relay service."

# ----------------------------
# Incoming Twilio Call
# ----------------------------
@app.post("/incoming_call", response_class=PlainTextResponse)
async def incoming_call(request: Request):
    form = await request.form()
    caller_number = form.get("From", "Unknown")
    call_session_id = caller_number.replace("+", "")

    twiml = f"""
<Response>
    <Connect>
        <Stream url="wss://{os.getenv('WS_PUBLIC_URL')}/ws/{call_session_id}" />
    </Connect>
</Response>
""".strip()
    return PlainTextResponse(twiml)

# ----------------------------
# WebSocket for real-time conversation
# ----------------------------
@app.websocket("/ws/{call_session_id}")
async def websocket_endpoint(websocket: WebSocket, call_session_id: str):
    await websocket.accept()
    history = []
    try:
        while True:
            data = await websocket.receive_text()
            history.append({"role": "user", "content": data})

            reply = gpt.ask_gpt(history)
            history.append({"role": "assistant", "content": reply})

            await websocket.send_text(reply)
    except WebSocketDisconnect:
        print(f"WebSocket disconnected: {call_session_id}")

