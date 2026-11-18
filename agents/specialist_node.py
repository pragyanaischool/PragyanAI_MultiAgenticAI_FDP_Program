# agents/specialist_node.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
from groq import Groq

app = FastAPI(title="Groq Specialist Agent (A2A Node)")

groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))

class A2ATask(BaseModel):
    task_id: str
    message: str
    context: dict = {}

@app.get("/.well-known/agent.json")
def get_agent_card():
    """A2A Standard Agent Discovery Card."""
    return {
        "id": "groq-analytics-specialist",
        "name": "High-Speed Groq Analytics Specialist",
        "version": "1.0.0",
        "capabilities": ["rapid-reasoning", "data-synthesis"],
        "endpoints": {"tasks": "/api/tasks"}
    }

@app.post("/api/tasks")
def handle_a2a_task(task: A2ATask):
    """Processes delegated tasks using Groq's LPU inference."""
    try:
        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a specialized enterprise AI agent operating inside an A2A multi-agent network."},
                {"role": "user", "content": f"Task: {task.message}\nContext: {task.context}"}
            ],
            temperature=0.3,
            max_tokens=1024
        )
        return {
            "task_id": task.task_id,
            "status": "completed",
            "agent_node": "groq-analytics-specialist",
            "result": completion.choices[0].message.content,
            "artifacts": {
                "inference_engine": "Groq LPU",
                "tokens_used": completion.usage.total_tokens if completion.usage else 0
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Groq Inference Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
