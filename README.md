# Twilio GPT Relay with PostgreSQL

## Deploy to Railway
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/YOUR_TEMPLATE_ID)

### Environment Variables
- `OPENAI_API_KEY` — your OpenAI API key
- `OPENAI_MODEL` — default: `gpt-4o-mini`
- `SYSTEM_PROMPT` — system role for GPT
- `WS_PUBLIC_URL` — your Railway domain without protocol

### Twilio Setup
- In "A Call Comes In", set webhook to:
```
https://<your-railway-domain>/incoming_call
```
