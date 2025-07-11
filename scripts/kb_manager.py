#!/usr/bin/env python3
"""
Knowledge Base Manager
Main script for intelligent content processing and organization.
"""

import os
import json
import yaml
import uuid
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import hashlib

class KnowledgeBaseManager:
    """Main class for managing the knowledge base system."""
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.config = self._load_config()
        self.conventions = self._load_conventions()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load AI instructions and configuration."""
        config_path = self.base_path / "config" / "ai_instructions.yaml"
        if config_path.exists():
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        return {}
    
    def _load_conventions(self) -> Dict[str, Any]:
        """Load naming conventions and standards."""
        conv_path = self.base_path / "config" / "conventions.yaml"
        if conv_path.exists():
            with open(conv_path, 'r') as f:
                return yaml.safe_load(f)
        return {}
    
    def generate_id(self) -> str:
        """Generate a unique ID for content."""
        return str(uuid.uuid4())
    
    def get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        return datetime.now(timezone.utc).isoformat()
    
    def process_stream_of_consciousness(self, content: str) -> Dict[str, Any]:
        """
        Process stream of consciousness input and organize intelligently.
        
        Args:
            content: Raw text input from user
            
        Returns:
            Dictionary containing organized content and metadata
        """
        result = {
            "original_content": content,
            "processed_items": [],
            "extracted_info": {
                "todos": [],
                "calendar_events": [],
                "notes": [],
                "tags": [],
                "categories": [],
                "cross_refs": []
            }
        }
        
        # Extract actionable items (todos)
        todos = self._extract_todos(content)
        result["extracted_info"]["todos"] = todos
        
        # Extract dates and events
        events = self._extract_calendar_events(content)
        result["extracted_info"]["calendar_events"] = events
        
        # Extract key topics and generate tags
        tags = self._extract_tags(content)
        result["extracted_info"]["tags"] = tags
        
        # Categorize content
        category = self._categorize_content(content, tags)
        result["extracted_info"]["categories"] = [category]
        
        # Create main note if content doesn't fit other categories
        if not todos and not events:
            note = self._create_note_from_content(content, tags, category)
            result["extracted_info"]["notes"] = [note]
        
        return result
    
    def _extract_todos(self, content: str) -> List[Dict[str, Any]]:
        """Extract actionable items from content."""
        todos = []
        
        # Keywords that indicate actionable items
        action_patterns = [
            r"(?:need to|must|should|have to|remember to|todo:?)\s+(.+?)(?:\.|$|\n)",
            r"(?:^|\n)-\s*(?:(?:\[ \])|(?:\[\s\]))\s*(.+?)(?:\n|$)",
            r"(?:action|task|do):?\s*(.+?)(?:\.|$|\n)"
        ]
        
        for pattern in action_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0] if match[0] else (match[1] if len(match) > 1 else "")
                
                todo = {
                    "id": self.generate_id(),
                    "created": self.get_timestamp(),
                    "type": "todo",
                    "title": match.strip(),
                    "description": "",
                    "priority": self._detect_priority(match),
                    "status": "active",
                    "category": "task",
                    "tags": self._extract_tags(match),
                    "due_date": self._extract_due_date(match),
                    "context": self._extract_context(match)
                }
                todos.append(todo)
        
        return todos
    
    def _extract_calendar_events(self, content: str) -> List[Dict[str, Any]]:
        """Extract calendar events from content."""
        events = []
        
        # Date/time patterns
        date_patterns = [
            r"(?:meeting|call|appointment|event)\s+(?:on|at)?\s*([^\.]+?)(?:\.|$|\n)",
            r"([A-Za-z]+\s+\d{1,2}(?:st|nd|rd|th)?\s*(?:at\s+\d{1,2}:\d{2})?)",
            r"((?:today|tomorrow|next week|this week)\s+(?:at\s+)?\d{1,2}:\d{2})"
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                event = {
                    "id": self.generate_id(),
                    "created": self.get_timestamp(),
                    "type": "calendar",
                    "title": match.strip(),
                    "description": "",
                    "datetime": self._parse_datetime(match),
                    "duration": "60min",
                    "category": "meeting",
                    "tags": ["calendar"]
                }
                events.append(event)
        
        return events
    
    def _extract_tags(self, content: str) -> List[str]:
        """Extract and generate relevant tags from content."""
        tags = []
        
        # Explicit hashtags
        hashtag_pattern = r"#(\w+)"
        hashtags = re.findall(hashtag_pattern, content)
        tags.extend(hashtags)
        
        # Context tags
        if any(word in content.lower() for word in ["work", "office", "meeting", "project"]):
            tags.append("@work")
        if any(word in content.lower() for word in ["home", "personal", "family"]):
            tags.append("@personal")
        
        # Topic-based tags
        topic_keywords = {
            "learning": ["learn", "study", "research", "read", "book", "article"],
            "health": ["exercise", "workout", "doctor", "health", "fitness"],
            "finance": ["money", "budget", "expense", "income", "investment"],
            "creative": ["write", "art", "music", "design", "creative", "idea"]
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in content.lower() for keyword in keywords):
                tags.append(f"#{topic}")
        
        return list(set(tags))  # Remove duplicates
    
    def _categorize_content(self, content: str, tags: List[str]) -> str:
        """Categorize content based on patterns and tags."""
        categories = self.config.get("organization", {}).get("auto_categorization", {})
        
        content_lower = content.lower()
        
        for category, keywords in categories.items():
            if any(keyword in content_lower for keyword in keywords):
                return category
        
        # Default categorization
        if "@work" in tags:
            return "work"
        elif any(tag.startswith("#") for tag in tags):
            return "learning"
        else:
            return "personal"
    
    def _detect_priority(self, text: str) -> str:
        """Detect priority level from text."""
        urgent_keywords = self.config.get("organization", {}).get("priority_detection", {}).get("urgent_keywords", [])
        
        text_lower = text.lower()
        if any(keyword in text_lower for keyword in urgent_keywords):
            return "high"
        elif any(word in text_lower for word in ["today", "asap"]):
            return "high"
        elif any(word in text_lower for word in ["important", "priority"]):
            return "medium"
        else:
            return "low"
    
    def _extract_due_date(self, text: str) -> Optional[str]:
        """Extract due date from text."""
        # Simple date extraction - can be enhanced
        today_keywords = ["today", "asap"]
        tomorrow_keywords = ["tomorrow"]
        
        text_lower = text.lower()
        if any(keyword in text_lower for keyword in today_keywords):
            return datetime.now(timezone.utc).date().isoformat()
        elif any(keyword in text_lower for keyword in tomorrow_keywords):
            tomorrow = datetime.now(timezone.utc).date().replace(day=datetime.now().day + 1)
            return tomorrow.isoformat()
        
        return None
    
    def _extract_context(self, text: str) -> str:
        """Extract context tags from text."""
        if any(word in text.lower() for word in ["home", "house"]):
            return "@home"
        elif any(word in text.lower() for word in ["work", "office"]):
            return "@work"
        elif any(word in text.lower() for word in ["urgent", "important"]):
            return "@urgent"
        else:
            return "@personal"
    
    def _parse_datetime(self, text: str) -> str:
        """Parse datetime from text (simplified)."""
        # This is a simplified version - real implementation would be more robust
        return self.get_timestamp()
    
    def _create_note_from_content(self, content: str, tags: List[str], category: str) -> Dict[str, Any]:
        """Create a note entry from general content."""
        return {
            "id": self.generate_id(),
            "created": self.get_timestamp(),
            "type": "note",
            "title": self._generate_title_from_content(content),
            "content": content,
            "category": category,
            "tags": tags,
            "priority": "low"
        }
    
    def _generate_title_from_content(self, content: str) -> str:
        """Generate a descriptive title from content."""
        # Take first meaningful sentence or up to 50 characters
        sentences = content.split('.')
        first_sentence = sentences[0].strip()
        
        if len(first_sentence) <= 50:
            return first_sentence
        else:
            return first_sentence[:47] + "..."
    
    def save_content(self, content_data: Dict[str, Any], content_type: str) -> str:
        """Save content to appropriate file with proper naming."""
        timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
        
        if content_type == "journal":
            date_str = datetime.now().strftime("%Y-%m-%d")
            filename = f"{date_str}.md"
            filepath = self.base_path / "data" / "journal" / filename
        elif content_type == "todo":
            filename = f"todo-{timestamp}.json"
            filepath = self.base_path / "data" / "todos" / filename
        elif content_type == "calendar":
            filename = f"event-{timestamp}.json"
            filepath = self.base_path / "data" / "calendar" / filename
        elif content_type == "note":
            filename = f"note-{timestamp}.md"
            filepath = self.base_path / "data" / "notes" / filename
        else:
            filename = f"{content_type}-{timestamp}.json"
            filepath = self.base_path / "data" / "notes" / filename
        
        # Ensure directory exists
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Save content
        if filepath.suffix == '.json':
            with open(filepath, 'w') as f:
                json.dump(content_data, f, indent=2)
        else:
            with open(filepath, 'w') as f:
                f.write(content_data)
        
        return str(filepath)
    
    def search_content(self, query: str, content_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search across all content in the knowledge base."""
        results = []
        
        data_dir = self.base_path / "data"
        
        search_dirs = []
        if content_type:
            search_dirs = [data_dir / content_type]
        else:
            search_dirs = [d for d in data_dir.iterdir() if d.is_dir()]
        
        for search_dir in search_dirs:
            if search_dir.exists():
                for file_path in search_dir.rglob("*"):
                    if file_path.is_file():
                        try:
                            content = self._read_file_content(file_path)
                            if query.lower() in content.lower():
                                results.append({
                                    "file": str(file_path),
                                    "type": search_dir.name,
                                    "content_preview": content[:200] + "..."
                                })
                        except Exception as e:
                            print(f"Error reading {file_path}: {e}")
        
        return results
    
    def _read_file_content(self, file_path: Path) -> str:
        """Read content from file, handling both JSON and text files."""
        if file_path.suffix == '.json':
            with open(file_path, 'r') as f:
                data = json.load(f)
                return json.dumps(data, indent=2)
        else:
            with open(file_path, 'r') as f:
                return f.read()


def main():
    """Main entry point for the knowledge base manager."""
    kb = KnowledgeBaseManager()
    
    # Example usage
    print("Knowledge Base Manager initialized.")
    print("Use this class in your AI tools for intelligent content processing.")


if __name__ == "__main__":
    main() 