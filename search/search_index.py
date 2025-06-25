#!/usr/bin/env python3
"""
Search Index Manager
Maintains search indexes for fast content retrieval.
"""

import json
import pickle
from pathlib import Path
from typing import Dict, List, Any, Set
from collections import defaultdict
import re

class SearchIndex:
    """Simple search index for the knowledge base."""
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.index_file = self.base_path / "search" / "search_index.pkl"
        self.metadata_file = self.base_path / "search" / "metadata_index.json"
        
        # In-memory indexes
        self.word_index = defaultdict(set)  # word -> set of file paths
        self.tag_index = defaultdict(set)   # tag -> set of file paths
        self.type_index = defaultdict(set)  # type -> set of file paths
        self.metadata = {}  # file_path -> metadata dict
        
        self.load_indexes()
    
    def load_indexes(self):
        """Load existing indexes from disk."""
        try:
            if self.index_file.exists():
                with open(self.index_file, 'rb') as f:
                    data = pickle.load(f)
                    self.word_index = data.get('word_index', defaultdict(set))
                    self.tag_index = data.get('tag_index', defaultdict(set))
                    self.type_index = data.get('type_index', defaultdict(set))
            
            if self.metadata_file.exists():
                with open(self.metadata_file, 'r') as f:
                    self.metadata = json.load(f)
                    
        except Exception as e:
            print(f"Error loading indexes: {e}")
            self._rebuild_indexes()
    
    def save_indexes(self):
        """Save indexes to disk."""
        try:
            # Ensure search directory exists
            self.index_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert sets to lists for JSON serialization
            index_data = {
                'word_index': {k: list(v) for k, v in self.word_index.items()},
                'tag_index': {k: list(v) for k, v in self.tag_index.items()},
                'type_index': {k: list(v) for k, v in self.type_index.items()}
            }
            
            with open(self.index_file, 'wb') as f:
                pickle.dump(index_data, f)
            
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata, f, indent=2)
                
        except Exception as e:
            print(f"Error saving indexes: {e}")
    
    def index_file(self, file_path: Path):
        """Index a single file."""
        try:
            content = self._read_file_content(file_path)
            metadata = self._extract_metadata(content, file_path)
            
            file_key = str(file_path.relative_to(self.base_path))
            
            # Index words
            words = self._extract_words(content)
            for word in words:
                self.word_index[word.lower()].add(file_key)
            
            # Index tags
            tags = metadata.get('tags', [])
            for tag in tags:
                self.tag_index[tag.lower()].add(file_key)
            
            # Index type
            content_type = metadata.get('type', 'unknown')
            self.type_index[content_type].add(file_key)
            
            # Store metadata
            self.metadata[file_key] = metadata
            
        except Exception as e:
            print(f"Error indexing {file_path}: {e}")
    
    def _rebuild_indexes(self):
        """Rebuild all indexes from scratch."""
        print("Rebuilding search indexes...")
        
        # Clear existing indexes
        self.word_index.clear()
        self.tag_index.clear()
        self.type_index.clear()
        self.metadata.clear()
        
        # Index all files
        data_dir = self.base_path / "data"
        if data_dir.exists():
            for file_path in data_dir.rglob("*"):
                if file_path.is_file() and not file_path.name.startswith('.'):
                    self.index_file(file_path)
        
        self.save_indexes()
        print("Index rebuild complete.")
    
    def search(self, query: str, content_type: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Search the indexed content.
        
        Args:
            query: Search query
            content_type: Filter by content type
            limit: Maximum results to return
            
        Returns:
            List of search results
        """
        results = []
        query_words = self._extract_words(query.lower())
        
        # Find files matching query words
        matching_files = set()
        for word in query_words:
            matching_files.update(self.word_index.get(word, set()))
        
        # Filter by content type if specified
        if content_type and content_type in self.type_index:
            type_files = self.type_index[content_type]
            matching_files = matching_files.intersection(type_files)
        
        # Build results
        for file_key in list(matching_files)[:limit]:
            file_path = self.base_path / file_key
            if file_path.exists():
                metadata = self.metadata.get(file_key, {})
                results.append({
                    "file": file_key,
                    "title": metadata.get('title', file_path.name),
                    "type": metadata.get('type', 'unknown'),
                    "tags": metadata.get('tags', []),
                    "created": metadata.get('created', ''),
                    "score": self._calculate_relevance_score(query_words, file_key)
                })
        
        # Sort by relevance score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results
    
    def search_by_tag(self, tag: str) -> List[Dict[str, Any]]:
        """Search for content with specific tag."""
        tag_files = self.tag_index.get(tag.lower(), set())
        results = []
        
        for file_key in tag_files:
            metadata = self.metadata.get(file_key, {})
            results.append({
                "file": file_key,
                "title": metadata.get('title', ''),
                "type": metadata.get('type', 'unknown'),
                "tags": metadata.get('tags', []),
                "created": metadata.get('created', '')
            })
        
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get index statistics."""
        return {
            "total_files": len(self.metadata),
            "total_words": len(self.word_index),
            "total_tags": len(self.tag_index),
            "files_by_type": {k: len(v) for k, v in self.type_index.items()},
            "most_common_tags": self._get_most_common_tags(10)
        }
    
    def _read_file_content(self, file_path: Path) -> str:
        """Read file content."""
        if file_path.suffix == '.json':
            with open(file_path, 'r') as f:
                data = json.load(f)
                return json.dumps(data, indent=2)
        else:
            with open(file_path, 'r') as f:
                return f.read()
    
    def _extract_metadata(self, content: str, file_path: Path) -> Dict[str, Any]:
        """Extract metadata from file content."""
        metadata = {
            "file_path": str(file_path),
            "file_name": file_path.name,
            "file_type": file_path.suffix,
            "title": file_path.stem
        }
        
        try:
            if file_path.suffix == '.json':
                data = json.loads(content)
                metadata.update({
                    "type": data.get("type", "unknown"),
                    "title": data.get("title", file_path.stem),
                    "tags": data.get("tags", []),
                    "created": data.get("created", ""),
                    "priority": data.get("priority", "")
                })
            elif content.startswith('---'):
                # Extract YAML frontmatter
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    try:
                        import yaml
                        frontmatter = yaml.safe_load(parts[1])
                        metadata.update(frontmatter)
                    except:
                        pass
        except:
            pass
        
        return metadata
    
    def _extract_words(self, text: str) -> List[str]:
        """Extract words from text for indexing."""
        # Simple word extraction - can be enhanced
        words = re.findall(r'\b\w+\b', text.lower())
        # Filter out very short words and common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        return [word for word in words if len(word) > 2 and word not in stop_words]
    
    def _calculate_relevance_score(self, query_words: List[str], file_key: str) -> float:
        """Calculate relevance score for a file."""
        metadata = self.metadata.get(file_key, {})
        score = 0.0
        
        # Count word matches in different fields with different weights
        title = metadata.get('title', '').lower()
        tags = [tag.lower() for tag in metadata.get('tags', [])]
        
        for word in query_words:
            if word in title:
                score += 3.0  # Title matches are most important
            if word in tags:
                score += 2.0  # Tag matches are important
            if file_key in self.word_index.get(word, set()):
                score += 1.0  # Content matches
        
        return score
    
    def _get_most_common_tags(self, limit: int) -> List[tuple]:
        """Get most commonly used tags."""
        tag_counts = [(tag, len(files)) for tag, files in self.tag_index.items()]
        tag_counts.sort(key=lambda x: x[1], reverse=True)
        return tag_counts[:limit]


def main():
    """Command line interface for search index."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python search_index.py <command>")
        print("Commands: rebuild, search <query>, stats")
        return
    
    index = SearchIndex()
    command = sys.argv[1]
    
    if command == "rebuild":
        index._rebuild_indexes()
        print("Index rebuilt successfully.")
    
    elif command == "search" and len(sys.argv) > 2:
        query = " ".join(sys.argv[2:])
        results = index.search(query)
        print(f"Found {len(results)} results for '{query}':")
        for result in results[:10]:  # Show top 10
            print(f"  {result['title']} ({result['type']}) - Score: {result['score']:.1f}")
    
    elif command == "stats":
        stats = index.get_statistics()
        print("Search Index Statistics:")
        print(f"  Total files: {stats['total_files']}")
        print(f"  Total words indexed: {stats['total_words']}")
        print(f"  Total tags: {stats['total_tags']}")
        print(f"  Files by type: {stats['files_by_type']}")
        print(f"  Most common tags: {stats['most_common_tags'][:5]}")
    
    else:
        print("Invalid command or missing arguments.")


if __name__ == "__main__":
    main() 