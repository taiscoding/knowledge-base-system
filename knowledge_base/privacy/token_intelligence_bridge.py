#!/usr/bin/env python3
"""
Token Intelligence Bridge
Handles integration between the privacy layer and the token intelligence system.
"""

import logging
import importlib.util
from typing import Dict, List, Any, Optional
import re

logger = logging.getLogger(__name__)

# Dummy class for fallback when token intelligence isn't available
class DummyTokenIntelligenceResponse:
    """Dummy response when token intelligence is unavailable."""
    def __init__(self):
        self.intelligence = {}
        self.confidence = 0.0
        self.intelligence_type = "unavailable"
        self.source = "fallback"
        self.processing_time_ms = 0


class TokenIntelligenceBridge:
    """Bridge between privacy layer and token intelligence system."""
    
    def __init__(self):
        """Initialize the bridge and try to import token intelligence."""
        self.token_intelligence_available = False
        self.token_intelligence_engine = None
        self.token_intelligence_request_class = None
        
        # Try to import token intelligence
        self._try_import_token_intelligence()
    
    def _try_import_token_intelligence(self):
        """Try to import token intelligence modules."""
        try:
            # Check if token intelligence is installed
            if importlib.util.find_spec("token_intelligence") is not None:
                # Import required classes
                from token_intelligence import TokenIntelligenceEngine
                from token_intelligence.core.data_models import TokenIntelligenceRequest
                
                # Initialize engine
                self.token_intelligence_engine = TokenIntelligenceEngine()
                self.token_intelligence_request_class = TokenIntelligenceRequest
                self.token_intelligence_available = True
                logger.info("Token intelligence system successfully initialized")
            else:
                logger.warning("Token intelligence module not available")
                self.token_intelligence_available = False
        except Exception as e:
            logger.warning(f"Error initializing token intelligence: {e}")
            self.token_intelligence_available = False
    
    def generate_intelligence(self, 
                             privacy_text: str, 
                             session_id: str,
                             preserved_context: List[str],
                             entity_relationships: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate intelligence for privacy tokens.
        
        Args:
            privacy_text: Text with privacy tokens
            session_id: Session ID
            preserved_context: List of context keywords
            entity_relationships: Dictionary of entity relationships
            
        Returns:
            Dictionary of token intelligence
        """
        # Try to use token intelligence if available
        if self.token_intelligence_available and self.token_intelligence_engine:
            try:
                # Create request
                request = self.token_intelligence_request_class(
                    privacy_text=privacy_text,
                    session_id=session_id,
                    preserved_context=preserved_context,
                    entity_relationships=entity_relationships
                )
                
                # Generate intelligence
                response = self.token_intelligence_engine.generate_intelligence(request)
                return response.intelligence
            except Exception as e:
                logger.error(f"Error generating token intelligence: {e}")
                return self._generate_fallback_intelligence(privacy_text)
        else:
            return self._generate_fallback_intelligence(privacy_text)
    
    def _generate_fallback_intelligence(self, privacy_text: str) -> Dict[str, Any]:
        """
        Generate basic fallback intelligence when token intelligence isn't available.
        
        Args:
            privacy_text: Text with privacy tokens
            
        Returns:
            Basic token intelligence dictionary
        """
        intelligence = {}
        
        # Extract tokens from privacy text
        tokens = re.findall(r'\[([A-Z_]+(?:_\d+)?)\]', privacy_text)
        
        # Generate basic intelligence for each token
        for token in tokens:
            token_type = token.split('_')[0]
            
            # Add generic intelligence based on token type
            if token_type == "PERSON":
                intelligence[f"{token}_type"] = "individual"
                intelligence[f"{token}_context"] = "mentioned_in_content"
            elif token_type == "PHONE":
                intelligence[f"{token}_type"] = "contact_method"
            elif token_type == "EMAIL":
                intelligence[f"{token}_type"] = "contact_method"
                intelligence[f"{token}_context"] = "electronic_communication"
            elif token_type == "LOCATION":
                intelligence[f"{token}_type"] = "physical_place"
            elif token_type == "PROJECT":
                intelligence[f"{token}_type"] = "work_activity"
                intelligence[f"{token}_context"] = "professional"
        
        return intelligence
    
    def enhance_privacy_text(self, 
                            privacy_text: str, 
                            session_id: str,
                            preserved_context: List[str],
                            entity_relationships: Dict[str, Any]) -> str:
        """
        Enhance privacy text with intelligence context.
        
        Args:
            privacy_text: Text with privacy tokens
            session_id: Session ID
            preserved_context: List of context keywords
            entity_relationships: Dictionary of entity relationships
            
        Returns:
            Enhanced text with context hints for AI
        """
        # Get intelligence for tokens
        intelligence = self.generate_intelligence(
            privacy_text, 
            session_id, 
            preserved_context, 
            entity_relationships
        )
        
        # Extract tokens from text
        tokens = re.findall(r'\[([A-Z_]+(?:_\d+)?)\]', privacy_text)
        
        # Create enhanced prompt with context
        enhanced_text = privacy_text
        
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