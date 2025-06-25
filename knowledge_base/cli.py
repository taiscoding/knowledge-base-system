#!/usr/bin/env python3
"""
Knowledge Base CLI
Command-line interface for the Knowledge Base system.
"""

import os
import sys
import argparse
import logging
from typing import List, Dict, Any, Optional

from knowledge_base import KnowledgeBaseManager
from knowledge_base.privacy import PrivacyIntegration
from token_intelligence import TokenIntelligenceEngine, TokenIntelligenceRequest

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('kb-cli')


class KnowledgeBaseCLI:
    """Command-line interface for the Knowledge Base system."""
    
    def __init__(self):
        """Initialize the CLI."""
        self.kb = KnowledgeBaseManager()
        self.privacy = PrivacyIntegration(self.kb)
        self.engine = TokenIntelligenceEngine()
    
    def run(self, args: List[str] = None) -> None:
        """
        Parse arguments and execute the appropriate command.
        
        Args:
            args: Command line arguments (or None to use sys.argv)
        """
        parser = self._create_parser()
        parsed_args = parser.parse_args(args)
        
        if not hasattr(parsed_args, 'func'):
            parser.print_help()
            return
        
        parsed_args.func(parsed_args)
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """Create the argument parser."""
        parser = argparse.ArgumentParser(
            description='Knowledge Base CLI - Manage your knowledge with privacy-preserving intelligence.'
        )
        
        subparsers = parser.add_subparsers(
            title='commands',
            description='valid commands',
            help='additional help'
        )
        
        # Add command
        add_parser = subparsers.add_parser(
            'add',
            help='Add content to the knowledge base'
        )
        add_parser.add_argument(
            'content',
            help='Content to add (use quotes or @file.txt to read from file)'
        )
        add_parser.add_argument(
            '--type',
            choices=['note', 'todo', 'calendar', 'project'],
            default=None,
            help='Content type (detected automatically if not specified)'
        )
        add_parser.add_argument(
            '--tags',
            help='Comma-separated tags to add'
        )
        add_parser.add_argument(
            '--privacy',
            action='store_true',
            help='Process through the privacy layer'
        )
        add_parser.set_defaults(func=self.add_content)
        
        # Search command
        search_parser = subparsers.add_parser(
            'search',
            help='Search the knowledge base'
        )
        search_parser.add_argument(
            'query',
            help='Search query'
        )
        search_parser.add_argument(
            '--type',
            choices=['note', 'todo', 'calendar', 'project'],
            default=None,
            help='Content type to search'
        )
        search_parser.set_defaults(func=self.search_content)
        
        # Export command
        export_parser = subparsers.add_parser(
            'export',
            help='Export knowledge base content'
        )
        export_parser.add_argument(
            '--output',
            help='Output file path',
            default=None
        )
        export_parser.add_argument(
            '--privacy',
            action='store_true',
            help='Export through privacy layer'
        )
        export_parser.set_defaults(func=self.export_content)
        
        # Import command
        import_parser = subparsers.add_parser(
            'import',
            help='Import content into the knowledge base'
        )
        import_parser.add_argument(
            'file',
            help='Bundle file to import'
        )
        import_parser.add_argument(
            '--privacy',
            action='store_true',
            help='Import through privacy layer'
        )
        import_parser.set_defaults(func=self.import_content)
        
        # List command
        list_parser = subparsers.add_parser(
            'list',
            help='List content in the knowledge base'
        )
        list_parser.add_argument(
            '--type',
            choices=['note', 'todo', 'calendar', 'project'],
            default=None,
            help='Content type to list'
        )
        list_parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Show items from the last N days'
        )
        list_parser.set_defaults(func=self.list_content)
        
        # Intelligence command
        intel_parser = subparsers.add_parser(
            'intel',
            help='Generate token intelligence'
        )
        intel_parser.add_argument(
            'text',
            help='Tokenized text to analyze'
        )
        intel_parser.add_argument(
            '--context',
            help='Comma-separated context keywords'
        )
        intel_parser.add_argument(
            '--session',
            default='cli-session',
            help='Session ID for token intelligence'
        )
        intel_parser.set_defaults(func=self.generate_intelligence)
        
        return parser
    
    def add_content(self, args: argparse.Namespace) -> None:
        """Add content to the knowledge base."""
        # Check if content is a file reference
        content = args.content
        if content.startswith('@'):
            file_path = content[1:]
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                logger.info(f"Read content from file: {file_path}")
            except Exception as e:
                logger.error(f"Failed to read file {file_path}: {e}")
                return
        
        # Process content
        try:
            if args.privacy:
                logger.info("Privacy processing is enabled, but requires Sankofa integration")
                logger.info("Using mock tokenization for demonstration")
                # In a real implementation, this would use the Sankofa client
                content = content
            
            result = self.kb.process_stream_of_consciousness(content)
            
            # Print summary
            print("\nContent added successfully:")
            print(f"- Todos: {len(result['extracted_info']['todos'])}")
            print(f"- Events: {len(result['extracted_info']['calendar_events'])}")
            print(f"- Notes: {len(result['extracted_info']['notes'])}")
            print(f"- Tags: {', '.join(result['extracted_info']['tags'])}")
            print(f"- Category: {', '.join(result['extracted_info']['categories'])}")
            
        except Exception as e:
            logger.error(f"Failed to add content: {e}")
    
    def search_content(self, args: argparse.Namespace) -> None:
        """Search the knowledge base."""
        try:
            results = self.kb.search_content(args.query, args.type)
            
            if not results:
                print(f"No results found for '{args.query}'")
                return
                
            print(f"\nFound {len(results)} results for '{args.query}':")
            for i, result in enumerate(results):
                print(f"\n[{i+1}] {result['type']} - {result['file']}")
                print(f"    {result['content_preview'][:100]}...")
                
        except Exception as e:
            logger.error(f"Search failed: {e}")
    
    def export_content(self, args: argparse.Namespace) -> None:
        """Export knowledge base content."""
        try:
            if args.privacy:
                result = self.privacy.export_to_privacy_bundle()
                if result.get('success'):
                    print(f"Successfully exported to {result.get('bundle_path')}")
                    print(f"Exported {result.get('items_exported')} items")
                else:
                    print(f"Export failed: {result.get('error')}")
            else:
                # Basic export (simplified)
                output_path = args.output or f"kb_export_{self._get_timestamp()}.json"
                print(f"Basic export functionality to {output_path}")
                print("For privacy-preserving export, use --privacy flag")
                
        except Exception as e:
            logger.error(f"Export failed: {e}")
    
    def import_content(self, args: argparse.Namespace) -> None:
        """Import content into the knowledge base."""
        try:
            if not os.path.exists(args.file):
                print(f"File not found: {args.file}")
                return
                
            if args.privacy:
                result = self.privacy.import_privacy_bundle(args.file)
                if result.get('success'):
                    print(f"Successfully imported {result.get('items_imported')} items")
                    print(f"Created {result.get('files_created')} files")
                else:
                    print(f"Import failed: {result.get('error')}")
            else:
                print(f"Basic import functionality from {args.file}")
                print("For privacy-preserving import, use --privacy flag")
                
        except Exception as e:
            logger.error(f"Import failed: {e}")
    
    def list_content(self, args: argparse.Namespace) -> None:
        """List content in the knowledge base."""
        try:
            # Simplified implementation
            print(f"Listing {args.type or 'all'} content from the last {args.days} days:")
            
            if args.type:
                path = os.path.join("data", args.type)
            else:
                path = "data"
                
            if not os.path.exists(path):
                print(f"No content found in {path}")
                return
                
            # Simple directory listing for demonstration
            print(f"\nContent in {path}:")
            for root, _, files in os.walk(path):
                for file in files:
                    print(f"- {os.path.join(root, file)}")
                
        except Exception as e:
            logger.error(f"List operation failed: {e}")
    
    def generate_intelligence(self, args: argparse.Namespace) -> None:
        """Generate token intelligence."""
        try:
            context = []
            if args.context:
                context = [c.strip() for c in args.context.split(',')]
            
            # Create request
            request = TokenIntelligenceRequest(
                privacy_text=args.text,
                preserved_context=context,
                session_id=args.session
            )
            
            # Generate intelligence
            response = self.engine.generate_intelligence(request)
            
            # Display results
            print("\nToken Intelligence Results:")
            print(f"- Type: {response.intelligence_type}")
            print(f"- Confidence: {response.confidence:.2f}")
            print("- Intelligence:")
            for key, value in response.intelligence.items():
                print(f"  • {key}: {value}")
            print(f"- Processing Time: {response.processing_time_ms}ms")
                
        except Exception as e:
            logger.error(f"Intelligence generation failed: {e}")
    
    def _get_timestamp(self) -> str:
        """Get a timestamp string for filenames."""
        from datetime import datetime
        return datetime.now().strftime("%Y%m%d_%H%M%S")


def main():
    """Main entry point for the CLI."""
    cli = KnowledgeBaseCLI()
    cli.run()


if __name__ == '__main__':
    main() 