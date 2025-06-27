"""
Content Models
Pydantic models for content in the knowledge base.
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from datetime import datetime

class ContentCreate(BaseModel):
    """Model for creating content."""
    content_data: Dict[str, Any] = Field(..., description="Content data")
    content_type: str = Field(..., description="Type of content")
    parent_id: Optional[str] = Field(None, description="ID of the parent folder")

class ContentUpdate(BaseModel):
    """Model for updating content."""
    updates: Dict[str, Any] = Field(..., description="Fields to update")

class ContentResponse(BaseModel):
    """Model for content responses."""
    id: str = Field(..., description="Content ID")
    title: str = Field(..., description="Content title")
    created: str = Field(..., description="Creation timestamp")
    last_modified: Optional[str] = Field(None, description="Last modified timestamp")
    
    # Optional fields
    content: Optional[str] = Field(None, description="Content body (for notes)")
    description: Optional[str] = Field(None, description="Content description")
    tags: Optional[List[str]] = Field([], description="Content tags")
    category: Optional[str] = Field(None, description="Content category")
    path: Optional[str] = Field(None, description="Content path in hierarchy")
    parent_id: Optional[str] = Field(None, description="ID of the parent folder")
    
    # Additional fields based on content type
    status: Optional[str] = Field(None, description="Status (for todos)")
    priority: Optional[str] = Field(None, description="Priority (for todos)")
    due_date: Optional[str] = Field(None, description="Due date (for todos)")
    datetime: Optional[str] = Field(None, description="Event datetime (for calendar)")
    duration: Optional[str] = Field(None, description="Event duration (for calendar)")

    # Special fields
    relationships: Optional[List[str]] = Field([], description="Related content IDs")
    _filepath: Optional[str] = Field(None, description="File path")
    _content_type: Optional[str] = Field(None, description="Content type")
    
    class Config:
        """Pydantic model configuration."""
        orm_mode = True  # Allow conversion from ORM objects
        extra = "allow"  # Allow extra fields

class NoteCreate(BaseModel):
    """Model for creating a note."""
    title: str = Field(..., description="Note title")
    content: str = Field(..., description="Note content")
    tags: Optional[List[str]] = Field([], description="Note tags")
    category: Optional[str] = Field("personal", description="Note category")
    parent_id: Optional[str] = Field(None, description="ID of the parent folder")

class TodoCreate(BaseModel):
    """Model for creating a todo."""
    title: str = Field(..., description="Todo title")
    description: Optional[str] = Field("", description="Todo description")
    priority: Optional[str] = Field("medium", description="Todo priority")
    status: Optional[str] = Field("active", description="Todo status")
    due_date: Optional[str] = Field(None, description="Todo due date")
    tags: Optional[List[str]] = Field([], description="Todo tags")
    category: Optional[str] = Field("task", description="Todo category")
    parent_id: Optional[str] = Field(None, description="ID of the parent folder")

class CalendarEventCreate(BaseModel):
    """Model for creating a calendar event."""
    title: str = Field(..., description="Event title")
    description: Optional[str] = Field("", description="Event description")
    datetime: str = Field(..., description="Event datetime")
    duration: Optional[str] = Field("60min", description="Event duration")
    tags: Optional[List[str]] = Field(["calendar"], description="Event tags")
    category: Optional[str] = Field("meeting", description="Event category")
    parent_id: Optional[str] = Field(None, description="ID of the parent folder")

class FolderCreate(BaseModel):
    """Model for creating a folder."""
    title: str = Field(..., description="Folder title")
    description: Optional[str] = Field("", description="Folder description")
    icon: Optional[str] = Field("folder", description="Folder icon")
    parent_id: Optional[str] = Field(None, description="ID of the parent folder")

class RelationshipCreate(BaseModel):
    """Model for creating a relationship."""
    source_id: str = Field(..., description="Source content ID")
    target_id: str = Field(..., description="Target content ID")
    relationship_type: str = Field("related", description="Type of relationship")
    description: Optional[str] = Field("", description="Relationship description")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

class RelationshipResponse(BaseModel):
    """Model for relationship responses."""
    id: str = Field(..., description="Relationship ID")
    source_id: str = Field(..., description="Source content ID")
    target_id: str = Field(..., description="Target content ID")
    relationship_type: str = Field(..., description="Type of relationship")
    description: Optional[str] = Field("", description="Relationship description")
    metadata: Optional[Dict[str, Any]] = Field({}, description="Additional metadata")
    created: str = Field(..., description="Creation timestamp")
    
    class Config:
        """Pydantic model configuration."""
        orm_mode = True
        extra = "allow"

class ContentProcessRequest(BaseModel):
    """Model for processing stream of consciousness."""
    content: str = Field(..., description="Text content to process")
    privacy_level: Optional[str] = Field("balanced", description="Privacy level")
    session_id: Optional[str] = Field(None, description="Privacy session ID") 