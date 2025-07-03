from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from agent import chat_with_agent

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
@app.get("/")
def read_root():
    return {"message": "Backend is running ✅"}
    
@app.post("/chat")
async def chat(request: Request):
    body = await request.json()
    prompt = body.get("prompt")
    slots = body.get("slots", {})
    timezone = slots.get("timezone", "UTC")

    if not prompt:
        return {"response": "No prompt provided"}
    
    response, updated_slots = chat_with_agent(prompt, user_timezone=timezone, previous_slots=slots)
    return {"response": response, "updated_slots": updated_slots}

