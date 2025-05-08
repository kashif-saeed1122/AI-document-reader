#!/usr/bin/env python3
"""MCP Server for Document Q&A with Gemini"""

import json
import sys
import os
from typing import Dict, Any
import httpx
import asyncio
from mcp import Server, ErrorCode, McpError

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

server = Server("document-qa-gemini")

@server.list_resources()
async def list_resources():
    """List available resources (document sessions)"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{API_BASE_URL}/api/sessions")
            sessions = response.json()
            return [{"uri": f"session://{s['session_id']}", "name": s['metadata']['filename']} 
                   for s in sessions]
        except:
            return []

@server.list_tools()
async def list_tools():
    """List available tools"""
    return [{
        "name": "ask_document_question",
        "description": "Ask a question about an uploaded document",
        "inputSchema": {
            "type": "object",
            "properties": {
                "session_id": {"type": "string", "description": "Document session ID"},
                "question": {"type": "string", "description": "Question to ask"}
            },
            "required": ["session_id", "question"]
        }
    }]

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> Any:
    """Handle tool calls"""
    if name == "ask_document_question":
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_BASE_URL}/api/ask",
                json=arguments
            )
            return response.json()
    
    raise McpError(ErrorCode.METHOD_NOT_FOUND, f"Unknown tool: {name}")

async def main():
    """Run the MCP server"""
    async with server:
        # Read from stdin, write to stdout
        async for message in server.input_stream:
            await server.handle_message(message)

if __name__ == "__main__":
    asyncio.run(main())