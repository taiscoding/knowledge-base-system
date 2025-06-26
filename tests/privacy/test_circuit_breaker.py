#!/usr/bin/env python3
"""
Test suite for the Circuit Breaker pattern implementation.
"""

import time
import pytest
from unittest.mock import MagicMock, patch

from knowledge_base.privacy.circuit_breaker import (
    CircuitBreaker, CircuitState, CircuitBreakerError,
    CircuitOpenError, with_circuit_breaker
)


class TestCircuitBreaker:
    """Test suite for the CircuitBreaker class."""
    
    def test_initialization(self):
        """Test that the circuit breaker initializes in closed state."""
        cb = CircuitBreaker("test-circuit")
        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 0
        assert cb.name == "test-circuit"
        
        # Test with custom parameters
        cb = CircuitBreaker(
            "custom-circuit", 
            failure_threshold=10,
            recovery_timeout=60,
            half_open_max_calls=5
        )
        assert cb.failure_threshold == 10
        assert cb.recovery_timeout == 60
        assert cb.half_open_max_calls == 5
    
    def test_successful_execution(self):
        """Test successful function execution."""
        cb = CircuitBreaker("test-success")
        test_fn = MagicMock(return_value="success")
        
        result = cb.execute(test_fn, arg1="test", arg2=123)
        
        assert result == "success"
        test_fn.assert_called_once_with(arg1="test", arg2=123)
        assert cb.state == CircuitState.CLOSED
        assert cb.successful_calls == 1
        assert cb.failed_calls == 0
        assert cb.total_calls == 1
    
    def test_failure_threshold(self):
        """Test that circuit opens after failure threshold is reached."""
        cb = CircuitBreaker("test-failures", failure_threshold=3)
        test_fn = MagicMock(side_effect=Exception("Simulated failure"))
        fallback_fn = MagicMock(return_value="fallback")
        
        # First failure
        with pytest.raises(Exception):
            cb.execute(test_fn)
        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 1
        
        # Second failure
        with pytest.raises(Exception):
            cb.execute(test_fn)
        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 2
        
        # Third failure - should trip circuit
        with pytest.raises(Exception):
            cb.execute(test_fn)
        assert cb.state == CircuitState.OPEN
        assert cb.failure_count == 3
        
        # Fourth call with fallback - circuit is open
        result = cb.execute(test_fn, fallback=fallback_fn)
        assert result == "fallback"
        assert cb.state == CircuitState.OPEN
        # Original function should not be called again
        assert test_fn.call_count == 3
        assert fallback_fn.call_count == 1
        assert cb.short_circuited_calls == 1
    
    def test_open_circuit_without_fallback(self):
        """Test that open circuit raises CircuitOpenError when no fallback is provided."""
        cb = CircuitBreaker("test-no-fallback", failure_threshold=1)
        test_fn = MagicMock(side_effect=Exception("Simulated failure"))
        
        # Trip the circuit
        with pytest.raises(Exception):
            cb.execute(test_fn)
        assert cb.state == CircuitState.OPEN
        
        # Next call should raise CircuitOpenError
        with pytest.raises(CircuitOpenError):
            cb.execute(test_fn)
    
    def test_recovery_timeout(self):
        """Test that circuit transitions to half-open after recovery timeout."""
        cb = CircuitBreaker("test-recovery", failure_threshold=1, recovery_timeout=0.1)
        test_fn = MagicMock(side_effect=[Exception("Fail"), "success"])
        
        # Trip the circuit
        with pytest.raises(Exception):
            cb.execute(test_fn)
        assert cb.state == CircuitState.OPEN
        
        # Wait for recovery timeout
        time.sleep(0.2)
        
        # Next call should try the function and succeed
        result = cb.execute(test_fn)
        assert result == "success"
        assert cb.state == CircuitState.CLOSED  # Should reset on success
    
    def test_half_open_state_failure(self):
        """Test that circuit reopens if it fails in half-open state."""
        cb = CircuitBreaker("test-half-open-fail", failure_threshold=1, recovery_timeout=0.1)
        test_fn = MagicMock(side_effect=[Exception("Fail 1"), Exception("Fail 2"), "success"])
        
        # Trip the circuit
        with pytest.raises(Exception):
            cb.execute(test_fn)
        assert cb.state == CircuitState.OPEN
        
        # Wait for recovery timeout
        time.sleep(0.2)
        
        # Next call should try and fail
        with pytest.raises(Exception):
            cb.execute(test_fn)
        assert cb.state == CircuitState.OPEN  # Back to open
        
        # Wait for recovery timeout again
        time.sleep(0.2)
        
        # Next call should try and succeed
        result = cb.execute(test_fn)
        assert result == "success"
        assert cb.state == CircuitState.CLOSED  # Reset on success
    
    def test_half_open_max_calls(self):
        """Test that half-open state enforces max calls."""
        cb = CircuitBreaker("test-half-open-max", failure_threshold=1, recovery_timeout=0.1, half_open_max_calls=2)
        test_fn = MagicMock(return_value="success")
        
        # Set up circuit in half-open state
        cb._change_state(CircuitState.HALF_OPEN)
        
        # Manually set half_open_calls to simulate previous calls
        cb.half_open_calls = 2
        
        # Third call should short-circuit because we're at the limit
        with pytest.raises(CircuitOpenError):
            cb.execute(test_fn)
    
    def test_reset(self):
        """Test resetting the circuit breaker."""
        cb = CircuitBreaker("test-reset")
        cb._change_state(CircuitState.OPEN)
        cb.failure_count = 10
        cb.half_open_calls = 5
        
        cb.reset()
        
        assert cb.state == CircuitState.CLOSED
        assert cb.failure_count == 0
        assert cb.half_open_calls == 0
    
    def test_metrics(self):
        """Test retrieving circuit breaker metrics."""
        cb = CircuitBreaker("test-metrics")
        test_fn = MagicMock(side_effect=[Exception("Fail"), "success"])
        fallback_fn = MagicMock(return_value="fallback")
        
        # Cause failure and use fallback
        with pytest.raises(Exception):
            cb.execute(test_fn)
        
        # Open the circuit
        cb._change_state(CircuitState.OPEN)
        
        # Call with fallback
        cb.execute(test_fn, fallback=fallback_fn)
        
        # Get metrics
        metrics = cb.get_metrics()
        
        assert metrics["name"] == "test-metrics"
        assert metrics["state"] == "open"
        assert metrics["failure_count"] == 1
        assert metrics["total_calls"] == 2
        assert metrics["successful_calls"] == 0
        assert metrics["failed_calls"] == 1
        assert metrics["short_circuited_calls"] == 1
        assert "time_in_current_state" in metrics
    
    def test_with_circuit_breaker_decorator(self):
        """Test the circuit breaker decorator."""
        cb = CircuitBreaker("test-decorator")
        fallback_fn = MagicMock(return_value="fallback")
        
        # Define a function with the decorator
        @with_circuit_breaker(cb, fallback=fallback_fn)
        def test_fn(value):
            if value == "fail":
                raise Exception("Simulated failure")
            return f"success-{value}"
        
        # Test successful execution
        result = test_fn("test")
        assert result == "success-test"
        
        # Test failure - with fallback, so no exception should be raised
        result = test_fn("fail")
        assert result == "fallback"
        fallback_fn.assert_called_once_with("fail")
        
        # Test without fallback to see exception
        @with_circuit_breaker(cb)  # No fallback provided
        def test_fn_no_fallback(value):
            if value == "fail":
                raise Exception("Simulated failure")
            return f"success-{value}"
            
        with pytest.raises(Exception):
            test_fn_no_fallback("fail")
    
    def test_circuit_state_enum(self):
        """Test that CircuitState enum works correctly."""
        assert CircuitState.CLOSED == "closed"
        assert CircuitState.OPEN == "open"
        assert CircuitState.HALF_OPEN == "half_open"
    
    def test_error_hierarchy(self):
        """Test that circuit breaker errors have correct hierarchy."""
        base_error = CircuitBreakerError("Base error")
        open_error = CircuitOpenError("Circuit open")
        
        assert isinstance(base_error, Exception)
        assert isinstance(open_error, CircuitBreakerError)
        assert isinstance(open_error, Exception)


if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 