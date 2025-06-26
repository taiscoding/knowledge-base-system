#!/usr/bin/env python3
"""
Benchmark tests for privacy components.
"""

import pytest
from knowledge_base.privacy.smart_anonymization import PrivacyEngine
from knowledge_base.privacy.session_manager import PrivacySessionManager

# Sample text with varying sizes and sensitive information density
SMALL_TEXT = """
Hi John Smith,

I wanted to follow up on our meeting about Project Phoenix.
Please call me at 555-123-4567 or email john.smith@example.com
when you have time.

Best regards,
Sarah Johnson
"""

MEDIUM_TEXT = """
MEETING NOTES: Project Phoenix Update (June 23, 2025)

Attendees:
- John Smith (Project Lead)
- Sarah Johnson (Engineering)
- Michael Brown (Design)
- Emily Davis (Marketing)

Contact Information:
- John: john.smith@example.com, 555-123-4567
- Sarah: sarah.johnson@example.com, 555-234-5678
- Michael: michael.brown@example.com, 555-345-6789
- Emily: emily.davis@example.com, 555-456-7890

Location: 123 Main Street, Suite 400, Anytown

Key Discussion Items:
1. Timeline update for Project Phoenix
2. Integration with Project Mercury (led by Robert Wilson)
3. Budget allocation for Q3 2025
4. Marketing strategy for September launch

Action Items:
- John to connect with Robert about integration timeline
- Sarah to finalize technical specifications by July 5th
- Michael to deliver updated mockups by June 30th
- Emily to draft press release by July 10th

Next meeting scheduled for July 7th, 2025 at 10:00 AM.
"""

# Generate a larger text for more intensive benchmarking
LARGE_TEXT = MEDIUM_TEXT * 10


@pytest.fixture
def privacy_engine():
    """Fixture providing a PrivacyEngine instance for benchmarking."""
    return PrivacyEngine()


@pytest.fixture
def session_manager():
    """Fixture providing a PrivacySessionManager instance for benchmarking."""
    import tempfile
    with tempfile.TemporaryDirectory() as temp_dir:
        yield PrivacySessionManager(storage_dir=temp_dir)


class TestPrivacyBenchmarks:
    """Benchmarks for privacy components."""

    def test_privacy_engine_initialization(self, benchmark):
        """Benchmark PrivacyEngine initialization."""
        benchmark(PrivacyEngine)

    def test_deidentify_small_text(self, benchmark, privacy_engine):
        """Benchmark deidentification of small text."""
        session_id = privacy_engine.create_session()
        benchmark(privacy_engine.deidentify, SMALL_TEXT, session_id)

    def test_deidentify_medium_text(self, benchmark, privacy_engine):
        """Benchmark deidentification of medium text."""
        session_id = privacy_engine.create_session()
        benchmark(privacy_engine.deidentify, MEDIUM_TEXT, session_id)

    def test_deidentify_large_text(self, benchmark, privacy_engine):
        """Benchmark deidentification of large text."""
        session_id = privacy_engine.create_session()
        benchmark(privacy_engine.deidentify, LARGE_TEXT, session_id)
    
    def test_reconstruct_performance(self, benchmark, privacy_engine):
        """Benchmark reconstruction of tokenized text."""
        session_id = privacy_engine.create_session()
        result = privacy_engine.deidentify(MEDIUM_TEXT, session_id)
        benchmark(privacy_engine.reconstruct, result.text, session_id)
    
    def test_token_consistency_performance(self, benchmark, privacy_engine):
        """Benchmark token consistency across multiple calls."""
        session_id = privacy_engine.create_session()
        privacy_engine.deidentify(SMALL_TEXT, session_id)
        
        # Benchmark subsequent call with overlapping entities
        def subsequent_deidentify():
            return privacy_engine.deidentify(
                "John Smith and Sarah Johnson discussed Project Phoenix.", 
                session_id
            )
        
        benchmark(subsequent_deidentify)
    
    def test_session_creation_performance(self, benchmark, session_manager):
        """Benchmark session creation."""
        benchmark(session_manager.create_session)
    
    def test_session_update_performance(self, benchmark, session_manager):
        """Benchmark session update."""
        session_id = session_manager.create_session()
        
        # Create some token mappings to update
        token_mappings = {
            "PERSON_001": "John Smith",
            "PERSON_002": "Sarah Johnson",
            "PROJECT_001": "Project Phoenix",
            "EMAIL_001": "john.smith@example.com",
            "PHONE_001": "555-123-4567"
        }
        
        def update_session():
            return session_manager.update_session(
                session_id,
                {"token_mappings": token_mappings}
            )
        
        benchmark(update_session)


if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 