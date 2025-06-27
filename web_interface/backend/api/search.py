"""
Search API
Endpoints for searching knowledge base content.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, List, Any, Optional

from services.kb_service import KnowledgeBaseService, get_kb_service

router = APIRouter()

@router.get("/content", response_model=Dict[str, Any])
async def search_content(
    query: str = Query(..., description="Search query"),
    content_type: Optional[str] = Query(None, description="Optional content type filter"),
    kb_service: KnowledgeBaseService = Depends(get_kb_service)
):
    """
    Search content in the knowledge base using text matching.
    """
    try:
        results = kb_service.search_content(query, content_type)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/semantic", response_model=Dict[str, Any])
async def search_semantic(
    query: str = Query(..., description="Search query"),
    top_k: int = Query(10, description="Number of results to return"),
    content_types: Optional[List[str]] = Query(None, description="Optional content types filter"),
    categories: Optional[List[str]] = Query(None, description="Optional categories filter"),
    tags: Optional[List[str]] = Query(None, description="Optional tags filter"),
    min_similarity: float = Query(0.0, description="Minimum similarity score (0.0 - 1.0)"),
    kb_service: KnowledgeBaseService = Depends(get_kb_service)
):
    """
    Perform semantic search in the knowledge base.
    """
    try:
        results = kb_service.search_semantic(
            query, top_k, content_types, categories, tags, min_similarity
        )
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Semantic search failed: {str(e)}")

@router.get("/similar/{content_id}", response_model=Dict[str, Any])
async def get_similar_content(
    content_id: str,
    top_k: int = Query(5, description="Number of results to return"),
    min_similarity: float = Query(0.7, description="Minimum similarity score (0.0 - 1.0)"),
    kb_service: KnowledgeBaseService = Depends(get_kb_service)
):
    """
    Find content similar to the specified content item.
    """
    try:
        results = kb_service.similar_content(content_id, top_k, min_similarity)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Similar content search failed: {str(e)}")

@router.get("/suggestions", response_model=Dict[str, Any])
async def get_search_suggestions(
    query: str = Query(..., description="Partial search query"),
    max_suggestions: int = Query(5, description="Maximum number of suggestions"),
    kb_service: KnowledgeBaseService = Depends(get_kb_service)
):
    """
    Get search suggestions based on partial input.
    """
    try:
        # Get suggestions based on content titles, tags, and categories
        # This would typically be implemented in the KnowledgeBaseService
        suggestions = kb_service.get_search_suggestions(query, max_suggestions)
        return {"suggestions": suggestions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting suggestions: {str(e)}")

@router.get("/recommendations/{content_id}", response_model=Dict[str, Any])
async def get_recommendations(
    content_id: str,
    max_items: int = Query(5, description="Maximum number of recommended items"),
    kb_service: KnowledgeBaseService = Depends(get_kb_service)
):
    """
    Get content recommendations based on specified content.
    """
    try:
        recommendations = kb_service.get_recommendations(content_id, max_items)
        return {"recommendations": recommendations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting recommendations: {str(e)}") 