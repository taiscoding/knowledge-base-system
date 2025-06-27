"""
Knowledge Management API
Endpoints for managing knowledge base content.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

from models.content import ContentCreate, ContentResponse, ContentUpdate
from services.kb_service import KnowledgeBaseService, get_kb_service

router = APIRouter()

@router.post("/content", response_model=ContentResponse)
async def create_content(
    content: ContentCreate,
    kb_service: KnowledgeBaseService = Depends(get_kb_service)
):
    """
    Create a new content item in the knowledge base.
    """
    try:
        result = kb_service.create_content(
            content_data=content.content_data,
            content_type=content.content_type,
            parent_id=content.parent_id
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create content: {str(e)}")

@router.get("/content/{content_id}", response_model=ContentResponse)
async def get_content(
    content_id: str = Path(..., description="The ID of the content"),
    include_relationships: bool = Query(False, description="Whether to include relationships"),
    kb_service: KnowledgeBaseService = Depends(get_kb_service)
):
    """
    Get a content item by ID.
    """
    try:
        content = kb_service.get_content(content_id, include_relationships)
        return content
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=f"Content not found: {content_id}")
        raise HTTPException(status_code=500, detail=f"Failed to get content: {str(e)}")

@router.put("/content/{content_id}", response_model=ContentResponse)
async def update_content(
    content_update: ContentUpdate,
    content_id: str = Path(..., description="The ID of the content"),
    kb_service: KnowledgeBaseService = Depends(get_kb_service)
):
    """
    Update a content item.
    """
    try:
        result = kb_service.update_content(content_id, content_update.updates)
        return result
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=f"Content not found: {content_id}")
        raise HTTPException(status_code=500, detail=f"Failed to update content: {str(e)}")

@router.delete("/content/{content_id}", response_model=Dict[str, bool])
async def delete_content(
    content_id: str = Path(..., description="The ID of the content"),
    kb_service: KnowledgeBaseService = Depends(get_kb_service)
):
    """
    Delete a content item.
    """
    try:
        result = kb_service.delete_content(content_id)
        return {"success": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete content: {str(e)}")

@router.post("/folder", response_model=ContentResponse)
async def create_folder(
    title: str = Query(..., description="Folder title"),
    parent_id: Optional[str] = Query(None, description="Optional parent folder ID"),
    description: str = Query("", description="Folder description"),
    icon: str = Query("folder", description="Folder icon"),
    kb_service: KnowledgeBaseService = Depends(get_kb_service)
):
    """
    Create a new folder.
    """
    try:
        result = kb_service.create_folder(title, parent_id, description, icon)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create folder: {str(e)}")

@router.get("/folder/{folder_id}/contents", response_model=List[ContentResponse])
async def list_folder_contents(
    folder_id: str = Path(..., description="The ID of the folder"),
    kb_service: KnowledgeBaseService = Depends(get_kb_service)
):
    """
    List the contents of a folder.
    """
    try:
        contents = kb_service.list_folder_contents(folder_id)
        return contents
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=f"Folder not found: {folder_id}")
        raise HTTPException(status_code=500, detail=f"Failed to list folder contents: {str(e)}")

@router.get("/folder/tree", response_model=Dict[str, Any])
async def get_folder_tree(
    folder_id: Optional[str] = Query(None, description="Root folder ID (None for entire tree)"),
    max_depth: int = Query(-1, description="Maximum depth (-1 for unlimited)"),
    kb_service: KnowledgeBaseService = Depends(get_kb_service)
):
    """
    Get a folder tree.
    """
    try:
        tree = kb_service.get_folder_tree(folder_id, max_depth)
        return tree
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get folder tree: {str(e)}")

@router.post("/content/{content_id}/move", response_model=ContentResponse)
async def move_content(
    content_id: str = Path(..., description="The ID of the content"),
    folder_id: str = Query(..., description="The ID of the destination folder"),
    kb_service: KnowledgeBaseService = Depends(get_kb_service)
):
    """
    Move content to a folder.
    """
    try:
        result = kb_service.move_content_to_folder(content_id, folder_id)
        return result
    except Exception as e:
        if "not found" in str(e).lower():
            raise HTTPException(status_code=404, detail=f"Content or folder not found")
        raise HTTPException(status_code=500, detail=f"Failed to move content: {str(e)}")

@router.post("/process", response_model=Dict[str, Any])
async def process_content(
    content: str = Query(..., description="Text content to process"),
    kb_service: KnowledgeBaseService = Depends(get_kb_service)
):
    """
    Process stream of consciousness input.
    """
    try:
        result = kb_service.process_stream_of_consciousness(content)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@router.post("/bulk", response_model=Dict[str, Any])
async def bulk_operation(
    operation: str = Query(..., description="Bulk operation type (move, tag, delete)"),
    content_ids: List[str] = Query(..., description="Content IDs to operate on"),
    target_id: Optional[str] = Query(None, description="Target ID (e.g., folder ID for move)"),
    metadata: Optional[Dict[str, Any]] = None,
    kb_service: KnowledgeBaseService = Depends(get_kb_service)
):
    """
    Perform bulk operations on content items.
    """
    try:
        results = {}
        
        if operation == "move" and target_id:
            # Move content items to target folder
            for content_id in content_ids:
                try:
                    result = kb_service.move_content_to_folder(content_id, target_id)
                    results[content_id] = {"success": True}
                except Exception as e:
                    results[content_id] = {"success": False, "error": str(e)}
                    
        elif operation == "delete":
            # Delete content items
            for content_id in content_ids:
                try:
                    result = kb_service.delete_content(content_id)
                    results[content_id] = {"success": result}
                except Exception as e:
                    results[content_id] = {"success": False, "error": str(e)}
        
        elif operation == "tag":
            # Add tags to content items
            if not metadata or "tags" not in metadata:
                raise HTTPException(status_code=400, detail="Tags not provided in metadata")
                
            tags = metadata["tags"]
            for content_id in content_ids:
                try:
                    content = kb_service.get_content(content_id)
                    
                    # Merge existing and new tags
                    existing_tags = content.get("tags", [])
                    updated_tags = list(set(existing_tags + tags))
                    
                    # Update content
                    result = kb_service.update_content(content_id, {"tags": updated_tags})
                    results[content_id] = {"success": True}
                except Exception as e:
                    results[content_id] = {"success": False, "error": str(e)}
        
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported bulk operation: {operation}")
            
        return {
            "operation": operation,
            "total": len(content_ids),
            "successful": sum(1 for r in results.values() if r.get("success", False)),
            "failed": sum(1 for r in results.values() if not r.get("success", False)),
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bulk operation failed: {str(e)}") 