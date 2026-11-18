# agents/specialist_node.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from groq import Groq

app = FastAPI(
    title="Groq Specialist Agent (A2A Node)",
    description="Autonomous A2A specialist agent powered by Groq LPU inference.",
    version="1.0.0"
)

# Initialize Groq client using environment variables
groq_api_key = os.environ.get("GROQ_API_KEY")
groq_client = Groq(api_key=groq_api_key) if groq_api_key else None

class A2ATaskRequest(BaseModel):
    task_id: str
    message: str
    context: dict = {}

@app.get("/.well-known/agent.json")
def get_agent_card():
    """
    A2A Standard Agent Discovery Card. 
    Exposes metadata, capabilities, and endpoints for peer agent discovery.
    """
    return {
        "id": "groq-analytics-specialist",
        "name": "High-Speed Groq Analytics Specialist",
        "version": "1.0.0",
        "capabilities": [
            "rapid-reasoning", 
            "data-synthesis", 
            "code-generation", 
            "context-evaluation"
        ],
        "endpoints": {
            "tasks": "/api/tasks"
        }
    }

@app.post("/api/tasks")
def handle_a2a_task(task: A2ATaskRequest):
    """
    Standard A2A Task Receiver Endpoint.
    Receives task payloads, processes them through Groq LPU inference, and returns structured results.
    """
    if not groq_client:
        raise HTTPException(
            status_code=500, 
            detail="GROQ_API_KEY is not configured in the specialist node environment."
        )
    
    try:
        # Execute ultra-low-latency inference via Groq
        completion = groq_client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {
                    "role": "system", 
                    "content": (
                        "You are an expert enterprise AI agent operating inside a secure Agent-to-Agent (A2A) network. "
                        "Synthesize incoming tasks and incorporate any provided MCP tool telemetry or contextual payloads."
                    )
                },
                {
                    "role": "user", 
                    "content": f"Delegated Task: {task.message}\n\nContext & Tool Telemetry: {task.context}"
                }
            ],
            temperature=0.3,
            max_tokens=1536
        )
        
        ai_response = completion.choices[0].message.content
        
        return {
            "task_id": task.task_id,
            "status": "completed",
            "agent_node": "groq-analytics-specialist",
            "result": ai_response,
            "artifacts": {
                "inference_engine": "Groq LPU",
                "model_used": "llama-3.3-70b-versatile",
                "tokens_used": completion.usage.total_tokens if completion.usage else 0
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Groq LPU Inference Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("specialist_node:app", host="127.0.0.1", port=8001, reload=True)
