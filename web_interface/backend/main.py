#!/usr/bin/env python3
"""
Knowledge Base Web Interface - Backend Server
Main entry point for the FastAPI application.
"""

import os
import logging
from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import uvicorn
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import API routes
from api.knowledge import router as knowledge_router
from api.auth import router as auth_router
from api.voice import router as voice_router
from api.dashboard import router as dashboard_router
from api.search import router as search_router
from api.graph import router as graph_router
from api.privacy import router as privacy_router
from api.nlp import router as nlp_router
from api.relationships import router as relationships_router
from api.organization import router as organization_router

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Knowledge Base System",
    description="Web interface for the Knowledge Base System with privacy features",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins in development
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Exception handler
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error", "message": str(exc)},
    )

# Include API routers
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(knowledge_router, prefix="/api/knowledge", tags=["Knowledge Management"])
app.include_router(voice_router, prefix="/api/voice", tags=["Voice Input"])
app.include_router(dashboard_router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(search_router, prefix="/api/search", tags=["Search"])
app.include_router(graph_router, prefix="/api/graph", tags=["Knowledge Graph"])
app.include_router(privacy_router, prefix="/api/privacy", tags=["Privacy"])
app.include_router(nlp_router, prefix="/api/nlp", tags=["Natural Language Processing"])
app.include_router(relationships_router, prefix="/api/relationships", tags=["Relationships"])
app.include_router(organization_router, prefix="/api/organization", tags=["Organization"])

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}

@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Knowledge Base System API"}

# Mount static files for frontend (in production)
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/", StaticFiles(directory=str(static_dir), html=True), name="static")

if __name__ == "__main__":
    # Get port from environment or use default
    port = int(os.environ.get("PORT", 8000))
    
    # Run the server
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=port, 
        reload=True,
        log_level="info",
    ) 