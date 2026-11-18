# frontend/app.py
import streamlit as st
import os
import requests
from groq import Groq

# Page Configuration
st.set_page_config(
    page_title="Groq Agentic Mesh & MCP Control Center",
    page_icon="⚡",
    layout="wide"
)

st.title("Pragyan AI - Groq Agentic Mesh with MCP & A2A")
st.markdown("Ultra-low-latency AI agent architecture powered by Groq LPUs, Model Context Protocol (MCP) tool servers, and Streamlit.")

# --- 1. Secure API Key & Configuration Retrieval from st.secrets ---
groq_api_key = None
try:
    groq_api_key = st.secrets.get("GROQ_API_KEY")
except Exception:
    pass

# Fallback to standard environment variable if running locally outside Streamlit secrets context
if not groq_api_key:
    groq_api_key = os.environ.get("GROQ_API_KEY")

if not groq_api_key:
    st.error("⚠️ `GROQ_API_KEY` is missing! Please configure it in your `.streamlit/secrets.toml` file or Streamlit Cloud Secrets dashboard.")
    st.stop()

# Initialize Groq Client
groq_client = Groq(api_key=groq_api_key)

# --- 2. MCP Tool Client Execution Layer ---
def execute_mcp_tool(tool_name: str, arguments: dict, server_url: str = None) -> dict:
    """
    Executes an MCP tool call. If a remote MCP server URL is provided, it makes an HTTP request;
    otherwise, it executes the embedded secure tool handler for cloud deployments.
    """
    if server_url:
        try:
            response = requests.post(f"{server_url}/mcp/call", json={
                "tool_name": tool_name,
                "arguments": arguments
            }, timeout=5.0)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            return {"error": f"Failed to reach remote MCP server: {str(e)}"}

    # Embedded Fallback for Single-Container Streamlit Cloud Deployments
    if tool_name == "query_enterprise_db":
        return {
            "status": "success",
            "source": "MCP Enterprise DB Server (Embedded)",
            "query_executed": arguments.get("query", ""),
            "rows_returned": 142,
            "sample_metrics": {
                "active_cluster_load": "14.2%",
                "average_inference_latency": "18ms",
                "daily_active_nodes": 1280,
                "system_health": "Optimal"
            }
        }
    elif tool_name == "read_secure_config":
        return {
            "status": "success",
            "source": "MCP Secure Config Vault (Embedded)",
            "environment": "production",
            "max_tokens": 4096,
            "active_model": "llama-3.3-70b-versatile"
        }
    
    return {"error": f"MCP Tool '{tool_name}' not found."}

# --- 3. Sidebar Configuration ---
st.sidebar.header("Mesh Parameters")
selected_model = st.sidebar.selectbox(
    "Groq Model",
    ["llama-3.3-70b-versatile", "openai/gpt-oss-120b", "mixtral-8x7b-32768"]
)
temperature = st.sidebar.slider("Inference Temperature", 0.0, 1.0, 0.3)
use_mcp = st.sidebar.checkbox("Enable MCP Tool Context", value=True)
mcp_server_url = st.sidebar.text_input("Remote MCP Server URL (Optional)", value="")

# --- 4. Main User Interface (A2UI Layer) ---
user_query = st.text_area(
    "Enter task or query for the agent mesh:",
    value="Analyze our current cluster load metrics and suggest an optimized scaling strategy."
)

col_action1, col_action2 = st.columns([1, 4])

with col_action1:
    run_workflow = st.button(" Run Workflow", type="primary", use_container_width=True)

if run_workflow:
    if not user_query.strip():
        st.warning("Please enter a valid query or task.")
    else:
        with st.spinner("Executing workflow across Groq LPU inference & MCP servers..."):
            context_payload = {}
            
            # Step A: Fetch context via Model Context Protocol (MCP)
            if use_mcp:
                mcp_result = execute_mcp_tool(
                    tool_name="query_enterprise_db", 
                    arguments={"query": user_query},
                    server_url=mcp_server_url.strip() if mcp_server_url.strip() else None
                )
                context_payload["mcp_data"] = mcp_result

            # Step B: Execute Groq LPU Inference
            try:
                system_prompt = (
                    "You are an expert enterprise AI agent operating within a multi-agent mesh architecture. "
                    "Incorporate the provided Model Context Protocol (MCP) tool telemetry and metrics into your structured analysis."
                )
                
                completion = groq_client.chat.completions.create(
                    model=selected_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Task: {user_query}\n\nMCP Tool Telemetry Context: {context_payload}"}
                    ],
                    temperature=temperature,
                    max_tokens=2048
                )
                
                ai_response = completion.choices[0].message.content
                
                st.success("Workflow completed successfully!")
                
                # Render Results Side-by-Side (A2UI Presentation)
                res_col1, res_col2 = st.columns(2)
                
                with res_col1:
                    st.subheader("🤖 Agent Synthesis")
                    st.markdown(ai_response)
                
                with res_col2:
                    st.subheader("🔍 Execution Metadata & MCP Telemetry")
                    st.json({
                        "model_used": selected_model,
                        "temperature": temperature,
                        "tokens_used": completion.usage.total_tokens if completion.usage else "N/A",
                        "mcp_context_injected": context_payload
                    })
                    
            except Exception as e:
                st.error(f"Groq LPU Inference Error: {str(e)}")
