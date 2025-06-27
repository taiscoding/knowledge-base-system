"""
Natural Language Processing Service
Service for natural language processing capabilities.
"""

import logging
import os
import re
from typing import Dict, List, Any, Optional, Union
from functools import lru_cache
import json

logger = logging.getLogger(__name__)

class NLPService:
    """Service for natural language processing operations."""
    
    def __init__(self):
        """Initialize the NLP service."""
        logger.info("Initializing NLPService")
        
        # Load any necessary resources or models
        # In a production system, this would initialize NLP libraries
        self._initialize_nlp_resources()
        
        logger.info("NLPService initialized successfully")
    
    def _initialize_nlp_resources(self):
        """Initialize NLP resources and models."""
        # In a real implementation, this would initialize libraries like spaCy or transformers
        # For now, we'll use simple regex-based approaches
        self.initialized = True
    
    def analyze_query(self, query: str) -> Dict[str, Any]:
        """
        Analyze a natural language query to determine intent and entities.
        
        Args:
            query: Natural language query
            
        Returns:
            Analysis results with intent and entities
        """
        # This is a simplified implementation using regex patterns
        # A real implementation would use a proper NLP library
        
        # Detect intent
        intent = "unknown"
        intent_confidence = 0.0
        
        # Pattern matching for basic intents
        search_patterns = [
            r"(?:find|search for|look for|get|show me|where is|locate)\s+(.+)",
            r"(?:what|which)\s+(.+?)(?:\s+is|\s+are|\s+is in|\s+are in)\s+(.+)"
        ]
        
        create_patterns = [
            r"(?:create|add|make|new)\s+(?:a |an )?(\w+)\s+(?:called|named|titled)?\s*(.+)",
            r"(?:create|add|make|new)\s+(?:a |an )?(\w+)"
        ]
        
        list_patterns = [
            r"(?:list|show|display|get)\s+(?:all|my)?\s*(\w+)s?",
            r"(?:what|which)\s+(\w+)s?\s+(?:do I have|are there|exist)"
        ]
        
        # Check for search intent
        for pattern in search_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                intent = "search"
                intent_confidence = 0.8
                break
        
        # Check for create intent
        if intent == "unknown":
            for pattern in create_patterns:
                match = re.search(pattern, query, re.IGNORECASE)
                if match:
                    intent = "create"
                    intent_confidence = 0.75
                    break
        
        # Check for list intent
        if intent == "unknown":
            for pattern in list_patterns:
                match = re.search(pattern, query, re.IGNORECASE)
                if match:
                    intent = "list"
                    intent_confidence = 0.7
                    break
        
        # Extract entities
        entities = self.extract_entities(query)
        
        # Determine content type
        content_type = self._detect_content_type(query, entities)
        
        return {
            "intent": intent,
            "intent_confidence": intent_confidence,
            "entities": entities,
            "content_type": content_type,
            "query": query
        }
    
    def extract_entities(self, text: str, types: List[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Extract named entities from text.
        
        Args:
            text: Text to extract entities from
            types: Types of entities to extract (None for all)
            
        Returns:
            Dictionary of entity types and values
        """
        # This is a simplified implementation
        # A real implementation would use a proper NLP library
        
        entities = {
            "person": [],
            "organization": [],
            "date": [],
            "location": [],
            "content_type": [],
            "tag": []
        }
        
        # Simple regex patterns for each entity type
        person_pattern = r"(?:with|from|by|for)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2})"
        date_pattern = r"(?:on|at|by|before|after)\s+([A-Za-z]+\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4}|yesterday|tomorrow|today|next week)"
        location_pattern = r"(?:in|at|from)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2})"
        tag_pattern = r"#(\w+)"
        
        # Content type keywords
        content_type_keywords = {
            "note": ["note", "notes", "document"],
            "todo": ["todo", "task", "todos", "tasks"],
            "calendar": ["event", "meeting", "appointment", "events", "meetings"],
            "project": ["project", "projects"]
        }
        
        # Filter entity types if specified
        if types:
            entities = {k: v for k, v in entities.items() if k in types}
        
        # Extract entities based on patterns
        if "person" in entities:
            for match in re.finditer(person_pattern, text):
                entities["person"].append({
                    "value": match.group(1),
                    "start": match.start(1),
                    "end": match.end(1)
                })
        
        if "date" in entities:
            for match in re.finditer(date_pattern, text):
                entities["date"].append({
                    "value": match.group(1),
                    "start": match.start(1),
                    "end": match.end(1)
                })
        
        if "location" in entities:
            for match in re.finditer(location_pattern, text):
                entities["location"].append({
                    "value": match.group(1),
                    "start": match.start(1),
                    "end": match.end(1)
                })
        
        if "tag" in entities:
            for match in re.finditer(tag_pattern, text):
                entities["tag"].append({
                    "value": match.group(1),
                    "start": match.start(1),
                    "end": match.end(1)
                })
        
        if "content_type" in entities:
            text_lower = text.lower()
            for content_type, keywords in content_type_keywords.items():
                for keyword in keywords:
                    if keyword in text_lower:
                        # Find position in text
                        start = text_lower.find(keyword)
                        end = start + len(keyword)
                        
                        entities["content_type"].append({
                            "value": content_type,
                            "keyword": keyword,
                            "start": start,
                            "end": end
                        })
        
        return entities
    
    def generate_response(self, query: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a response based on query analysis.
        
        Args:
            query: Natural language query
            analysis: Query analysis
            
        Returns:
            Response with actions and message
        """
        intent = analysis.get("intent", "unknown")
        content_type = analysis.get("content_type")
        entities = analysis.get("entities", {})
        
        # Determine action based on intent and entities
        action = {
            "type": intent,
            "parameters": {}
        }
        
        # Generate natural language response
        response_text = ""
        
        if intent == "search":
            search_term = query
            for key in ["person", "tag", "content_type"]:
                if key in entities and entities[key]:
                    for entity in entities[key]:
                        # Remove the entity from the search term to get cleaner results
                        search_term = search_term.replace(entity.get("value", ""), "").strip()
            
            action["parameters"]["search_term"] = search_term
            action["parameters"]["content_type"] = content_type
            
            response_text = f"I'll search for '{search_term}'"
            if content_type:
                response_text += f" in {content_type}s"
                
        elif intent == "create":
            title = ""
            if "content_type" in entities and entities["content_type"]:
                content_type_entity = entities["content_type"][0]
                # Look for text after the content type keyword
                keyword = content_type_entity.get("keyword", "")
                keyword_pos = query.lower().find(keyword)
                if keyword_pos >= 0:
                    remaining_text = query[keyword_pos + len(keyword):].strip()
                    # Extract title - everything after "called", "named", "titled" or ":"
                    title_match = re.search(r"(?:called|named|titled|:)\s*(.+)", remaining_text)
                    if title_match:
                        title = title_match.group(1).strip()
                    else:
                        # Just use the remaining text
                        title = remaining_text
            
            action["parameters"]["title"] = title
            action["parameters"]["content_type"] = content_type
            
            response_text = f"I'll create a new {content_type or 'note'}"
            if title:
                response_text += f" titled '{title}'"
                
        elif intent == "list":
            content_type_to_list = content_type
            if "content_type" in entities and entities["content_type"]:
                content_type_to_list = entities["content_type"][0].get("value", "")
            
            action["parameters"]["content_type"] = content_type_to_list
            
            response_text = f"Here are your {content_type_to_list or 'notes'}"
            
        else:
            response_text = "I'm not sure how to help with that query."
        
        return {
            "text": response_text,
            "action": action,
            "query": query
        }
    
    def summarize_text(self, text: str, max_length: int = 200) -> str:
        """
        Summarize text to a specified maximum length.
        
        Args:
            text: Text to summarize
            max_length: Maximum length of summary
            
        Returns:
            Summarized text
        """
        # This is a simplified implementation
        # A real implementation would use a proper NLP library
        
        if len(text) <= max_length:
            return text
        
        # Split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        # Keep adding sentences until we exceed max_length
        summary = ""
        for sentence in sentences:
            if len(summary) + len(sentence) <= max_length:
                summary += sentence + " "
            else:
                break
        
        return summary.strip()
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Sentiment analysis results
        """
        # This is a simplified implementation
        # A real implementation would use a proper NLP library
        
        # Count positive and negative words
        positive_words = ["good", "great", "excellent", "positive", "happy", "like", "love",
                         "best", "better", "awesome", "amazing", "wonderful", "fantastic"]
        negative_words = ["bad", "poor", "negative", "unhappy", "dislike", "hate",
                         "worst", "worse", "terrible", "awful", "disappointing", "frustrating"]
        
        text_lower = text.lower()
        words = re.findall(r'\w+', text_lower)
        
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        total_words = len(words)
        
        # Calculate sentiment score (-1 to 1)
        if total_words > 0:
            sentiment_score = (positive_count - negative_count) / total_words
        else:
            sentiment_score = 0
            
        # Determine sentiment label
        if sentiment_score > 0.05:
            sentiment = "positive"
        elif sentiment_score < -0.05:
            sentiment = "negative"
        else:
            sentiment = "neutral"
            
        return {
            "sentiment": sentiment,
            "score": sentiment_score,
            "positive_words": positive_count,
            "negative_words": negative_count,
            "total_words": total_words
        }
    
    def generate_tags(self, text: str, max_tags: int = 5) -> List[str]:
        """
        Generate tags from text.
        
        Args:
            text: Text to generate tags from
            max_tags: Maximum number of tags to generate
            
        Returns:
            List of tags
        """
        # This is a simplified implementation
        # A real implementation would use a proper NLP library
        
        # Extract keyterms using TF-IDF or similar approach
        # For simplicity, we'll use word frequency
        text_lower = text.lower()
        
        # Remove stop words
        stop_words = ["i", "me", "my", "myself", "we", "our", "ours", "ourselves",
                     "you", "your", "yours", "yourself", "yourselves", "he", "him", 
                     "his", "himself", "she", "her", "hers", "herself", "it", "its",
                     "itself", "they", "them", "their", "theirs", "themselves", 
                     "what", "which", "who", "whom", "this", "that", "these", "those",
                     "am", "is", "are", "was", "were", "be", "been", "being", "have",
                     "has", "had", "having", "do", "does", "did", "doing", "a", "an",
                     "the", "and", "but", "if", "or", "because", "as", "until", "while",
                     "of", "at", "by", "for", "with", "about", "against", "between",
                     "into", "through", "during", "before", "after", "above", "below",
                     "to", "from", "up", "down", "in", "out", "on", "off", "over", "under",
                     "again", "further", "then", "once", "here", "there", "when", "where",
                     "why", "how", "all", "any", "both", "each", "few", "more", "most",
                     "other", "some", "such", "no", "nor", "not", "only", "own", "same",
                     "so", "than", "too", "very", "can", "will", "just", "don", "should",
                     "now"]
        
        # Extract words and count frequency
        words = re.findall(r'\w+', text_lower)
        word_counts = {}
        
        for word in words:
            if word not in stop_words and len(word) > 3:  # Only consider words longer than 3 characters
                word_counts[word] = word_counts.get(word, 0) + 1
        
        # Sort by frequency
        sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Get top tags
        tags = [word for word, count in sorted_words[:max_tags]]
        
        return tags
    
    def _detect_content_type(self, query: str, entities: Dict[str, List]) -> str:
        """
        Detect content type from query and entities.
        
        Args:
            query: Query text
            entities: Extracted entities
            
        Returns:
            Detected content type
        """
        # Check for explicit content type in entities
        if "content_type" in entities and entities["content_type"]:
            return entities["content_type"][0].get("value", "")
        
        # Check for content type keywords in query
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["todo", "task", "todos", "tasks", "to-do"]):
            return "todo"
        elif any(word in query_lower for word in ["event", "meeting", "appointment", "events", "schedule"]):
            return "calendar"
        elif any(word in query_lower for word in ["project", "projects"]):
            return "project"
        elif any(word in query_lower for word in ["note", "notes", "document", "documents"]):
            return "note"
        
        # Default to note
        return "note"


@lru_cache
def get_nlp_service() -> NLPService:
    """
    Get or create an NLPService instance.
    
    Returns:
        Singleton NLPService instance
    """
    return NLPService() 