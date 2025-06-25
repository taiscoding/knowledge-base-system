"""
Content Types for Knowledge Base
Defines the different types of content that can be stored in the knowledge base.
"""

from dataclasses import dataclass, asdict, field
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import uuid


def generate_id() -> str:
    """Generate a unique ID for content."""
    return str(uuid.uuid4())


def get_timestamp() -> str:
    """Get current timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat()


@dataclass
class BaseContent:
    """Base class for all content types."""
    
    title: str
    category: str = "general"
    tags: List[str] = field(default_factory=list)
    priority: str = "medium"
    
    # Auto-generated fields
    id: str = field(default_factory=generate_id)
    created: str = field(default_factory=get_timestamp)
    last_modified: str = field(default_factory=get_timestamp)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class Note(BaseContent):
    """
    A note in the knowledge base.
    
    Notes are the most basic content type and can contain any text.
    """
    
    content: str = ""
    content_type: str = field(default="note")
    references: List[str] = field(default_factory=list)
    

@dataclass
class Todo(BaseContent):
    """
    A todo item in the knowledge base.
    
    Todos represent actionable items with status, due date, etc.
    """
    
    description: str = ""
    status: str = "active"  # active, completed, cancelled, delegated
    due_date: Optional[str] = None
    completed_date: Optional[str] = None
    context: str = "@personal"
    content_type: str = field(default="todo")
    
    def mark_completed(self) -> None:
        """Mark the todo as completed."""
        self.status = "completed"
        self.completed_date = get_timestamp()


@dataclass
class CalendarEvent(BaseContent):
    """
    A calendar event in the knowledge base.
    
    Events represent time-based activities.
    """
    
    description: str = ""
    datetime: str = field(default_factory=get_timestamp)
    duration: str = "60min"
    location: Optional[str] = None
    attendees: List[str] = field(default_factory=list)
    content_type: str = field(default="calendar")


@dataclass
class Project(BaseContent):
    """
    A project in the knowledge base.
    
    Projects group together related content items.
    """
    
    description: str = ""
    status: str = "active"  # active, completed, paused, cancelled
    start_date: str = field(default_factory=get_timestamp)
    end_date: Optional[str] = None
    related_items: List[str] = field(default_factory=list)
    content_type: str = field(default="project")
    team: List[str] = field(default_factory=list)
    goals: List[str] = field(default_factory=list)
    progress: int = 0  # 0-100


@dataclass
class Reference(BaseContent):
    """
    A reference to external content.
    
    References can be links, files, citations, etc.
    """
    
    reference_type: str = "link"  # link, file, citation, etc.
    url: Optional[str] = None
    file_path: Optional[str] = None
    citation: Optional[str] = None
    content_type: str = field(default="reference")
    description: str = ""
    notes: str = "" 