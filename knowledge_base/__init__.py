"""
Knowledge Base Manager
A system for intelligent organization and processing of personal knowledge.
"""

__version__ = '1.0.0'

from knowledge_base.manager import KnowledgeBaseManager
from knowledge_base.content_types import Note, Todo, CalendarEvent, Project, Reference

__all__ = [
    'KnowledgeBaseManager',
    'Note',
    'Todo',
    'CalendarEvent',
    'Project',
    'Reference'
] 