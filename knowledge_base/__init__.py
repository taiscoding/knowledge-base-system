"""
Knowledge Base Manager with Integrated Privacy
A system for intelligent organization and processing of personal knowledge with privacy-preserving features.
"""

__version__ = '1.0.0'

from knowledge_base.manager import KnowledgeBaseManager
from knowledge_base.content_types import Note, Todo, CalendarEvent, Project, Reference
from knowledge_base.privacy import PrivacyEngine, PrivacySessionManager, DeidentificationResult

__all__ = [
    'KnowledgeBaseManager',
    'Note',
    'Todo',
    'CalendarEvent',
    'Project',
    'Reference',
    'PrivacyEngine',
    'PrivacySessionManager',
    'DeidentificationResult'
] 