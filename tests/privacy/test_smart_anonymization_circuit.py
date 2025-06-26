#!/usr/bin/env python3
"""
Tests for circuit breaker integration with smart anonymization
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


class TestPrivacyEngineCircuitBreaker:
    """Test circuit breaker integration with PrivacyEngine."""
    
    def test_initialization(self):
        """Test that circuit breakers are properly initialized."""
        engine = PrivacyEngine()
        
        assert hasattr(engine, "_deidentify_circuit")
        assert isinstance(engine._deidentify_circuit, CircuitBreaker)
        assert engine._deidentify_circuit.name == "privacy_deidentify"
        
        assert hasattr(engine, "_reconstruct_circuit")
        assert isinstance(engine._reconstruct_circuit, CircuitBreaker)
        assert engine._reconstruct_circuit.name == "privacy_reconstruct"
        
        assert hasattr(engine, "_batch_circuit")
        assert isinstance(engine._batch_circuit, CircuitBreaker)
        assert engine._batch_circuit.name == "privacy_batch"
    
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
            with patch.object(engine, '_deidentify_fallback', return_value=DeidentificationResult(
                text="Fallback",
                session_id=session_id,
                privacy_level="minimal",
                token_map={},
                entity_relationships={}
            )):
                engine.deidentify("Test text", session_id)
        
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
    
    def test_half_open_state(self):
        """Test circuit half-open state behavior."""
        engine = PrivacyEngine()
        engine._deidentify_circuit.recovery_timeout = 0.1
        engine._deidentify_circuit.failure_threshold = 1
        engine._deidentify_circuit.half_open_max_calls = 1
        session_id = engine.create_session()
        
        # First make the circuit fail and open
        with patch.object(engine, '_deidentify_impl', side_effect=Exception("Simulated failure")):
            with patch.object(engine, '_deidentify_fallback', return_value=DeidentificationResult(
                text="Fallback",
                session_id=session_id,
                privacy_level="minimal",
                token_map={},
                entity_relationships={}
            )):
                engine.deidentify("Test text", session_id)
        
        assert engine._deidentify_circuit.state == CircuitState.OPEN
        
        # Wait for recovery timeout to transition to half-open
        time.sleep(0.2)
        
        # First call in half-open should try real implementation
        # But make it fail again
        with patch.object(engine, '_deidentify_impl', side_effect=Exception("Another failure")):
            with patch.object(engine, '_deidentify_fallback', return_value=DeidentificationResult(
                text="Fallback after half-open",
                session_id=session_id,
                privacy_level="minimal",
                token_map={},
                entity_relationships={}
            )):
                result = engine.deidentify("Test text", session_id)
        
        # Should be back to open after failing in half-open
        assert engine._deidentify_circuit.state == CircuitState.OPEN
        assert result.text == "Fallback after half-open"
    
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

    def test_enhance_for_ai_error_handling(self):
        """Test error handling in enhance_for_ai method."""
        engine = PrivacyEngine()
        session_id = engine.create_session()
        
        # Setup token intelligence bridge to raise an exception
        engine.token_intelligence_bridge.enhance_privacy_text = MagicMock(
            side_effect=Exception("Token intelligence error")
        )
        
        # Should handle the exception and return original text
        text = "Original text with [TOKEN_001]"
        result = engine.enhance_for_ai(text, session_id)
        
        assert result == text
        engine.token_intelligence_bridge.enhance_privacy_text.assert_called_once()
    
    def test_custom_circuit_breaker_config(self):
        """Test circuit breaker with custom configuration."""
        # Create engine with custom circuit breaker config
        engine = PrivacyEngine({
            "circuit_breaker": {
                "failure_threshold": 10,
                "recovery_timeout": 60
            }
        })
        
        # Check that config was applied
        assert engine._deidentify_circuit.failure_threshold == 10
        assert engine._deidentify_circuit.recovery_timeout == 60
        assert engine._reconstruct_circuit.failure_threshold == 10
        assert engine._reconstruct_circuit.recovery_timeout == 60
        assert engine._batch_circuit.failure_threshold == 10
        assert engine._batch_circuit.recovery_timeout == 60 