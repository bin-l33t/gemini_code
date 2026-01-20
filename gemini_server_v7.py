import os

from typing import Optional

from pydantic import BaseModel

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# from deprecated_generative_ai import genai
# genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# model = genai.GenerativeModel('gemini-pro')


class Message(BaseModel):
    role: str
    content: str


class ChatSessionRequest(BaseModel):
    messages: list[Message]
    persona: Optional[str] = None


app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/chat")
async def chat_endpoint(request: ChatSessionRequest):
    # persona = request.persona or "default"
    # prompt = f"You are a helpful assistant. "
    # for message in request.messages:
    #     prompt += f"{message.role}: {message.content}\n"
    # prompt += "assistant: "
    # print(f"prompt: {prompt}")
    # response = model.generate_content(prompt)
    # return {"response": response.text}
    return {"response": "The new Gemini API is not yet supported. Stay tuned!"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
