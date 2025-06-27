"""
Dashboard API
Endpoints for dashboard statistics and recent activity.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime, timedelta

from services.kb_service import KnowledgeBaseService, get_kb_service

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/stats", response_model=Dict[str, Any])
async def get_dashboard_stats(
    kb_service: KnowledgeBaseService = Depends(get_kb_service)
):
    """
    Get dashboard statistics.
    """
    try:
        # This would typically query the database for all these statistics
        # For now, we'll count files in various directories
        
        # Get content counts by type
        notes_count = 0
        todos_count = 0
        events_count = 0
        active_todos = 0
        completed_todos = 0
        upcoming_events = 0
        
        # Get privacy score (in a real app, this would be calculated based on various factors)
        privacy_score = 85  # Default/demo value
        
        # Attempt to count notes
        notes = await _get_content_by_type(kb_service, "note")
        notes_count = len(notes)
        
        # Attempt to count todos and their statuses
        todos = await _get_content_by_type(kb_service, "todo")
        todos_count = len(todos)
        
        # Count active vs completed todos
        for todo in todos:
            if todo.get("status") == "active":
                active_todos += 1
            elif todo.get("status") == "completed":
                completed_todos += 1
                
        # Attempt to count calendar events
        events = await _get_content_by_type(kb_service, "calendar")
        events_count = len(events)
        
        # Count upcoming events (next 7 days)
        now = datetime.now()
        week_from_now = now + timedelta(days=7)
        
        for event in events:
            event_date = event.get("datetime")
            if event_date:
                try:
                    event_datetime = datetime.fromisoformat(event_date.replace('Z', '+00:00'))
                    if now <= event_datetime <= week_from_now:
                        upcoming_events += 1
                except (ValueError, TypeError):
                    pass
        
        # Return all stats
        return {
            "totalNotes": notes_count,
            "totalTodos": todos_count,
            "totalEvents": events_count,
            "activeTodos": active_todos,
            "completedTodos": completed_todos,
            "upcomingEvents": upcoming_events,
            "privacyScore": privacy_score
        }
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard stats: {str(e)}")

@router.get("/recent-content", response_model=List[Dict[str, Any]])
async def get_recent_content(
    limit: int = Query(5, description="Number of items to return"),
    kb_service: KnowledgeBaseService = Depends(get_kb_service)
):
    """
    Get recent content from the knowledge base.
    """
    try:
        # Get recent content from each type
        notes = await _get_content_by_type(kb_service, "note")
        todos = await _get_content_by_type(kb_service, "todo")
        events = await _get_content_by_type(kb_service, "calendar")
        
        # Combine all content
        all_content = []
        all_content.extend([{**item, "type": "note"} for item in notes])
        all_content.extend([{**item, "type": "todo"} for item in todos])
        all_content.extend([{**item, "type": "calendar"} for item in events])
        
        # Sort by creation date (newest first)
        sorted_content = sorted(
            all_content, 
            key=lambda x: x.get("created", ""), 
            reverse=True
        )
        
        # Return limited results
        return sorted_content[:limit]
    except Exception as e:
        logger.error(f"Error getting recent content: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get recent content: {str(e)}")

@router.get("/activity", response_model=List[Dict[str, Any]])
async def get_recent_activity(
    limit: int = Query(10, description="Number of items to return"),
    kb_service: KnowledgeBaseService = Depends(get_kb_service)
):
    """
    Get recent activity from the knowledge base.
    """
    try:
        # In a real implementation, this would query an activity log
        # For now, we'll return some dummy data
        
        # Get privacy audit logs if available
        activities = []
        
        try:
            if hasattr(kb_service.manager, 'audit_logger') and kb_service.manager.audit_logger:
                # Try to get actual audit logs
                logs = kb_service.manager.get_audit_logs()
                
                for log in logs:
                    activity = {
                        "id": log.get("log_id", ""),
                        "action": log.get("operation", ""),
                        "content": log.get("details", {}).get("action", "Content operation"),
                        "timestamp": log.get("timestamp", "")
                    }
                    activities.append(activity)
        except Exception as e:
            logger.warning(f"Could not get audit logs: {e}")
        
        # If we couldn't get real logs or there aren't enough, add some mock data
        if len(activities) < limit:
            # Mock data
            mock_activities = [
                {
                    "id": "1",
                    "action": "created",
                    "content": "Project Meeting Notes",
                    "timestamp": "2025-06-26T13:35:13Z"
                },
                {
                    "id": "2",
                    "action": "updated",
                    "content": "Complete milestone 4",
                    "timestamp": "2025-06-24T09:12:45Z"
                },
                {
                    "id": "3", 
                    "action": "deleted",
                    "content": "Old draft",
                    "timestamp": "2025-06-23T16:22:33Z"
                },
                {
                    "id": "4",
                    "action": "viewed",
                    "content": "Team Sync-up",
                    "timestamp": "2025-06-23T14:38:16Z"
                },
                {
                    "id": "5",
                    "action": "created",
                    "content": "Knowledge Base Design",
                    "timestamp": "2025-06-22T10:05:22Z"
                }
            ]
            
            # Add mock activities if needed
            activities.extend(mock_activities[:limit - len(activities)])
        
        # Sort by timestamp (newest first)
        sorted_activities = sorted(
            activities, 
            key=lambda x: x.get("timestamp", ""), 
            reverse=True
        )
        
        # Return limited results
        return sorted_activities[:limit]
    except Exception as e:
        logger.error(f"Error getting recent activity: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get recent activity: {str(e)}")

async def _get_content_by_type(kb_service: KnowledgeBaseService, content_type: str) -> List[Dict[str, Any]]:
    """Helper function to get content by type with error handling."""
    try:
        # In a production system, we'd use proper database queries
        # For now, we search through files
        results = kb_service.search_content("", content_type)
        
        content_items = []
        for result in results:
            # Extract ID from filepath
            file_path = result.get("file", "")
            file_name = file_path.split("/")[-1] if "/" in file_path else file_path
            
            # Extract ID from filename (assumes format: type-date-id.json or type-id.json)
            parts = file_name.split("-")
            content_id = parts[-1].replace(".json", "") if len(parts) > 1 else ""
            
            if content_id:
                try:
                    content = kb_service.get_content(content_id)
                    content_items.append(content)
                except Exception as e:
                    logger.warning(f"Could not retrieve content {content_id}: {e}")
                    
        return content_items
    except Exception as e:
        logger.warning(f"Error getting {content_type} content: {e}")
        return [] 