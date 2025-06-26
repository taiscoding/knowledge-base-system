#!/usr/bin/env python3
"""
Knowledge Base CLI
Command-line interface for the Knowledge Base system.
"""

import argparse
import json
import sys
import uuid
from pathlib import Path
from typing import Dict, List, Any, Optional

from knowledge_base import KnowledgeBaseManager, PrivacyEngine

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Knowledge Base with Integrated Privacy CLI"
    )
    
    # Required arguments for all commands
    parser.add_argument(
        "--base-path", "-b",
        default=".",
        help="Base path for knowledge base storage"
    )
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Process command
    process_parser = subparsers.add_parser(
        "process", help="Process a stream of consciousness input"
    )
    process_parser.add_argument(
        "content", help="Text content to process"
    )
    
    # Privacy-aware process command
    privacy_parser = subparsers.add_parser(
        "process-private", help="Process input with privacy preservation"
    )
    privacy_parser.add_argument(
        "content", help="Text content to process privately"
    )
    privacy_parser.add_argument(
        "--session-id", "-s", 
        default=None,
        help="Privacy session ID (created if not provided)"
    )
    privacy_parser.add_argument(
        "--privacy-level", "-p",
        default="balanced",
        choices=["strict", "balanced", "minimal"],
        help="Privacy level for anonymization"
    )
    
    # Interactive command with privacy
    interactive_parser = subparsers.add_parser(
        "chat", help="Interactive chat mode with privacy"
    )
    interactive_parser.add_argument(
        "--privacy-level", "-p",
        default="balanced",
        choices=["strict", "balanced", "minimal"],
        help="Privacy level for anonymization"
    )
    
    # Search command
    search_parser = subparsers.add_parser(
        "search", help="Search across knowledge base content"
    )
    search_parser.add_argument(
        "query", help="Search query"
    )
    search_parser.add_argument(
        "--content-type", "-t",
        help="Limit search to specific content type"
    )
    
    # Create session command
    session_parser = subparsers.add_parser(
        "create-session", help="Create a new privacy session"
    )
    session_parser.add_argument(
        "--privacy-level", "-p",
        default="balanced",
        choices=["strict", "balanced", "minimal"],
        help="Privacy level for the session"
    )
    
    # Process command-line arguments
    args = parser.parse_args()
    
    # Initialize knowledge base manager
    kb = KnowledgeBaseManager(base_path=args.base_path)
    
    # Execute requested command
    if args.command == "process":
        result = kb.process_stream_of_consciousness(args.content)
        print(json.dumps(result, indent=2))
        
    elif args.command == "process-private":
        result = kb.process_with_privacy(
            args.content,
            session_id=args.session_id,
            privacy_level=args.privacy_level
        )
        print(json.dumps(result, indent=2))
        
    elif args.command == "search":
        results = kb.search_content(args.query, content_type=args.content_type)
        print(json.dumps(results, indent=2))
        
    elif args.command == "create-session":
        session_id = kb.session_manager.create_session(args.privacy_level)
        print(json.dumps({
            "session_id": session_id,
            "privacy_level": args.privacy_level,
            "message": f"Created new privacy session: {session_id}"
        }, indent=2))
        
    elif args.command == "chat":
        print("Starting interactive chat mode (type 'exit' to quit)")
        print(f"Privacy level: {args.privacy_level}\n")
        
        # Create initial session
        session_id = kb.session_manager.create_session(args.privacy_level)
        print(f"Created session: {session_id}")
        
        while True:
            try:
                user_input = input("\nYou: ")
                if user_input.lower() in ["exit", "quit"]:
                    print("Goodbye!")
                    break
                    
                result = kb.process_and_respond(user_input, session_id)
                print(f"\nKB: {result['response']['message']}")
                
                # Show suggestions if any
                suggestions = result['response']['suggestions']
                if suggestions:
                    print("\nSuggestions:")
                    for suggestion in suggestions:
                        print(f"- {suggestion['text']}")
                        
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
                
            except Exception as e:
                print(f"Error: {e}")
        
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 