from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from pydantic import BaseModel
from app.agent.graph import agent_app
from langchain_core.messages import HumanMessage

load_dotenv()

app = FastAPI(title="Agentic Task Assistant API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AgentRequest(BaseModel):
    message: str
    # user_id: str  # Future use for auth

class AgentResponse(BaseModel):
    response: str

@app.get("/")
async def root():
    return {"message": "Agentic Task Assistant API is running"}

@app.post("/api/agent", response_model=AgentResponse)
async def chat_agent(request: AgentRequest):
    try:
        # Run the agent
        inputs = {"messages": [HumanMessage(content=request.message)]}
        result = await agent_app.ainvoke(inputs)
        
        # Get the final message content
        last_message = result["messages"][-1]
        return AgentResponse(response=last_message.content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

