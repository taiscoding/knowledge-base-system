"""
Natural Language Processing API
Endpoints for querying the knowledge base using natural language.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, List, Any, Optional
import logging

from services.kb_service import KnowledgeBaseService, get_kb_service
from services.nlp_service import NLPService, get_nlp_service

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/query", response_model=Dict[str, Any])
async def natural_language_query(
    query: str = Query(..., description="Natural language query"),
    kb_service: KnowledgeBaseService = Depends(get_kb_service),
    nlp_service: NLPService = Depends(get_nlp_service)
):
    """
    Process a natural language query and return relevant results.
    """
    try:
        # Analyze query to extract intent and entities
        analysis = nlp_service.analyze_query(query)
        
        # Generate a response based on the query analysis
        response = nlp_service.generate_response(query, analysis)
        
        return {
            "query": query,
            "analysis": analysis,
            "response": response
        }
    except Exception as e:
        logger.error(f"Error processing natural language query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")

@router.get("/extract-entities", response_model=Dict[str, Any])
async def extract_entities(
    text: str = Query(..., description="Text to extract entities from"),
    types: List[str] = Query(["person", "organization", "date", "location"], 
                           description="Types of entities to extract"),
    nlp_service: NLPService = Depends(get_nlp_service)
):
    """
    Extract named entities from text.
    """
    try:
        entities = nlp_service.extract_entities(text, types)
        return {"entities": entities}
    except Exception as e:
        logger.error(f"Error extracting entities: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Entity extraction failed: {str(e)}")

@router.get("/summarize", response_model=Dict[str, Any])
async def summarize_content(
    content_id: str = Query(..., description="ID of content to summarize"),
    max_length: int = Query(200, description="Maximum summary length in characters"),
    kb_service: KnowledgeBaseService = Depends(get_kb_service),
    nlp_service: NLPService = Depends(get_nlp_service)
):
    """
    Generate a summary of specified content.
    """
    try:
        # Get content
        content = kb_service.get_content(content_id)
        
        # Extract text based on content type
        content_type = content.get("_content_type", "")
        
        if content_type == "note":
            text = content.get("content", "")
        elif content_type == "todo":
            text = f"{content.get('title', '')}. {content.get('description', '')}"
        elif content_type == "calendar":
            text = f"{content.get('title', '')}. {content.get('description', '')}"
        else:
            text = str(content)
        
        # Generate summary
        summary = nlp_service.summarize_text(text, max_length)
        
        return {
            "content_id": content_id,
            "content_type": content_type,
            "summary": summary
        }
    except Exception as e:
        logger.error(f"Error summarizing content: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")

@router.post("/conversation", response_model=Dict[str, Any])
async def process_conversation_message(
    message: str = Query(..., description="User message"),
    session_id: Optional[str] = Query(None, description="Conversation session ID"),
    kb_service: KnowledgeBaseService = Depends(get_kb_service),
    nlp_service: NLPService = Depends(get_nlp_service)
):
    """
    Process a conversation message and generate a response.
    """
    try:
        # Process message using KnowledgeBaseManager's conversation feature
        result = kb_service.process_and_respond(message, session_id)
        
        # Extract session_id from result for future reference
        if result.get("privacy") and result["privacy"].get("session_id"):
            session_id = result["privacy"]["session_id"]
        
        return {
            "message": message,
            "response": result.get("response", {}).get("message", ""),
            "suggestions": result.get("response", {}).get("suggestions", []),
            "session_id": session_id,
            "processed_items": result.get("extracted_info", {})
        }
    except Exception as e:
        logger.error(f"Error processing conversation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Conversation processing failed: {str(e)}")

@router.post("/analyze-sentiment", response_model=Dict[str, Any])
async def analyze_sentiment(
    text: str = Query(..., description="Text to analyze for sentiment"),
    nlp_service: NLPService = Depends(get_nlp_service)
):
    """
    Analyze the sentiment of the provided text.
    """
    try:
        sentiment = nlp_service.analyze_sentiment(text)
        return sentiment
    except Exception as e:
        logger.error(f"Error analyzing sentiment: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Sentiment analysis failed: {str(e)}")

@router.post("/tag-content", response_model=Dict[str, Any])
async def tag_content(
    content_id: str = Query(..., description="ID of content to tag"),
    kb_service: KnowledgeBaseService = Depends(get_kb_service),
    nlp_service: NLPService = Depends(get_nlp_service)
):
    """
    Automatically generate tags for content.
    """
    try:
        # Get content
        content = kb_service.get_content(content_id)
        
        # Extract text based on content type
        content_type = content.get("_content_type", "")
        text = ""
        
        if content_type == "note":
            text = content.get("content", "")
        elif content_type == "todo":
            text = f"{content.get('title', '')}. {content.get('description', '')}"
        elif content_type == "calendar":
            text = f"{content.get('title', '')}. {content.get('description', '')}"
        
        # Generate tags
        tags = nlp_service.generate_tags(text)
        
        # Update content with new tags
        existing_tags = content.get("tags", [])
        combined_tags = list(set(existing_tags + tags))
        
        # Update content
        updated_content = kb_service.update_content(
            content_id, {"tags": combined_tags}
        )
        
        return {
            "content_id": content_id,
            "content_type": content_type,
            "previous_tags": existing_tags,
            "new_tags": tags,
            "combined_tags": combined_tags
        }
    except Exception as e:
        logger.error(f"Error tagging content: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Content tagging failed: {str(e)}") 