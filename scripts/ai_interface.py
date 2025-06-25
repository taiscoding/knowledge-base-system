#!/usr/bin/env python3
"""
AI Interface for Knowledge Base
Simple interface for automated tools to interact with the knowledge base.
"""

import sys
import json
from pathlib import Path
from kb_manager import KnowledgeBaseManager

class KnowledgeBaseAI:
    """AI-friendly interface for the knowledge base."""
    
    def __init__(self):
        self.kb = KnowledgeBaseManager()
    
    def process_input(self, user_input: str) -> dict:
        """
        Main entry point for processing user input.
        
        Args:
            user_input: Raw text from user
            
        Returns:
            Dictionary with processing results and saved files
        """
        try:
            # Process the stream of consciousness input
            result = self.kb.process_stream_of_consciousness(user_input)
            
            saved_files = []
            
            # Save extracted todos
            for todo in result["extracted_info"]["todos"]:
                filepath = self.kb.save_content(todo, "todo")
                saved_files.append(filepath)
            
            # Save extracted calendar events
            for event in result["extracted_info"]["calendar_events"]:
                filepath = self.kb.save_content(event, "calendar")
                saved_files.append(filepath)
            
            # Save extracted notes
            for note in result["extracted_info"]["notes"]:
                note_content = self._format_note_content(note)
                filepath = self.kb.save_content(note_content, "note")
                saved_files.append(filepath)
            
            # Create summary
            summary = {
                "success": True,
                "items_created": {
                    "todos": len(result["extracted_info"]["todos"]),
                    "calendar_events": len(result["extracted_info"]["calendar_events"]),
                    "notes": len(result["extracted_info"]["notes"])
                },
                "tags_extracted": result["extracted_info"]["tags"],
                "categories": result["extracted_info"]["categories"],
                "files_saved": saved_files,
                "message": self._generate_summary_message(result)
            }
            
            return summary
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Error processing input: {e}"
            }
    
    def search(self, query: str, content_type: str = None) -> dict:
        """
        Search the knowledge base.
        
        Args:
            query: Search query
            content_type: Optional filter by content type
            
        Returns:
            Search results
        """
        try:
            results = self.kb.search_content(query, content_type)
            
            return {
                "success": True,
                "query": query,
                "results_count": len(results),
                "results": results,
                "message": f"Found {len(results)} matching items"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Search error: {e}"
            }
    
    def add_journal_entry(self, content: str, mood: str = "neutral", energy: str = "medium") -> dict:
        """
        Add a journal entry.
        
        Args:
            content: Journal content
            mood: Current mood
            energy: Energy level
            
        Returns:
            Result of journal entry creation
        """
        try:
            journal_data = {
                "id": self.kb.generate_id(),
                "created": self.kb.get_timestamp(),
                "type": "journal",
                "content": content,
                "mood": mood,
                "energy": energy,
                "tags": self.kb._extract_tags(content),
                "category": "personal"
            }
            
            journal_content = self._format_journal_content(journal_data)
            filepath = self.kb.save_content(journal_content, "journal")
            
            return {
                "success": True,
                "file_saved": filepath,
                "message": "Journal entry saved successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Error saving journal entry: {e}"
            }
    
    def add_todo(self, title: str, description: str = "", priority: str = "medium", 
                 due_date: str = None, context: str = "@personal") -> dict:
        """
        Add a todo item.
        
        Args:
            title: Todo title
            description: Optional description
            priority: Priority level (high/medium/low)
            due_date: Optional due date
            context: Context tag
            
        Returns:
            Result of todo creation
        """
        try:
            todo_data = {
                "id": self.kb.generate_id(),
                "created": self.kb.get_timestamp(),
                "updated": self.kb.get_timestamp(),
                "type": "todo",
                "title": title,
                "description": description,
                "priority": priority,
                "status": "active",
                "category": "task",
                "tags": self.kb._extract_tags(title + " " + description),
                "due_date": due_date,
                "context": context,
                "completed_date": None
            }
            
            filepath = self.kb.save_content(todo_data, "todo")
            
            return {
                "success": True,
                "file_saved": filepath,
                "todo_id": todo_data["id"],
                "message": f"Todo '{title}' created successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Error creating todo: {e}"
            }
    
    def get_status(self) -> dict:
        """Get current status of the knowledge base."""
        try:
            data_dir = Path("data")
            status = {
                "success": True,
                "total_items": 0,
                "by_type": {}
            }
            
            if data_dir.exists():
                for content_dir in data_dir.iterdir():
                    if content_dir.is_dir():
                        count = len(list(content_dir.glob("*")))
                        status["by_type"][content_dir.name] = count
                        status["total_items"] += count
            
            status["message"] = f"Knowledge base contains {status['total_items']} items"
            return status
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Error getting status: {e}"
            }
    
    def _format_note_content(self, note_data: dict) -> str:
        """Format note data as markdown."""
        metadata = f"""---
id: {note_data['id']}
created: {note_data['created']}
type: note
title: "{note_data['title']}"
category: {note_data['category']}
tags: {note_data['tags']}
priority: {note_data['priority']}
---

# {note_data['title']}

{note_data['content']}
"""
        return metadata
    
    def _format_journal_content(self, journal_data: dict) -> str:
        """Format journal data as markdown."""
        date_str = journal_data['created'][:10]  # Extract date part
        metadata = f"""---
id: {journal_data['id']}
created: {journal_data['created']}
type: journal
date: {date_str}
mood: {journal_data['mood']}
energy: {journal_data['energy']}
tags: {journal_data['tags']}
category: personal
---

# {date_str} - Journal Entry

{journal_data['content']}
"""
        return metadata
    
    def _generate_summary_message(self, result: dict) -> str:
        """Generate a human-readable summary message."""
        info = result["extracted_info"]
        parts = []
        
        if info["todos"]:
            parts.append(f"{len(info['todos'])} todo(s)")
        if info["calendar_events"]:
            parts.append(f"{len(info['calendar_events'])} calendar event(s)")
        if info["notes"]:
            parts.append(f"{len(info['notes'])} note(s)")
        
        if parts:
            items_text = ", ".join(parts)
            return f"Successfully processed and saved: {items_text}. Tags: {', '.join(info['tags']) if info['tags'] else 'none'}"
        else:
            return "Content processed but no specific items extracted"


def main():
    """Command-line interface for testing."""
    if len(sys.argv) < 2:
        print("Usage: python ai_interface.py '<command>' [args...]")
        print("Commands: process, search, status, journal, todo")
        return
    
    ai = KnowledgeBaseAI()
    command = sys.argv[1]
    
    if command == "process":
        if len(sys.argv) < 3:
            print("Usage: python ai_interface.py process '<text>'")
            return
        result = ai.process_input(sys.argv[2])
        print(json.dumps(result, indent=2))
    
    elif command == "search":
        if len(sys.argv) < 3:
            print("Usage: python ai_interface.py search '<query>' [type]")
            return
        content_type = sys.argv[3] if len(sys.argv) > 3 else None
        result = ai.search(sys.argv[2], content_type)
        print(json.dumps(result, indent=2))
    
    elif command == "status":
        result = ai.get_status()
        print(json.dumps(result, indent=2))
    
    elif command == "journal":
        if len(sys.argv) < 3:
            print("Usage: python ai_interface.py journal '<content>' [mood] [energy]")
            return
        mood = sys.argv[3] if len(sys.argv) > 3 else "neutral"
        energy = sys.argv[4] if len(sys.argv) > 4 else "medium"
        result = ai.add_journal_entry(sys.argv[2], mood, energy)
        print(json.dumps(result, indent=2))
    
    elif command == "todo":
        if len(sys.argv) < 3:
            print("Usage: python ai_interface.py todo '<title>' [description] [priority]")
            return
        description = sys.argv[3] if len(sys.argv) > 3 else ""
        priority = sys.argv[4] if len(sys.argv) > 4 else "medium"
        result = ai.add_todo(sys.argv[2], description, priority)
        print(json.dumps(result, indent=2))
    
    else:
        print(f"Unknown command: {command}")


if __name__ == "__main__":
    main() 