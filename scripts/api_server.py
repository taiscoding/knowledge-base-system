#!/usr/bin/env python3
"""
Unified Knowledge Base API Server
Exposes both knowledge base and privacy functionality through a REST API.
"""

import os
import json
import uvicorn
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

from knowledge_base import KnowledgeBaseManager

# Initialize the API server
app = FastAPI(
    title="Knowledge Base with Integrated Privacy",
    description="API for managing knowledge with privacy-preserving features",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize global KB manager
kb_manager = None

# ----- Model definitions -----

class ProcessRequest(BaseModel):
    """Request model for processing text."""
    content: str = Field(..., description="Text content to process")
    
class PrivacyProcessRequest(BaseModel):
    """Request model for privacy-aware processing."""
    content: str = Field(..., description="Text content to process with privacy")
    session_id: Optional[str] = Field(None, description="Privacy session ID (created if not provided)")
    privacy_level: str = Field("balanced", description="Privacy level for anonymization")

class SearchRequest(BaseModel):
    """Request model for search."""
    query: str = Field(..., description="Search query")
    content_type: Optional[str] = Field(None, description="Content type to search")

class SessionRequest(BaseModel):
    """Request model for creating a session."""
    privacy_level: str = Field("balanced", description="Privacy level for the session")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Optional session metadata")

class ConversationRequest(BaseModel):
    """Request model for conversation."""
    message: str = Field(..., description="User message")
    session_id: Optional[str] = Field(None, description="Privacy session ID")

# ----- Dependency functions -----

def get_kb_manager():
    """Get or initialize the KB manager."""
    global kb_manager
    if kb_manager is None:
        kb_manager = KnowledgeBaseManager()
    return kb_manager

# ----- API routes -----

@app.get("/")
async def root():
    """Root endpoint providing API info."""
    return {
        "name": "Knowledge Base with Integrated Privacy API",
        "version": "1.0.0",
        "docs_url": "/docs"
    }

@app.post("/process")
async def process_content(request: ProcessRequest, kb=Depends(get_kb_manager)):
    """Process raw text content."""
    try:
        result = kb.process_stream_of_consciousness(request.content)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@app.post("/process-private")
async def process_with_privacy(request: PrivacyProcessRequest, kb=Depends(get_kb_manager)):
    """Process text with privacy preservation."""
    try:
        result = kb.process_with_privacy(
            request.content,
            session_id=request.session_id,
            privacy_level=request.privacy_level
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Privacy processing failed: {str(e)}")

@app.post("/search")
async def search(request: SearchRequest, kb=Depends(get_kb_manager)):
    """Search across knowledge base content."""
    try:
        results = kb.search_content(request.query, request.content_type)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.post("/sessions")
async def create_session(request: SessionRequest, kb=Depends(get_kb_manager)):
    """Create a new privacy session."""
    try:
        session_id = kb.session_manager.create_session(
            request.privacy_level,
            request.metadata
        )
        return {
            "session_id": session_id,
            "privacy_level": request.privacy_level,
            "message": f"Created new privacy session: {session_id}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Session creation failed: {str(e)}")

@app.get("/sessions/{session_id}")
async def get_session(session_id: str, kb=Depends(get_kb_manager)):
    """Get session details."""
    try:
        session = kb.session_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        return session
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get session: {str(e)}")

@app.post("/conversation")
async def conversation(request: ConversationRequest, kb=Depends(get_kb_manager)):
    """Engage in conversation with privacy."""
    try:
        result = kb.process_and_respond(request.message, request.session_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversation processing failed: {str(e)}")

# ----- Server startup -----

@app.on_event("startup")
async def startup():
    """Initialize resources on startup."""
    # Ensure KB manager is initialized
    get_kb_manager()

if __name__ == "__main__":
    # Get port from environment or use default
    port = int(os.environ.get("PORT", 8000))
    
    # Run the server
    uvicorn.run(
        "api_server:app", 
        host="0.0.0.0", 
        port=port, 
        reload=True
    ) 