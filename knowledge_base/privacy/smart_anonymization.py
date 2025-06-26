#!/usr/bin/env python3
"""
Smart Anonymization Module
Core functionality for privacy-preserving data anonymization.
"""

import re
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class DeidentificationResult:
    """Results of a deidentification operation."""
    text: str
    tokens: Dict[str, str]
    token_map: Dict[str, str]
    entity_relationships: Dict[str, Dict[str, Any]]
    privacy_level: str


class PrivacyEngine:
    """
    Core privacy engine that handles smart anonymization.
    
    This engine provides token-based anonymization to protect sensitive data
    while preserving the essential meaning and context for AI operations.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the privacy engine.
        
        Args:
            config: Configuration dictionary for privacy settings
        """
        self.config = config or {}
        self.sessions = {}
        self._initialize_detection_patterns()
    
    def _initialize_detection_patterns(self):
        """Initialize patterns for detecting sensitive information."""
        # Person name detection patterns
        self.name_patterns = [
            r'\b(?:[A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b',  # First Last, First Middle Last
            r'\b(?:[A-Z][a-z]+(?:-[A-Z][a-z]+))\b',  # Hyphenated names
            r'\b(?:[A-Z][a-z]+\'[A-Z]?[a-z]+)\b',  # Names with apostrophes
        ]
        
        # Phone number patterns
        self.phone_patterns = [
            r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b',  # Standard US phone: 555-555-5555
            r'\(\d{3}\)\s*\d{3}[-.\s]?\d{4}\b',     # Parentheses format: (555) 555-5555
            r'\+\d{1,3}\s*\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b'  # International: +1 555-555-5555
        ]
        
        # Email patterns
        self.email_patterns = [
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'  # standard email
        ]
        
        # Location patterns
        self.location_patterns = [
            r'\b\d{1,5}\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Place|Pl|Court|Ct|Way)\b',
            r'\b[A-Z][a-z]+(?:town|ville|burg|city)\b'
        ]
        
        # Project patterns
        self.project_patterns = [
            r'\b(?:Project|Initiative)\s+[A-Z][a-zA-Z]+\b',
            r'\b[A-Z][a-zA-Z]+\s+(?:Project|Initiative)\b'
        ]
    
    def create_session(self, privacy_level: str = "balanced") -> str:
        """
        Create a new privacy session.
        
        Args:
            privacy_level: Privacy level for the session ("strict", "balanced", "minimal")
            
        Returns:
            Session ID
        """
        import uuid
        
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            "created_at": str(logging.getLogger(__name__)),
            "privacy_level": privacy_level,
            "token_mappings": {},
            "entity_relationships": {},
            "preserved_context": []
        }
        
        return session_id
    
    def deidentify(self, text: str, session_id: str) -> DeidentificationResult:
        """
        De-identify text by replacing sensitive information with tokens.
        
        Args:
            text: Text to de-identify
            session_id: Session ID for token consistency
            
        Returns:
            DeidentificationResult with tokenized text and metadata
        """
        # Ensure session exists
        if session_id not in self.sessions:
            self.create_session("balanced")
            
        session = self.sessions[session_id]
        privacy_level = session["privacy_level"]
        token_mappings = session["token_mappings"]
        entity_relationships = session["entity_relationships"]
        
        # Process text
        processed_text = text
        new_token_mappings = {}
        
        # Detect and tokenize names
        processed_text, name_tokens = self._process_patterns(
            processed_text, 
            self.name_patterns, 
            "PERSON", 
            token_mappings
        )
        new_token_mappings.update(name_tokens)
        
        # Detect and tokenize phone numbers
        processed_text, phone_tokens = self._process_patterns(
            processed_text, 
            self.phone_patterns, 
            "PHONE", 
            token_mappings
        )
        new_token_mappings.update(phone_tokens)
        
        # Detect and tokenize emails
        processed_text, email_tokens = self._process_patterns(
            processed_text, 
            self.email_patterns, 
            "EMAIL", 
            token_mappings
        )
        new_token_mappings.update(email_tokens)
        
        # Detect and tokenize locations
        if privacy_level in ["balanced", "strict"]:
            processed_text, location_tokens = self._process_patterns(
                processed_text, 
                self.location_patterns, 
                "LOCATION", 
                token_mappings
            )
            new_token_mappings.update(location_tokens)
        
        # Detect and tokenize projects
        processed_text, project_tokens = self._process_patterns(
            processed_text, 
            self.project_patterns, 
            "PROJECT", 
            token_mappings
        )
        new_token_mappings.update(project_tokens)
        
        # Update session with new tokens
        token_mappings.update(new_token_mappings)
        self.sessions[session_id]["token_mappings"] = token_mappings
        
        # Update entity relationships
        self._update_entity_relationships(new_token_mappings, entity_relationships)
        
        # Return the result
        return DeidentificationResult(
            text=processed_text,
            tokens=new_token_mappings,
            token_map=token_mappings,
            entity_relationships=entity_relationships,
            privacy_level=privacy_level
        )
    
    def reconstruct(self, text: str, session_id: str) -> str:
        """
        Reconstruct original text by replacing tokens with original values.
        
        Args:
            text: Text with privacy tokens
            session_id: Session ID for token mapping
            
        Returns:
            Reconstructed text with original values
        """
        if session_id not in self.sessions:
            logger.warning(f"Session {session_id} not found")
            return text
            
        session = self.sessions[session_id]
        token_mappings = session["token_mappings"]
        
        reconstructed = text
        
        # Replace all tokens with original values
        for token, original in token_mappings.items():
            reconstructed = reconstructed.replace(f"[{token}]", original)
            
        return reconstructed
    
    def enhance_for_ai(self, text: str, session_id: str) -> str:
        """
        Enhance de-identified text with context for AI processing.
        
        Args:
            text: De-identified text
            session_id: Session ID
            
        Returns:
            Enhanced text with context hints for AI
        """
        from token_intelligence import TokenIntelligenceEngine
        
        if session_id not in self.sessions:
            logger.warning(f"Session {session_id} not found")
            return text
        
        session = self.sessions[session_id]
        preserved_context = session.get("preserved_context", [])
        entity_relationships = session.get("entity_relationships", {})
        
        # Extract tokens from text
        tokens = re.findall(r'\[([A-Z_]+(?:_\d+)?)\]', text)
        
        # Get intelligence for tokens
        intelligence_engine = TokenIntelligenceEngine()
        
        from token_intelligence.core.data_models import TokenIntelligenceRequest
        request = TokenIntelligenceRequest(
            privacy_text=text,
            preserved_context=preserved_context,
            entity_relationships=entity_relationships,
            session_id=session_id
        )
        
        response = intelligence_engine.generate_intelligence(request)
        intelligence = response.intelligence
        
        # Create enhanced prompt with context
        enhanced_text = text
        
        # Add intelligence context based on token type
        if intelligence:
            enhanced_text += "\n\nContext (Privacy-Preserved):\n"
            for token in tokens:
                token_context = {}
                for key, value in intelligence.items():
                    if key.startswith(token):
                        context_key = key.replace(f"{token}_", "")
                        token_context[context_key] = value
                
                if token_context:
                    enhanced_text += f"\n[{token}]: {token_context}\n"
        
        return enhanced_text
    
    def _process_patterns(
        self, 
        text: str, 
        patterns: List[str], 
        token_type: str,
        existing_mappings: Dict[str, str]
    ) -> Tuple[str, Dict[str, str]]:
        """
        Process text with a list of patterns and tokenize matches.
        
        Args:
            text: Text to process
            patterns: List of regex patterns to match
            token_type: Type of token (PERSON, PHONE, etc.)
            existing_mappings: Existing token mappings
            
        Returns:
            Tuple of (processed_text, new_token_mappings)
        """
        processed = text
        new_mappings = {}
        reverse_map = {v: k for k, v in existing_mappings.items()}
        
        # Find the highest token number for this type
        token_counter = 1
        for token in existing_mappings.keys():
            if token.startswith(token_type):
                try:
                    num = int(token.split('_')[1])
                    token_counter = max(token_counter, num + 1)
                except (IndexError, ValueError):
                    pass
        
        # Process each pattern
        for pattern in patterns:
            matches = re.finditer(pattern, processed)
            
            # Process matches in reverse order to avoid messing up string indexes
            matches = list(matches)
            for match in reversed(matches):
                original = match.group(0)
                
                # Skip if already a token
                if original.startswith('[') and original.endswith(']'):
                    continue
                    
                # Check if we've already seen this value
                if original in reverse_map:
                    token = reverse_map[original]
                else:
                    # Create new token
                    token = f"{token_type}_{token_counter:03d}"
                    token_counter += 1
                    new_mappings[token] = original
                    reverse_map[original] = token
                
                # Replace in text
                processed = processed[:match.start()] + f"[{token}]" + processed[match.end():]
        
        return processed, new_mappings
    
    def _update_entity_relationships(
        self, 
        new_tokens: Dict[str, str], 
        entity_relationships: Dict[str, Dict[str, Any]]
    ) -> None:
        """
        Update entity relationships based on new tokens.
        
        Args:
            new_tokens: New token mappings
            entity_relationships: Existing entity relationships
        """
        # Initialize relationship entries for new tokens
        for token in new_tokens:
            if token not in entity_relationships:
                entity_relationships[token] = {
                    "type": token.split('_')[0],
                    "linked_entities": []
                }
                
        # TODO: Implement more sophisticated relationship detection
        # This would involve analyzing context to determine relationships 