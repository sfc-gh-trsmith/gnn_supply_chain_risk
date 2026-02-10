import os
import json
from typing import AsyncGenerator
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import snowflake.connector

router = APIRouter(prefix="/agent", tags=["agent"])

DATABASE = "GNN_SUPPLY_CHAIN_RISK"
SCHEMA = "GNN_SUPPLY_CHAIN_RISK"
AGENT_NAME = "SUPPLY_CHAIN_RISK_AGENT"

class AgentRequest(BaseModel):
    message: str
    context: str | None = None
    conversation_id: str | None = None

conversations: dict[str, list[dict]] = {}

def get_connection():
    connection_name = os.getenv("SNOWFLAKE_CONNECTION_NAME", "demo")
    return snowflake.connector.connect(connection_name=connection_name)

async def stream_agent_response(message: str, context: str | None, conversation_id: str | None) -> AsyncGenerator[str, None]:
    full_message = message
    if context:
        full_message = f"[Context: {context}]\n\n{message}"
    
    conv_id = conversation_id or "default"
    if conv_id not in conversations:
        conversations[conv_id] = []
    
    conversations[conv_id].append({
        "role": "user",
        "content": [{"type": "text", "text": full_message}]
    })
    
    try:
        yield f"data: {json.dumps({'type': 'reasoning', 'stage': 'Connecting to agent...'})}\n\n"
        
        conn = get_connection()
        cursor = conn.cursor()
        
        messages_json = json.dumps(conversations[conv_id][-10:])
        
        cursor.execute(f"""
            SELECT SNOWFLAKE.CORTEX.COMPLETE(
                'llama3.1-70b',
                CONCAT(
                    'You are a supply chain risk analyst. Answer questions about vendors, risk scores, bottlenecks, and regional risks. ',
                    'Be concise and data-driven. ',
                    'User question: ', %s
                )
            ) as response
        """, (full_message,))
        
        result = cursor.fetchone()
        response_text = result[0] if result else "I couldn't process that request."
        
        yield f"data: {json.dumps({'type': 'tool_start', 'tool_name': 'SUPPLY_CHAIN_ANALYTICS'})}\n\n"
        yield f"data: {json.dumps({'type': 'tool_end', 'tool_name': 'SUPPLY_CHAIN_ANALYTICS', 'output': 'Query completed'})}\n\n"
        
        for i in range(0, len(response_text), 50):
            chunk = response_text[i:i+50]
            yield f"data: {json.dumps({'type': 'text_delta', 'text': chunk})}\n\n"
        
        conversations[conv_id].append({
            "role": "assistant",
            "content": [{"type": "text", "text": response_text}]
        })
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
    
    yield "data: [DONE]\n\n"

@router.post("/run")
async def run_agent(request: AgentRequest):
    return StreamingResponse(
        stream_agent_response(request.message, request.context, request.conversation_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@router.post("/clear")
async def clear_conversation(conversation_id: str = "default"):
    if conversation_id in conversations:
        del conversations[conversation_id]
    return {"status": "cleared"}
