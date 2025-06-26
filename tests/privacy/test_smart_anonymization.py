#!/usr/bin/env python3
"""
Tests for smart anonymization module
"""

import pytest
from unittest.mock import patch, MagicMock
import re
import time

from knowledge_base.privacy.smart_anonymization import (
    PrivacyEngine, DeidentificationResult
)
from knowledge_base.privacy.circuit_breaker import (
    CircuitBreaker, CircuitState, CircuitOpenError
)


class TestPrivacyEngine:
    """Test suite for PrivacyEngine."""
    
    def test_initialization(self):
        """Test proper initialization of the privacy engine."""
        engine = PrivacyEngine()
        assert hasattr(engine, "sessions")
        assert isinstance(engine.sessions, dict)
        assert hasattr(engine, "_deidentify_circuit")
        assert isinstance(engine._deidentify_circuit, CircuitBreaker)
        assert hasattr(engine, "_reconstruct_circuit")
        assert isinstance(engine._reconstruct_circuit, CircuitBreaker)
    
    def test_create_session(self):
        """Test session creation."""
        engine = PrivacyEngine()
        session_id = engine.create_session(privacy_level="strict")
        
        assert session_id in engine.sessions
        assert engine.sessions[session_id]["privacy_level"] == "strict"
        
        # Test default privacy level
        default_session_id = engine.create_session()
        assert engine.sessions[default_session_id]["privacy_level"] == "balanced"
    
    def test_deidentify_simple(self):
        """Test basic de-identification."""
        engine = PrivacyEngine()
        session_id = engine.create_session()
        
        text = "John Smith called from 555-123-4567 about Project Phoenix"
        result = engine.deidentify(text, session_id)
        
        # Check result structure
        assert isinstance(result, DeidentificationResult)
        assert result.session_id == session_id
        assert result.privacy_level == "balanced"
        assert len(result.token_map) > 0
        
        # Check token substitutions in text
        assert "John Smith" not in result.text
        assert "555-123-4567" not in result.text
        assert "Project Phoenix" not in result.text
        
        # Check tokens are present
        assert re.search(r'\[PERSON_\d+\]', result.text)
        assert re.search(r'\[PHONE_\d+\]', result.text)
        assert re.search(r'\[PROJECT_\d+\]', result.text)
    
    def test_reconstruct(self):
        """Test reconstruction of de-identified text."""
        engine = PrivacyEngine()
        session_id = engine.create_session()
        
        # De-identify text first
        original_text = "John Smith called about Project Phoenix"
        result = engine.deidentify(original_text, session_id)
        anonymized_text = result.text
        
        # Reconstruct
        reconstructed = engine.reconstruct(anonymized_text, session_id)
        
        # Check that reconstruction restores original text
        assert "John Smith" in reconstructed
        assert "Project Phoenix" in reconstructed
    
    def test_token_consistency(self):
        """Test that the same token is used for the same entity."""
        engine = PrivacyEngine()
        session_id = engine.create_session()
        
        # De-identify two texts with the same entity
        text1 = "John Smith works on Project Phoenix."
        text2 = "Project Phoenix is led by John Smith."
        
        result1 = engine.deidentify(text1, session_id)
        result2 = engine.deidentify(text2, session_id)
        
        # Extract tokens
        john_token_1 = None
        phoenix_token_1 = None
        john_token_2 = None
        phoenix_token_2 = None
        
        for token, value in result1.token_map.items():
            if value == "John Smith":
                john_token_1 = token
            elif value == "Project Phoenix":
                phoenix_token_1 = token
        
        for token, value in result2.token_map.items():
            if value == "John Smith":
                john_token_2 = token
            elif value == "Project Phoenix":
                phoenix_token_2 = token
        
        # Check token consistency
        assert john_token_1 is not None
        assert phoenix_token_1 is not None
        assert john_token_1 == john_token_2
        assert phoenix_token_1 == phoenix_token_2
    
    def test_deidentify_batch(self):
        """Test batch de-identification."""
        engine = PrivacyEngine()
        session_id = engine.create_session()
        
        texts = [
            "John Smith called from 555-123-4567.",
            "Project Phoenix meeting with Sarah Johnson.",
            "Email john.smith@example.com for details."
        ]
        
        results = engine.deidentify_batch(texts, session_id)
        
        # Check that we got results for all texts
        assert len(results) == 3
        
        # Check that each result is properly anonymized
        for i, result in enumerate(results):
            assert isinstance(result, DeidentificationResult)
            assert result.session_id == session_id
            
            # Text-specific checks
            if i == 0:
                assert "John Smith" not in result.text
                assert "555-123-4567" not in result.text
            elif i == 1:
                assert "Project Phoenix" not in result.text
                assert "Sarah Johnson" not in result.text
            elif i == 2:
                assert "john.smith@example.com" not in result.text
    
    def test_enhance_for_ai(self):
        """Test AI enhancement of de-identified text."""
        # Create a mock token intelligence bridge
        mock_bridge = MagicMock()
        mock_bridge.enhance_privacy_text.return_value = "Enhanced Text"
        
        engine = PrivacyEngine()
        engine.token_intelligence_bridge = mock_bridge
        
        session_id = engine.create_session()
        
        # Add some context to the session
        engine.sessions[session_id]["preserved_context"] = ["important", "context"]
        
        # Test enhancement
        result = engine.enhance_for_ai("Anonymized text", session_id)
        
        # Verify bridge was called correctly
        mock_bridge.enhance_privacy_text.assert_called_once()
        assert result == "Enhanced Text"
        
        # Test with non-existent session
        result = engine.enhance_for_ai("Text", "non-existent-session")
        assert result == "Text"  # Should return original text
        
        # Test with exception in enhancement
        mock_bridge.enhance_privacy_text.side_effect = Exception("Enhancement error")
        result = engine.enhance_for_ai("Text with error", session_id)
        assert result == "Text with error"  # Should return original text

    def test_circuit_breaker_deidentify(self):
        """Test circuit breaker for deidentify."""
        engine = PrivacyEngine()
        session_id = engine.create_session()
        
        # Mock _deidentify_impl to fail
        with patch.object(engine, '_deidentify_impl', side_effect=Exception("Simulated failure")):
            # Set circuit breaker to trip after 1 failure
            engine._deidentify_circuit.failure_threshold = 1
            
            # First call should try and fail, using fallback
            with patch.object(engine, '_deidentify_fallback', return_value=DeidentificationResult(
                text="Fallback text",
                session_id=session_id,
                privacy_level="minimal",
                token_map={},
                entity_relationships={}
            )) as mock_fallback:
                result = engine.deidentify("Test text", session_id)
                
                # Check that fallback was used
                mock_fallback.assert_called_once()
                assert result.text == "Fallback text"
                assert result.privacy_level == "minimal"
                
                # Circuit should now be open
                assert engine._deidentify_circuit.state == CircuitState.OPEN
            
            # Second call should short-circuit directly to fallback
            with patch.object(engine, '_deidentify_fallback', return_value=DeidentificationResult(
                text="Fallback text 2",
                session_id=session_id,
                privacy_level="minimal",
                token_map={},
                entity_relationships={}
            )) as mock_fallback:
                result = engine.deidentify("Another test", session_id)
                
                # Check that fallback was used again
                mock_fallback.assert_called_once()
                assert result.text == "Fallback text 2"
                
                # Original impl should not be called
                assert engine._deidentify_impl.call_count == 1  # Only from first call
    
    def test_circuit_breaker_reconstruct(self):
        """Test circuit breaker for reconstruct."""
        engine = PrivacyEngine()
        session_id = engine.create_session()
        
        # Mock _reconstruct_impl to fail
        with patch.object(engine, '_reconstruct_impl', side_effect=Exception("Simulated failure")):
            # Set circuit breaker to trip after 1 failure
            engine._reconstruct_circuit.failure_threshold = 1
            
            # First call should try and fail, using fallback
            with patch.object(engine, '_reconstruct_fallback', return_value="Fallback reconstruction") as mock_fallback:
                result = engine.reconstruct("[TOKEN_001]", session_id)
                
                # Check that fallback was used
                mock_fallback.assert_called_once()
                assert result == "Fallback reconstruction"
                
                # Circuit should now be open
                assert engine._reconstruct_circuit.state == CircuitState.OPEN
            
            # Second call should short-circuit directly to fallback
            with patch.object(engine, '_reconstruct_fallback', return_value="Fallback reconstruction 2") as mock_fallback:
                result = engine.reconstruct("[TOKEN_002]", session_id)
                
                # Check that fallback was used again
                mock_fallback.assert_called_once()
                assert result == "Fallback reconstruction 2"
                
                # Original impl should not be called
                assert engine._reconstruct_impl.call_count == 1  # Only from first call
    
    def test_circuit_breaker_batch(self):
        """Test circuit breaker for batch operations."""
        engine = PrivacyEngine()
        session_id = engine.create_session()
        
        # Mock _deidentify_batch_impl to fail
        with patch.object(engine, '_deidentify_batch_impl', side_effect=Exception("Simulated batch failure")):
            # Set circuit breaker to trip after 1 failure
            engine._batch_circuit.failure_threshold = 1
            
            # First call should try and fail, using fallback
            with patch.object(engine, '_deidentify_batch_fallback', return_value=[
                DeidentificationResult(
                    text="Fallback batch text",
                    session_id=session_id,
                    privacy_level="minimal",
                    token_map={},
                    entity_relationships={}
                )
            ]) as mock_fallback:
                result = engine.deidentify_batch(["Test text"], session_id)
                
                # Check that fallback was used
                mock_fallback.assert_called_once()
                assert result[0].text == "Fallback batch text"
                assert result[0].privacy_level == "minimal"
                
                # Circuit should now be open
                assert engine._batch_circuit.state == CircuitState.OPEN
    
    def test_recovery_timeout(self):
        """Test circuit recovery after timeout."""
        # Use a very short timeout for testing
        engine = PrivacyEngine()
        engine._deidentify_circuit.recovery_timeout = 0.1
        engine._deidentify_circuit.failure_threshold = 1
        session_id = engine.create_session()
        
        # First make the circuit fail and open
        with patch.object(engine, '_deidentify_impl', side_effect=Exception("Simulated failure")):
            try:
                engine.deidentify("Test text", session_id)
            except Exception:
                pass
        
        assert engine._deidentify_circuit.state == CircuitState.OPEN
        
        # Wait for recovery timeout
        time.sleep(0.2)
        
        # Now mock the impl to succeed
        with patch.object(engine, '_deidentify_impl', return_value=DeidentificationResult(
            text="Success after recovery",
            session_id=session_id,
            privacy_level="balanced",
            token_map={},
            entity_relationships={}
        )):
            result = engine.deidentify("Test text", session_id)
        
        # Should have recovered and used real implementation
        assert result.text == "Success after recovery"
        assert engine._deidentify_circuit.state == CircuitState.CLOSED
    
    def test_deidentify_fallback(self):
        """Test the fallback implementation for deidentify."""
        engine = PrivacyEngine()
        session_id = engine.create_session()
        
        # Add some token mappings to the session
        engine.sessions[session_id]["token_mappings"] = {
            "PERSON_001": "John Smith",
            "PROJECT_001": "Project Phoenix"
        }
        
        # Test fallback with matching text
        text = "John Smith is working on Project Phoenix"
        result = engine._deidentify_fallback(text, session_id)
        
        # Should replace known entities
        assert "John Smith" not in result.text
        assert "Project Phoenix" not in result.text
        assert "[PERSON_001]" in result.text
        assert "[PROJECT_001]" in result.text
        
        # Test with missing session
        result = engine._deidentify_fallback("Some text", "invalid-session")
        assert isinstance(result, DeidentificationResult)
        assert result.privacy_level == "minimal"
    
    def test_reconstruct_fallback(self):
        """Test the fallback implementation for reconstruct."""
        engine = PrivacyEngine()
        session_id = engine.create_session()
        
        # Add some token mappings to the session
        engine.sessions[session_id]["token_mappings"] = {
            "PERSON_001": "John Smith",
            "PROJECT_001": "Project Phoenix"
        }
        
        # Test fallback with bracket format
        text = "[PERSON_001] is working on [PROJECT_001]"
        result = engine._reconstruct_fallback(text, session_id)
        
        # Should replace known tokens in brackets
        assert "John Smith" in result
        assert "Project Phoenix" in result
        
        # Test with non-bracket format - shouldn't replace
        text = "PERSON_001 is working on PROJECT_001"
        result = engine._reconstruct_fallback(text, session_id)
        
        # Should not replace tokens without brackets
        assert "John Smith" not in result
        assert "Project Phoenix" not in result
        assert "PERSON_001" in result
        
        # Test with missing session
        result = engine._reconstruct_fallback("[TOKEN_001]", "invalid-session")
        assert result == "[TOKEN_001]"  # Should return original text
    
    def test_batch_fallback(self):
        """Test the fallback implementation for batch processing."""
        engine = PrivacyEngine()
        session_id = engine.create_session()
        
        # Add some token mappings to the session
        engine.sessions[session_id]["token_mappings"] = {
            "PERSON_001": "John Smith",
            "PROJECT_001": "Project Phoenix"
        }
        
        # Test batch fallback
        texts = [
            "John Smith is here",
            "Project Phoenix is secret"
        ]
        
        results = engine._deidentify_batch_fallback(texts, session_id)
        
        # Should have results for both texts
        assert len(results) == 2
        
        # Should have replaced known entities
        assert "John Smith" not in results[0].text
        assert "Project Phoenix" not in results[1].text
        
        # Test with error in one text
        with patch.object(engine, '_deidentify_fallback') as mock_fallback:
            mock_fallback.side_effect = [
                DeidentificationResult(text="Success", session_id=session_id, privacy_level="minimal", 
                                      token_map={}, entity_relationships={}),
                Exception("Test error")
            ]
            
            results = engine._deidentify_batch_fallback(["Text1", "Text2"], session_id)
            
            # Should still have 2 results despite the error
            assert len(results) == 2
            assert results[0].text == "Success"
            assert results[1].text == "Text2"  # Original text preserved 