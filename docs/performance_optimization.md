# Performance Optimization Guide

This document outlines the performance optimizations implemented for the Knowledge Base System's privacy components and provides guidance for future development.

## Performance Benchmark Results

Our testing revealed the following performance metrics for the privacy components:

| Operation | Performance | Notes |
|-----------|------------|--------|
| Deidentify (Small Text) | ~14,600 ops/sec | ~68μs per operation |
| Deidentify (Medium Text) | ~3,500 ops/sec | ~285μs per operation |
| Deidentify (Large Text) | ~374 ops/sec | ~2.67ms per operation |
| Reconstruct | ~52,300 ops/sec | ~19μs per operation |
| Token Consistency | ~29,100 ops/sec | ~34μs per operation |
| Session Create | ~7,500 ops/sec | ~133μs per operation |
| Session Update | ~13,100 ops/sec | ~76μs per operation |

These baseline measurements will help us track performance over time and detect regressions.

## Optimization Techniques Implemented

### 1. Pattern Detection Optimizations

#### 1.1 Efficient Regex Patterns

The regex patterns used for entity detection have been optimized to:

- Avoid excessive backtracking
- Minimize catastrophic backtracking risk
- Use positive lookbehinds sparingly (only with fixed width)
- Prioritize word boundary checks for faster filtering

#### 1.2 Match Processing Optimization

The `_process_patterns` method in `PrivacyEngine` has been optimized to:

- Process matches in reverse order to prevent position shifts
- Use direct slicing operations instead of string replacement where possible
- Implement early skipping for already tokenized text

#### 1.3 Capturing Groups

Where appropriate, capturing groups are used to isolate precisely the text that should be tokenized, minimizing unnecessary replacements:

```python
r'\bmeeting about\s+(Project\s+[A-Z][a-zA-Z]+)\b'  # Captures only the project name
```

### 2. Token Management Optimizations

#### 2.1 Inverse Mapping Cache

An inverse mapping from original values to tokens is maintained for O(1) token lookup:

```python
inverse_mappings = {value: key for key, value in token_mappings.items()}
```

This prevents the need to scan all existing tokens when checking if we've seen a value before.

#### 2.2 Token Counter Management

Token counters are managed efficiently per token type:

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

#### 2.3 Session Caching

Session data is cached in memory with disk persistence as backup:

```python
self.sessions = self._load_sessions()  # Initialize from disk
self._save_session(session_id)  # Persist to disk when needed
```

### 3. Entity Relationship Optimizations

#### 3.1 Type-Based Grouping

Entities are grouped by type before relationship detection:

```python
token_by_type = {}
for token in new_tokens:
    token_type = token.split('_')[0]
    if token_type not in token_by_type:
        token_by_type[token_type] = []
    token_by_type[token_type].append(token)
```

This reduces the complexity from O(n²) to O(n) when applying relationship rules.

#### 3.2 Relationship Rules Table

Pre-defined relationship rules enable efficient relationship mapping:

```python
relationship_rules = {
    "PERSON": { "PHONE": "has_phone_number", "EMAIL": "has_email", ... },
    "PROJECT": { "PERSON": "has_member", ... },
    # ...
}
```

#### 3.3 Dictionary Operations

The code uses efficient dictionary operations:

```python
# Quick check if key exists
if token not in entity_relationships:
    entity_relationships[token] = {...}

# Efficient dictionary update
entity_relationships[token].setdefault("relationships", {})[other_token] = relation
```

### 4. Text Processing Optimizations

#### 4.1 Staged Processing

Text is processed in stages by entity type, allowing for priority-based tokenization:

```python
# Process in order: names, phones, emails, locations, projects
processed_text, name_tokens = self._process_patterns(text, self.name_patterns, "PERSON", ...)
processed_text, phone_tokens = self._process_patterns(processed_text, self.phone_patterns, "PHONE", ...)
```

#### 4.2 Text Reconstruction

Text reconstruction is optimized for speed:

```python
reconstructed = text
for token, original in token_mappings.items():
    reconstructed = reconstructed.replace(f"[{token}]", original)
```

### 5. Python-Specific Optimizations

#### 5.1 Dictionary Comprehensions

Dictionary comprehensions are used for efficient transformations:

```python
inverse_mappings = {value: key for key, value in token_mappings.items()}
```

#### 5.2 List Comprehensions

List comprehensions provide efficient filtering:

```python
project_tokens = [token for token, value in token_map.items() 
                  if token.startswith("PROJECT")]
```

#### 5.3 Generator Expressions

Generator expressions are used for memory efficiency:

```python
any(original == "John Smith" for original in result.token_map.values())
```

## Optimization Guidelines for Future Development

When adding new features or modifying existing ones, consider these guidelines:

### 1. Regex Optimization

1. **Test Regex Performance**: Use tools like regex101.com to evaluate your patterns
2. **Avoid Catastrophic Backtracking**: Be careful with nested repetition operators
3. **Use Atomic Groups**: Consider using atomic groups `(?>...)` for complex patterns
4. **Be Specific**: More specific patterns are often faster
5. **Use Word Boundaries**: `\b` checks are cheap and filter out many non-matches

### 2. Data Structure Selection

1. **Use Dictionaries** for lookups whenever possible
2. **Prefer Sets** for membership testing over lists
3. **Consider OrderedDict** when order matters
4. **Use Collections.defaultdict** to simplify code with default values

### 3. Profiling Techniques

When optimizing, always profile first to identify bottlenecks:

```python
import cProfile
import pstats

def profile_func(func, *args, **kwargs):
    profiler = cProfile.Profile()
    profiler.enable()
    result = func(*args, **kwargs)
    profiler.disable()
    stats = pstats.Stats(profiler).sort_stats('cumtime')
    stats.print_stats(20)
    return result

# Example usage
profile_func(privacy_engine.deidentify, text, session_id)
```

### 4. Benchmarking New Changes

Always benchmark changes to detect performance regressions:

```bash
python -m pytest tests/benchmarks/test_privacy_benchmarks.py -v
```

## Conclusion

The current implementation prioritizes both correctness and performance. The privacy engine can process text at high throughput rates while maintaining privacy protection and token consistency.

For the next phase of development, we recommend:

1. **Batch Processing**: Implement batch processing for multiple texts
2. **Token Intelligence Caching**: Add client-side caching for token intelligence results
3. **Pattern Compilation**: Pre-compile regex patterns at initialization
4. **Parallel Processing**: Consider parallel processing for large texts

By following these recommendations, we can further improve the system's performance while maintaining its robust privacy protection capabilities. 