#!/usr/bin/env python3
"""
Differential Privacy Module for Knowledge Base System.

This module provides differential privacy mechanisms including:
1. Privacy budget management
2. Noise injection for privacy-preserving queries
3. Privacy-preserving aggregation functions
"""

import os
import json
import math
import random
import logging
import numpy as np
from enum import Enum
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Tuple, Set, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

class NoiseDistribution(str, Enum):
    """Noise distribution types for differential privacy."""
    LAPLACE = "laplace"        # Laplace distribution
    GAUSSIAN = "gaussian"      # Gaussian (normal) distribution
    GEOMETRIC = "geometric"    # Geometric distribution


@dataclass
class PrivacyBudget:
    """Privacy budget for differential privacy operations."""
    budget_id: str
    total_epsilon: float
    remaining_epsilon: float
    created_at: str
    last_updated: str
    query_history: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert budget to dictionary."""
        return {
            "budget_id": self.budget_id,
            "total_epsilon": self.total_epsilon,
            "remaining_epsilon": self.remaining_epsilon,
            "created_at": self.created_at,
            "last_updated": self.last_updated,
            "query_history": self.query_history,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PrivacyBudget':
        """Create budget from dictionary."""
        return cls(
            budget_id=data["budget_id"],
            total_epsilon=data["total_epsilon"],
            remaining_epsilon=data["remaining_epsilon"],
            created_at=data["created_at"],
            last_updated=data["last_updated"],
            query_history=data.get("query_history", []),
            metadata=data.get("metadata", {})
        )


class BudgetExhaustedException(Exception):
    """Exception raised when privacy budget is exhausted."""
    pass


class PrivacyBudgetManager:
    """
    Manages privacy budgets for differential privacy.
    
    This class provides:
    1. Privacy budget allocation and tracking
    2. Budget consumption recording
    3. Budget enforcement
    """
    
    def __init__(self, storage_dir: str = None, default_epsilon: float = 1.0):
        """
        Initialize the privacy budget manager.
        
        Args:
            storage_dir: Directory for storing budget data
            default_epsilon: Default epsilon value for new budgets
        """
        # Set up storage location
        if storage_dir:
            self.storage_dir = Path(storage_dir)
        else:
            self.storage_dir = Path.home() / ".kb_privacy" / "budgets"
            
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Default configuration
        self.default_epsilon = default_epsilon
        
        # Active budgets
        self.budgets: Dict[str, PrivacyBudget] = {}
        
        # Load existing budgets
        self._load_budgets()
    
    def _load_budgets(self) -> None:
        """Load all privacy budgets from storage."""
        try:
            for budget_file in self.storage_dir.glob("budget_*.json"):
                try:
                    with open(budget_file, 'r') as f:
                        budget_data = json.load(f)
                        budget = PrivacyBudget.from_dict(budget_data)
                        self.budgets[budget.budget_id] = budget
                        logger.debug(f"Loaded privacy budget: {budget.budget_id}")
                except Exception as e:
                    logger.error(f"Error loading budget from {budget_file}: {e}")
        except Exception as e:
            logger.error(f"Error loading privacy budgets: {e}")
    
    def create_budget(self, 
                     total_epsilon: float = None,
                     metadata: Dict[str, Any] = None) -> PrivacyBudget:
        """
        Create a new privacy budget.
        
        Args:
            total_epsilon: Total epsilon value for this budget
            metadata: Optional metadata for the budget
            
        Returns:
            New privacy budget
        """
        import uuid
        
        # Generate unique budget ID
        budget_id = f"budget-{uuid.uuid4().hex[:8]}"
        
        # Use default epsilon if none provided
        if total_epsilon is None:
            total_epsilon = self.default_epsilon
            
        # Create timestamp
        now = datetime.now().isoformat()
        
        # Create budget
        budget = PrivacyBudget(
            budget_id=budget_id,
            total_epsilon=total_epsilon,
            remaining_epsilon=total_epsilon,
            created_at=now,
            last_updated=now,
            query_history=[],
            metadata=metadata or {}
        )
        
        # Store budget
        self.budgets[budget_id] = budget
        self._save_budget(budget)
        
        return budget
    
    def _save_budget(self, budget: PrivacyBudget) -> None:
        """
        Save a privacy budget to storage.
        
        Args:
            budget: Privacy budget to save
        """
        budget_path = self.storage_dir / f"budget_{budget.budget_id}.json"
        
        try:
            with open(budget_path, 'w') as f:
                json.dump(budget.to_dict(), f, indent=2)
        except Exception as e:
            logger.error(f"Error saving budget {budget.budget_id}: {e}")
    
    def get_budget(self, budget_id: str) -> Optional[PrivacyBudget]:
        """
        Get a privacy budget by ID.
        
        Args:
            budget_id: Budget ID
            
        Returns:
            Privacy budget or None if not found
        """
        return self.budgets.get(budget_id)
    
    def consume_budget(self, 
                      budget_id: str, 
                      epsilon: float,
                      query_type: str,
                      query_details: Dict[str, Any] = None) -> float:
        """
        Consume part of a privacy budget.
        
        Args:
            budget_id: Budget ID
            epsilon: Epsilon amount to consume
            query_type: Type of query consuming budget
            query_details: Optional query details
            
        Returns:
            Remaining epsilon
            
        Raises:
            BudgetExhaustedException: If budget is insufficient
        """
        # Get budget
        budget = self.get_budget(budget_id)
        if not budget:
            raise ValueError(f"Budget not found: {budget_id}")
            
        # Check if sufficient budget remains
        if budget.remaining_epsilon < epsilon:
            raise BudgetExhaustedException(
                f"Privacy budget exhausted for {budget_id}. "
                f"Requested: {epsilon}, Remaining: {budget.remaining_epsilon}"
            )
        
        # Update remaining budget
        budget.remaining_epsilon -= epsilon
        budget.last_updated = datetime.now().isoformat()
        
        # Record query
        query_record = {
            "timestamp": datetime.now().isoformat(),
            "epsilon_used": epsilon,
            "query_type": query_type,
            "remaining_after": budget.remaining_epsilon,
            "details": query_details or {}
        }
        budget.query_history.append(query_record)
        
        # Save updated budget
        self._save_budget(budget)
        
        return budget.remaining_epsilon
    
    def reset_budget(self, budget_id: str) -> Optional[PrivacyBudget]:
        """
        Reset a privacy budget to its original total.
        
        Args:
            budget_id: Budget ID
            
        Returns:
            Updated privacy budget or None if not found
        """
        budget = self.get_budget(budget_id)
        if not budget:
            return None
            
        # Reset to original total
        budget.remaining_epsilon = budget.total_epsilon
        budget.last_updated = datetime.now().isoformat()
        
        # Add reset record to history
        query_record = {
            "timestamp": datetime.now().isoformat(),
            "action": "reset",
            "previous_remaining": 0,
            "new_remaining": budget.total_epsilon
        }
        budget.query_history.append(query_record)
        
        # Save updated budget
        self._save_budget(budget)
        
        return budget


class DifferentialPrivacyMechanism:
    """
    Implementation of differential privacy mechanisms.
    
    This class provides:
    1. Noise addition methods
    2. Privacy-preserving query mechanisms
    3. Utility evaluation tools
    """
    
    def __init__(self, budget_manager: PrivacyBudgetManager = None):
        """
        Initialize the differential privacy mechanism.
        
        Args:
            budget_manager: Optional budget manager for tracking
        """
        self.budget_manager = budget_manager
    
    def add_laplace_noise(self, 
                         value: float, 
                         sensitivity: float, 
                         epsilon: float) -> float:
        """
        Add Laplace noise to a numeric value.
        
        Args:
            value: Original value
            sensitivity: Sensitivity of the query
            epsilon: Privacy parameter (smaller = more privacy)
            
        Returns:
            Value with Laplace noise added
        """
        # Calculate scale parameter
        scale = sensitivity / epsilon
        
        # Generate Laplace noise
        noise = np.random.laplace(0, scale)
        
        # Add noise to value
        return value + noise
    
    def add_gaussian_noise(self, 
                          value: float, 
                          sensitivity: float, 
                          epsilon: float, 
                          delta: float) -> float:
        """
        Add Gaussian noise to a numeric value.
        
        Args:
            value: Original value
            sensitivity: Sensitivity of the query
            epsilon: Privacy parameter (smaller = more privacy)
            delta: Probability parameter (smaller = stricter guarantee)
            
        Returns:
            Value with Gaussian noise added
        """
        # Calculate standard deviation using analytic Gaussian mechanism
        # (see: https://arxiv.org/abs/1805.06530)
        c = math.sqrt(2 * math.log(1.25 / delta))
        sigma = c * sensitivity / epsilon
        
        # Generate Gaussian noise
        noise = np.random.normal(0, sigma)
        
        # Add noise to value
        return value + noise
    
    def add_geometric_noise(self,
                          value: int,
                          sensitivity: int,
                          epsilon: float) -> int:
        """
        Add geometric noise to an integer value.
        
        Args:
            value: Original integer value
            sensitivity: Sensitivity of the query (integer)
            epsilon: Privacy parameter (smaller = more privacy)
            
        Returns:
            Integer with geometric noise added
        """
        # Calculate parameter for geometric distribution
        alpha = math.exp(-epsilon / sensitivity)
        p = 1 - alpha
        
        # Generate two-sided geometric noise
        noise_magnitude = np.random.geometric(p) - 1
        noise = noise_magnitude if random.random() > 0.5 else -noise_magnitude
        
        # Add noise to value
        return value + noise
    
    def privatize_count(self, 
                       count: int, 
                       epsilon: float,
                       sensitivity: int = 1,
                       budget_id: Optional[str] = None) -> int:
        """
        Apply differential privacy to a count query.
        
        Args:
            count: Original count value
            epsilon: Privacy parameter
            sensitivity: Sensitivity (defaults to 1 for count queries)
            budget_id: Optional budget ID for tracking
            
        Returns:
            Privacy-preserving count
            
        Raises:
            BudgetExhaustedException: If budget is insufficient
        """
        # Consume budget if tracking
        if budget_id and self.budget_manager:
            self.budget_manager.consume_budget(
                budget_id=budget_id,
                epsilon=epsilon,
                query_type="count",
                query_details={"sensitivity": sensitivity}
            )
        
        # Add Laplace noise and round to nearest integer
        noisy_count = self.add_laplace_noise(count, sensitivity, epsilon)
        
        # Count can't be negative
        return max(0, round(noisy_count))
    
    def privatize_sum(self, 
                     sum_value: float, 
                     epsilon: float,
                     sensitivity: float,
                     budget_id: Optional[str] = None) -> float:
        """
        Apply differential privacy to a sum query.
        
        Args:
            sum_value: Original sum value
            epsilon: Privacy parameter
            sensitivity: Sensitivity of the sum query
            budget_id: Optional budget ID for tracking
            
        Returns:
            Privacy-preserving sum
            
        Raises:
            BudgetExhaustedException: If budget is insufficient
        """
        # Consume budget if tracking
        if budget_id and self.budget_manager:
            self.budget_manager.consume_budget(
                budget_id=budget_id,
                epsilon=epsilon,
                query_type="sum",
                query_details={"sensitivity": sensitivity}
            )
        
        # Add Laplace noise
        return self.add_laplace_noise(sum_value, sensitivity, epsilon)
    
    def privatize_average(self, 
                         sum_value: float, 
                         count: int,
                         epsilon: float,
                         sensitivity: float,
                         budget_id: Optional[str] = None) -> float:
        """
        Apply differential privacy to an average query.
        
        Args:
            sum_value: Original sum value
            count: Count of values
            epsilon: Privacy parameter
            sensitivity: Sensitivity of the sum
            budget_id: Optional budget ID for tracking
            
        Returns:
            Privacy-preserving average
            
        Raises:
            BudgetExhaustedException: If budget is insufficient
            ValueError: If count is zero
        """
        if count == 0:
            raise ValueError("Cannot compute average with zero count")
            
        # Split epsilon between sum and count (equal allocation)
        epsilon_sum = epsilon / 2
        epsilon_count = epsilon / 2
        
        # Consume budget if tracking
        if budget_id and self.budget_manager:
            self.budget_manager.consume_budget(
                budget_id=budget_id,
                epsilon=epsilon,
                query_type="average",
                query_details={
                    "sensitivity": sensitivity,
                    "epsilon_sum": epsilon_sum,
                    "epsilon_count": epsilon_count
                }
            )
        
        # Add noise to sum and count
        noisy_sum = self.add_laplace_noise(sum_value, sensitivity, epsilon_sum)
        noisy_count = self.add_laplace_noise(count, 1, epsilon_count)
        
        # Ensure count is at least 1 to avoid division by zero
        noisy_count = max(1, noisy_count)
        
        # Calculate noisy average
        return noisy_sum / noisy_count
    
    def privatize_histogram(self, 
                          counts: Dict[str, int], 
                          epsilon: float,
                          budget_id: Optional[str] = None) -> Dict[str, int]:
        """
        Apply differential privacy to a histogram.
        
        Args:
            counts: Dictionary of category to count
            epsilon: Privacy parameter
            budget_id: Optional budget ID for tracking
            
        Returns:
            Privacy-preserving histogram
            
        Raises:
            BudgetExhaustedException: If budget is insufficient
        """
        # Consume budget if tracking
        if budget_id and self.budget_manager:
            self.budget_manager.consume_budget(
                budget_id=budget_id,
                epsilon=epsilon,
                query_type="histogram",
                query_details={"categories": len(counts)}
            )
        
        # Sensitivity is 1 for a standard histogram (one individual only affects one bin)
        sensitivity = 1
        
        # Add noise to each bin
        noisy_counts = {}
        for category, count in counts.items():
            noisy_count = self.add_laplace_noise(count, sensitivity, epsilon)
            # Counts should be non-negative integers
            noisy_counts[category] = max(0, round(noisy_count))
        
        return noisy_counts
    
    def privatize_top_k(self, 
                       counts: Dict[str, int],
                       k: int,
                       epsilon: float,
                       budget_id: Optional[str] = None) -> List[Tuple[str, int]]:
        """
        Apply differential privacy to a top-k query.
        
        Args:
            counts: Dictionary of item to count
            k: Number of top items to return
            epsilon: Privacy parameter
            budget_id: Optional budget ID for tracking
            
        Returns:
            Top k items with noisy counts
            
        Raises:
            BudgetExhaustedException: If budget is insufficient
        """
        # Consume budget if tracking
        if budget_id and self.budget_manager:
            self.budget_manager.consume_budget(
                budget_id=budget_id,
                epsilon=epsilon,
                query_type="top_k",
                query_details={"k": k, "total_items": len(counts)}
            )
        
        # Add noise to all counts
        sensitivity = 1
        noisy_counts = {}
        for item, count in counts.items():
            noisy_counts[item] = self.add_laplace_noise(count, sensitivity, epsilon)
        
        # Sort by noisy count and take top k
        top_items = sorted(noisy_counts.items(), key=lambda x: x[1], reverse=True)[:k]
        
        # Round counts to integers
        return [(item, max(0, round(count))) for item, count in top_items]


class PrivacyPreservingAnalytics:
    """
    Privacy-preserving analytics with differential privacy.
    
    This class provides:
    1. Private counting and statistics
    2. Privacy-aware aggregation
    3. Privacy-preserving recommendations
    """
    
    def __init__(self, budget_manager: Optional[PrivacyBudgetManager] = None):
        """
        Initialize privacy-preserving analytics.
        
        Args:
            budget_manager: Optional budget manager for tracking
        """
        if budget_manager:
            self.budget_manager = budget_manager
        else:
            self.budget_manager = PrivacyBudgetManager()
            
        # Create DP mechanism
        self.dp_mechanism = DifferentialPrivacyMechanism(self.budget_manager)
    
    def create_analytics_budget(self, 
                              total_epsilon: float = 1.0,
                              purpose: str = "analytics") -> str:
        """
        Create a budget for analytics operations.
        
        Args:
            total_epsilon: Total privacy budget
            purpose: Purpose of this budget
            
        Returns:
            Budget ID
        """
        budget = self.budget_manager.create_budget(
            total_epsilon=total_epsilon,
            metadata={"purpose": purpose}
        )
        return budget.budget_id
    
    def count_with_privacy(self, 
                          count: int,
                          budget_id: str,
                          epsilon: float = 0.1) -> int:
        """
        Get a privacy-preserving count.
        
        Args:
            count: Original count
            budget_id: Budget ID
            epsilon: Privacy parameter for this operation
            
        Returns:
            Privacy-preserving count
            
        Raises:
            BudgetExhaustedException: If budget is insufficient
        """
        return self.dp_mechanism.privatize_count(
            count=count,
            epsilon=epsilon,
            budget_id=budget_id
        )
    
    def get_private_stats(self, 
                         values: List[float],
                         budget_id: str,
                         epsilon: float = 0.3,
                         sensitivity: Optional[float] = None) -> Dict[str, float]:
        """
        Get privacy-preserving statistics for a list of values.
        
        Args:
            values: List of numeric values
            budget_id: Budget ID
            epsilon: Privacy parameter for this operation
            sensitivity: Sensitivity of the values (max - min if not provided)
            
        Returns:
            Dictionary of statistics
            
        Raises:
            BudgetExhaustedException: If budget is insufficient
        """
        if not values:
            return {
                "count": 0,
                "sum": 0,
                "avg": 0,
                "min": 0,
                "max": 0
            }
        
        # Calculate sensitivity if not provided
        if sensitivity is None:
            sensitivity = max(values) - min(values)
            if sensitivity <= 0:
                sensitivity = 1.0  # Default if all values are the same
        
        # Count number of values (without noise)
        count = len(values)
        
        # Calculate actual statistics
        actual_sum = sum(values)
        actual_avg = actual_sum / count if count > 0 else 0
        
        # Allocate privacy budget
        # 50% for count/sum/avg, 25% for min, 25% for max
        epsilon_count_sum_avg = epsilon * 0.5
        epsilon_min = epsilon * 0.25
        epsilon_max = epsilon * 0.25
        
        # Get private statistics
        # Use privatize_average for better accuracy than separate sum and count
        private_avg = self.dp_mechanism.privatize_average(
            sum_value=actual_sum,
            count=count,
            epsilon=epsilon_count_sum_avg,
            sensitivity=sensitivity,
            budget_id=budget_id
        )
        
        # Min and max need special handling for differential privacy
        private_min = min(values) + self.dp_mechanism.add_laplace_noise(
            value=0,
            sensitivity=sensitivity,
            epsilon=epsilon_min
        )
        
        private_max = max(values) + self.dp_mechanism.add_laplace_noise(
            value=0,
            sensitivity=sensitivity,
            epsilon=epsilon_max
        )
        
        # Ensure min <= max
        if private_min > private_max:
            middle = (private_min + private_max) / 2
            private_min = middle - abs(private_min - private_max) / 4
            private_max = middle + abs(private_min - private_max) / 4
        
        return {
            "count": count,  # Original count is often revealed in DP
            "avg": private_avg,
            "min": private_min,
            "max": private_max,
            "noisy": True
        }
    
    def get_private_histogram(self,
                            data: List[str],
                            categories: Optional[List[str]] = None,
                            budget_id: str = None,
                            epsilon: float = 0.2) -> Dict[str, int]:
        """
        Get a privacy-preserving histogram.
        
        Args:
            data: List of categorical values
            categories: Optional list of all possible categories
            budget_id: Budget ID
            epsilon: Privacy parameter for this operation
            
        Returns:
            Dictionary of category to noisy count
            
        Raises:
            BudgetExhaustedException: If budget is insufficient
        """
        # Count occurrences of each category
        counts = {}
        
        # Initialize counts for all categories if provided
        if categories:
            for category in categories:
                counts[category] = 0
        
        # Count data
        for item in data:
            if item in counts:
                counts[item] += 1
            else:
                counts[item] = 1
        
        # Apply differential privacy
        return self.dp_mechanism.privatize_histogram(
            counts=counts,
            epsilon=epsilon,
            budget_id=budget_id
        )
    
    def get_private_top_k(self,
                        counts: Dict[str, int],
                        k: int,
                        budget_id: str,
                        epsilon: float = 0.3) -> List[Tuple[str, int]]:
        """
        Get privacy-preserving top-k results.
        
        Args:
            counts: Dictionary of item to count
            k: Number of top items to return
            budget_id: Budget ID
            epsilon: Privacy parameter for this operation
            
        Returns:
            List of (item, count) tuples for top k items
            
        Raises:
            BudgetExhaustedException: If budget is insufficient
        """
        return self.dp_mechanism.privatize_top_k(
            counts=counts,
            k=k,
            epsilon=epsilon,
            budget_id=budget_id
        )
    
    def private_keyword_analysis(self,
                               documents: List[str],
                               budget_id: str,
                               top_k: int = 10,
                               epsilon: float = 0.5) -> List[Tuple[str, int]]:
        """
        Perform privacy-preserving keyword analysis on documents.
        
        Args:
            documents: List of text documents
            budget_id: Budget ID
            top_k: Number of top keywords to return
            epsilon: Privacy parameter for this operation
            
        Returns:
            List of (keyword, count) tuples
            
        Raises:
            BudgetExhaustedException: If budget is insufficient
        """
        # Simple tokenization and counting
        word_counts = {}
        
        for doc in documents:
            # Simple tokenization (split by whitespace and remove punctuation)
            words = doc.lower().split()
            words = [word.strip('.,!?:;()[]{}"\'-') for word in words]
            
            # Count unique words in this document (ignoring duplicates)
            unique_words = set(words)
            for word in unique_words:
                if word and len(word) > 2:  # Skip very short words
                    if word in word_counts:
                        word_counts[word] += 1
                    else:
                        word_counts[word] = 1
        
        # Get private top keywords
        return self.get_private_top_k(
            counts=word_counts,
            k=top_k,
            budget_id=budget_id,
            epsilon=epsilon
        )
    
    def private_recommendations(self,
                              item_interactions: Dict[str, int],
                              num_recommendations: int = 5,
                              budget_id: str = None,
                              epsilon: float = 0.4) -> List[Tuple[str, float]]:
        """
        Generate privacy-preserving content recommendations.
        
        Args:
            item_interactions: Dictionary of item ID to interaction count
            num_recommendations: Number of recommendations to return
            budget_id: Budget ID
            epsilon: Privacy parameter for this operation
            
        Returns:
            List of (item ID, score) recommendations
            
        Raises:
            BudgetExhaustedException: If budget is insufficient
        """
        # Apply differential privacy to interaction counts
        private_counts = self.dp_mechanism.privatize_histogram(
            counts=item_interactions,
            epsilon=epsilon/2,  # Split budget between counts and final ranking
            budget_id=budget_id
        )
        
        # Create recommendation scores (could be more sophisticated in practice)
        scores = {}
        for item, count in private_counts.items():
            # Generate a slightly noisy score based on the private count
            base_score = count / max(private_counts.values()) if private_counts else 0
            
            # Add a small amount of Laplace noise to the score
            score = self.dp_mechanism.add_laplace_noise(
                value=base_score,
                sensitivity=1.0/max(sum(private_counts.values()), 1),  # Normalized sensitivity
                epsilon=epsilon/2  # Use the second half of the budget
            )
            scores[item] = max(0, score)  # Ensure non-negative
        
        # Get top recommendations
        recommendations = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:num_recommendations]
        
        return recommendations 