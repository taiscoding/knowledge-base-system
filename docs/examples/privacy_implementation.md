# Privacy Implementation Details

This document provides technical details about the pattern detection and entity relationship implementation in the Knowledge Base System.

## Pattern Detection System

The Privacy Engine uses a sophisticated pattern detection system to identify and tokenize various types of sensitive information. This system is implemented in the `PrivacyEngine._initialize_detection_patterns()` and `PrivacyEngine._process_patterns()` methods.

### Pattern Types

The following pattern types are implemented:

#### 1. Person Names

```python
# Person name detection patterns
self.name_patterns = [
    r'\b(?:[A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b',  # First Last, First Middle Last
    r'\b(?:Dr\.|Mr\.|Mrs\.|Ms\.|Prof\.)\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\b',  # Titles with names
    r'\b(?:[A-Z][a-z]+(?:-[A-Z][a-z]+))\b',  # Hyphenated names
    r'\b(?:[A-Z][a-z]+\'[A-Z]?[a-z]+)\b',  # Names with apostrophes
    r'\bHi\s+([A-Z][a-z]+\s+[A-Z][a-z]+)\b',  # Names after greeting
    r'\bregards,\s*\n\s*([A-Z][a-z]+\s+[A-Z][a-z]+)\b',  # Names in signature
]
```

These patterns match:
- Standard first/last name combinations (John Smith)
- Names with middle names (John Edward Smith)
- Names with titles (Dr. Smith, Mrs. Johnson)
- Hyphenated names (Mary-Jane Williams)
- Names with apostrophes (O'Reilly, D'Angelo)
- Names in greetings (Hi John Smith)
- Names in signatures (regards, Sarah Johnson)

#### 2. Phone Numbers

```python
# Phone number patterns
self.phone_patterns = [
    r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b',  # Standard US phone: 555-555-5555
    r'\(\d{3}\)\s*\d{3}[-.\s]?\d{4}\b',     # Parentheses format: (555) 555-5555
    r'\+\d{1,3}\s*\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b',  # International: +1 555-555-5555
    r'\b\d{10}\b'  # Simple 10-digit number
]
```

These patterns match:
- Standard formats (555-123-4567, 555.123.4567, 555 123 4567)
- Parenthesized formats ((555) 123-4567)
- International formats (+1 555-123-4567)
- Plain digits (5551234567)

#### 3. Email Addresses

```python
# Email patterns
self.email_patterns = [
    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'  # standard email
]
```

This pattern matches standard email addresses, including those with:
- Special characters in the local part (._%+-)
- Subdomains
- Various TLDs

#### 4. Locations

```python
# Location patterns
self.location_patterns = [
    r'\b\d{1,5}\s+[A-Za-z0-9\s,\.]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Place|Pl|Court|Ct|Way|Terrace|Terr|Circle|Cir|Square|Sq)\b',
    r'\b\d{1,5}\s+[A-Z][a-z]+(?:\s+[A-Z]?[a-z]+)?\s+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Place|Pl|Court|Ct|Way|Terrace|Terr|Circle|Cir|Square|Sq)\b',
    r'\bmeet at\s+(\d{1,5}\s+[A-Z][a-z]+\s+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Place|Pl|Court|Ct|Way))\b',
    r'\b[A-Z][a-z]+(?:town|ville|burg|city|field|shire|port|bridge|haven|dale|wood|ford)\b',
    r'\b(?:New|North|South|East|West|Central)\s+[A-Z][a-zA-Z]+\b'  # Directional city names
]
```

These patterns match:
- Street addresses with various street suffix formats
- Numbered addresses (123 Main Street)
- City names with common suffixes (Newtown, Springfield)
- Directional city names (North Hampton, West Village)
- Contextual location mentions (meet at 123 Oak Street)

#### 5. Projects

```python
# Project patterns
self.project_patterns = [
    r'\b(?:Project|Initiative|Program|Operation)\s+[A-Z][a-zA-Z]+\b',
    r'\b[A-Z][a-zA-Z]+\s+(?:Project|Initiative|Program)\b',
    r'\b(?:Team|Group)\s+[A-Z][a-zA-Z]+\b',
    r'\bmeeting about\s+(Project\s+[A-Z][a-zA-Z]+)\b',
    r'\bworking on\s+(Project\s+[A-Z][a-zA-Z]+)\b'
]
```

These patterns match:
- "Project X" format (Project Phoenix)
- "X Project" format (Phoenix Project)
- Team and group names (Team Alpha)
- Contextual project mentions (meeting about Project Phoenix)

### Pattern Processing

The pattern processing algorithm works in these steps:

1. For each pattern type, iterate through all patterns
2. Find all matches in the text
3. Process matches in reverse order to avoid disrupting text positions
4. For each match:
   - Check if it's already a token (skip if so)
   - Check if we've seen this value before (reuse token if so)
   - Create a new token if needed
   - Replace the text with the token

This ensures consistent tokenization and prevents nested tokenization issues.

## Entity Relationship Detection

Entity relationship detection is implemented in the `PrivacyEngine._update_entity_relationships()` method. This system automatically identifies and tracks relationships between detected entities.

### Relationship Types

The system defines relationships between different entity types:

```python
# Define relationship rules between token types
relationship_rules = {
    "PERSON": {
        "PHONE": "has_phone_number",
        "EMAIL": "has_email",
        "PROJECT": "works_on",
        "LOCATION": "associated_with"
    },
    "PROJECT": {
        "PERSON": "has_member",
        "LOCATION": "located_at"
    },
    "EMAIL": {
        "PERSON": "belongs_to"
    },
    "PHONE": {
        "PERSON": "belongs_to"
    },
    "LOCATION": {
        "PERSON": "associated_with",
        "PROJECT": "hosts"
    }
}
```

### Relationship Detection Methods

The system uses multiple methods to detect relationships:

#### 1. Type-based Relationships

Based on the predefined rules, entities of certain types are automatically related:
- Person entities are linked to their contact methods (phone, email)
- Person entities are linked to projects they're mentioned with
- Locations are linked to both people and projects

#### 2. Content Analysis

The system analyzes the content to find relationships:
- Name parts appearing in email addresses
- Projects mentioned in context with people
- Locations associated with meetings

#### 3. Bidirectional Relationships

All relationships are bidirectional with appropriate relationship types:
- If a person "has_email" an email address, the email "belongs_to" the person
- If a person "works_on" a project, the project "has_member" the person

### Relationship Representation

Relationships are stored in a structured format within the entity_relationships dictionary:

```python
entity_relationships = {
    "PERSON_001": {
        "type": "person",
        "linked_entities": ["EMAIL_001", "PROJECT_001"],
        "relationships": {
            "EMAIL_001": "has_email",
            "PROJECT_001": "works_on"
        }
    },
    "EMAIL_001": {
        "type": "email",
        "linked_entities": ["PERSON_001"],
        "relationships": {
            "PERSON_001": "belongs_to"
        }
    },
    "PROJECT_001": {
        "type": "project",
        "linked_entities": ["PERSON_001"],
        "relationships": {
            "PERSON_001": "has_member"
        }
    }
}
```

## Token Consistency

The system ensures token consistency through multiple mechanisms:

### 1. Session-based Token Mapping

Tokens are consistent within a session, stored in `PrivacySessionManager`:

```python
session = {
    "token_mappings": {
        "PERSON_001": "John Smith",
        "EMAIL_001": "john.smith@example.com"
    }
}
```

### 2. Inverse Mapping

An inverse mapping is maintained for efficient lookup:

```python
inverse_mappings = {
    "John Smith": "PERSON_001",
    "john.smith@example.com": "EMAIL_001"
}
```

### 3. Token Counter Management

Token counters are managed per token type:

```python
token_counter = 1
for token in existing_mappings.keys():
    if token.startswith(token_type):
        try:
            num = int(token.split('_')[1])
            token_counter = max(token_counter, num + 1)
        except (IndexError, ValueError):
            pass
```

## Performance Optimization

The pattern detection system is optimized for performance:

1. **Efficient Regex Patterns**: Carefully constructed to minimize backtracking
2. **Reverse Processing**: Processing matches in reverse order prevents position shifts
3. **Token Caching**: Fast lookup of existing tokens via inverse mapping
4. **Staged Processing**: Entities are processed by type for better organization

## Usage Example

```python
from knowledge_base.privacy import PrivacyEngine

engine = PrivacyEngine()
session_id = engine.create_session()

text = "John Smith is working on Project Phoenix. Contact him at john.smith@example.com or 555-123-4567."
result = engine.deidentify(text, session_id)

print(result.text)
# "[PERSON_001] is working on [PROJECT_001]. Contact him at [EMAIL_001] or [PHONE_001]."

print(result.token_map)
# {"PERSON_001": "John Smith", "PROJECT_001": "Project Phoenix", "EMAIL_001": "john.smith@example.com", "PHONE_001": "555-123-4567"}

print(result.entity_relationships)
# Complex structure with relationship information

# Reconstruct the original text
original = engine.reconstruct(result.text, session_id)
print(original)
# "John Smith is working on Project Phoenix. Contact him at john.smith@example.com or 555-123-4567."
``` 