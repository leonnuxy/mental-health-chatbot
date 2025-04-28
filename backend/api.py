from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (for development only)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

class ChatRequest(BaseModel):
    prompt: str
    conversation_history: list

def get_ai_response(prompt, conversation_history):
    input_text = "\n".join(conversation_history + [f"User: {prompt}"])
    try:
        result = subprocess.run(
            ['ollama', 'run', 'mistral'],
            input=input_text,
            text=True,
            capture_output=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr}")
        return "Sorry, I couldn't generate a response."
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return "Sorry, an unexpected error occurred."

@app.post("/chat/")
async def chat(request: ChatRequest):
    try:
        ai_response = get_ai_response(request.prompt, request.conversation_history)
        return {"response": ai_response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))