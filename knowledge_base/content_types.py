"""
Content Types for Knowledge Base
Defines the different types of content that can be stored in the knowledge base.
"""

from dataclasses import dataclass, asdict, field
from typing import List, Dict, Any, Optional, Set
from datetime import datetime, timezone
import uuid
from enum import Enum


def generate_id() -> str:
    """Generate a unique ID for content."""
    return str(uuid.uuid4())


def get_timestamp() -> str:
    """Get current timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat()


class RelationshipType(Enum):
    """Types of relationships between content items."""
    PARENT_CHILD = "parent_child"  # Hierarchical relationship
    REFERENCE = "reference"         # One content references another
    DEPENDENCY = "dependency"       # One content depends on another
    CONTINUATION = "continuation"   # One content continues from another
    RELATED = "related"             # General relationship (default)


@dataclass
class Relationship:
    """Represents a relationship between two content items."""
    source_id: str
    target_id: str
    relationship_type: RelationshipType = RelationshipType.RELATED
    description: str = ""
    created: str = field(default_factory=get_timestamp)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = asdict(self)
        # Convert enum to string
        result["relationship_type"] = self.relationship_type.value
        return result


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
    
    # Hierarchical organization
    parent_id: Optional[str] = None  # ID of the parent content item (if any)
    path: Optional[str] = None       # Full path in the hierarchy (e.g., /work/projects/project1)
    
    # Relationship management
    relationships: List[str] = field(default_factory=list)  # List of relationship IDs
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    def add_relationship(self, relationship_id: str) -> None:
        """Add a relationship to this content."""
        if relationship_id not in self.relationships:
            self.relationships.append(relationship_id)
            self.last_modified = get_timestamp()


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


@dataclass
class Folder(BaseContent):
    """
    A folder in the knowledge base hierarchy.
    
    Folders are used to organize content in a hierarchical structure.
    They can contain other folders and content items.
    """
    
    description: str = ""
    icon: str = "folder"  # Used for UI representation
    content_type: str = field(default="folder")
    children: List[str] = field(default_factory=list)  # IDs of child content items
    
    def add_child(self, child_id: str) -> None:
        """Add a child to this folder."""
        if child_id not in self.children:
            self.children.append(child_id)
            self.last_modified = get_timestamp()
    
    def remove_child(self, child_id: str) -> None:
        """Remove a child from this folder."""
        if child_id in self.children:
            self.children.remove(child_id)
            self.last_modified = get_timestamp() 