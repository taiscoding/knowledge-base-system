#!/usr/bin/env python3
"""
Circuit Breaker Module
Implementation of the Circuit Breaker pattern for fault tolerance.
"""

import time
import logging
from enum import Enum
from typing import Any, Callable, Optional, Dict, TypeVar, Generic

logger = logging.getLogger(__name__)

# Type variables for function and result typing
T = TypeVar('T')
R = TypeVar('R')

class CircuitState(str, Enum):
    """Circuit breaker states."""
    CLOSED = "closed"        # Normal operation - requests pass through
    OPEN = "open"            # Failing - requests are short-circuited
    HALF_OPEN = "half_open"  # Testing recovery - limited requests pass through


class CircuitBreakerError(Exception):
    """Base exception for circuit breaker errors."""
    pass


class CircuitOpenError(CircuitBreakerError):
    """Error raised when circuit is open."""
    pass


class CircuitBreaker(Generic[T, R]):
    """
    Circuit Breaker implementation for fault tolerance.
    
    This class implements the Circuit Breaker pattern to prevent cascading failures
    by failing fast when a service is unavailable or experiencing high error rates.
    """
    
    def __init__(
        self, 
        name: str, 
        failure_threshold: int = 5,
        recovery_timeout: int = 30,
        half_open_max_calls: int = 3
    ):
        """
        Initialize the circuit breaker.
        
        Args:
            name: Unique name for this circuit breaker
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds to wait before attempting recovery
            half_open_max_calls: Maximum calls in half-open state
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        
        # State variables
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0
        self.half_open_calls = 0
        
        # Metrics
        self.total_calls = 0
        self.successful_calls = 0
        self.failed_calls = 0
        self.short_circuited_calls = 0
        self.last_state_change_time = time.time()
        
        logger.info(f"Circuit breaker '{name}' initialized in CLOSED state")
    
    def execute(
        self, 
        function: Callable[..., R],
        fallback: Optional[Callable[..., R]] = None, 
        *args: Any,
        **kwargs: Any
    ) -> R:
        """
        Execute function with circuit breaker protection.
        
        Args:
            function: The function to execute
            fallback: Optional fallback function to call when circuit is open
            args: Positional arguments for the function
            kwargs: Keyword arguments for the function
            
        Returns:
            Result of function or fallback
            
        Raises:
            CircuitOpenError: When circuit is open and no fallback is provided
            CircuitBreakerError: For other circuit breaker errors
        """
        self.total_calls += 1
        
        # Check if circuit is open
        if self.state == CircuitState.OPEN:
            if time.time() - self.last_failure_time > self.recovery_timeout:
                # Recovery timeout reached, move to half-open
                self._change_state(CircuitState.HALF_OPEN)
            else:
                # Circuit still open, short circuit the request
                self.short_circuited_calls += 1
                return self._handle_open_circuit(fallback, *args, **kwargs)
        
        # Check if we've reached the maximum half-open calls
        if self.state == CircuitState.HALF_OPEN:
            if self.half_open_calls >= self.half_open_max_calls:
                # Too many half-open calls, short circuit
                self.short_circuited_calls += 1
                return self._handle_open_circuit(fallback, *args, **kwargs)
            
            self.half_open_calls += 1
        
        # Execute the function
        try:
            result = function(*args, **kwargs)
            
            # Success - if half-open, close the circuit
            self.successful_calls += 1
            if self.state == CircuitState.HALF_OPEN:
                self.reset()
            
            return result
            
        except Exception as e:
            logger.error(f"Circuit '{self.name}' operation failed: {str(e)}")
            self.failed_calls += 1
            self.record_failure()
            return self._handle_failure(fallback, *args, exception=e, **kwargs)
    
    def record_failure(self) -> None:
        """Record a failure and update circuit state if necessary."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        # If closed and threshold reached, open the circuit
        if (self.state == CircuitState.CLOSED and 
            self.failure_count >= self.failure_threshold):
            self._change_state(CircuitState.OPEN)
        
        # If half-open and failure occurs, open the circuit
        if self.state == CircuitState.HALF_OPEN:
            self._change_state(CircuitState.OPEN)
            self.half_open_calls = 0
    
    def reset(self) -> None:
        """Reset the circuit breaker to closed state."""
        self.failure_count = 0
        self._change_state(CircuitState.CLOSED)
        self.half_open_calls = 0
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get current metrics for the circuit breaker.
        
        Returns:
            Dictionary with circuit breaker metrics
        """
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "total_calls": self.total_calls,
            "successful_calls": self.successful_calls,
            "failed_calls": self.failed_calls,
            "short_circuited_calls": self.short_circuited_calls,
            "time_in_current_state": time.time() - self.last_state_change_time
        }
    
    def _change_state(self, new_state: CircuitState) -> None:
        """
        Change the circuit state with logging.
        
        Args:
            new_state: New state to change to
        """
        old_state = self.state
        self.state = new_state
        self.last_state_change_time = time.time()
        
        if old_state != new_state:
            logger.info(f"Circuit '{self.name}' state changed from {old_state.value} to {new_state.value}")
    
    def _handle_open_circuit(
        self, 
        fallback: Optional[Callable[..., R]],
        *args: Any,
        **kwargs: Any
    ) -> R:
        """
        Handle request when circuit is open.
        
        Args:
            fallback: Optional fallback function
            args: Positional arguments
            kwargs: Keyword arguments
            
        Returns:
            Result of fallback function
            
        Raises:
            CircuitOpenError: When no fallback is provided
        """
        logger.info(f"Circuit '{self.name}' is OPEN - short-circuiting request")
        if fallback:
            return fallback(*args, **kwargs)
        raise CircuitOpenError(f"Circuit '{self.name}' is OPEN")
    
    def _handle_failure(
        self, 
        fallback: Optional[Callable[..., R]], 
        *args: Any, 
        exception: Optional[Exception] = None, 
        **kwargs: Any
    ) -> R:
        """
        Handle function failure.
        
        Args:
            fallback: Optional fallback function
            args: Positional arguments
            exception: Original exception raised
            kwargs: Keyword arguments
            
        Returns:
            Result of fallback function
            
        Raises:
            Original exception or CircuitBreakerError
        """
        if fallback:
            return fallback(*args, **kwargs)
        if exception:
            raise exception
        raise CircuitBreakerError(f"Operation failed in circuit '{self.name}'")


def with_circuit_breaker(
    circuit: CircuitBreaker,
    fallback: Optional[Callable[..., R]] = None
) -> Callable[[Callable[..., R]], Callable[..., R]]:
    """
    Decorator to wrap a function with circuit breaker protection.
    
    Args:
        circuit: The circuit breaker to use
        fallback: Optional fallback function to use when circuit is open
        
    Returns:
        Decorated function
    
    Example:
        @with_circuit_breaker(my_circuit, fallback=my_fallback)
        def my_function():
            # potentially failing operation
            pass
    """
    def decorator(function: Callable[..., R]) -> Callable[..., R]:
        def wrapper(*args: Any, **kwargs: Any) -> R:
            return circuit.execute(function, fallback, *args, **kwargs)
        return wrapper
    return decorator 