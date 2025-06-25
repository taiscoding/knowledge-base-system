# Troubleshooting Guide

This document helps you diagnose and fix common issues with the Knowledge Base & Token Intelligence System.

## Installation Issues

### ImportError: No module named 'knowledge_base'

**Problem**: The system is not installed correctly or not in your Python path.

**Solutions**:
1. Verify the installation:
   ```bash
   pip list | grep knowledge-base-system
   ```

2. If not installed, install or reinstall:
   ```bash
   pip install knowledge-base-system
   ```

3. If installing from source, ensure you're in the correct directory:
   ```bash
   cd knowledge-base-system
   pip install -e .
   ```

### ModuleNotFoundError: No module named 'yaml'

**Problem**: Missing dependencies.

**Solution**:
```bash
pip install pyyaml
```

## Configuration Issues

### FileNotFoundError: config/ai_instructions.yaml

**Problem**: Configuration files are not in the expected location.

**Solutions**:
1. Create the config directory and files:
   ```bash
   mkdir -p config
   touch config/ai_instructions.yaml
   touch config/conventions.yaml
   ```

2. Or specify an alternate configuration path:
   ```python
   from knowledge_base import KnowledgeBaseManager
   kb = KnowledgeBaseManager(base_path="/path/to/custom/config")
   ```

### Configuration values not being applied

**Problem**: Environment variables or configuration changes are not taking effect.

**Solutions**:
1. Verify environment variables are set:
   ```bash
   echo $KB_LOG_LEVEL
   ```

2. Restart your Python environment after changing configurations.

3. Check that you're updating the correct files:
   ```bash
   ls -la config/
   ```

## Data Storage Issues

### Permission denied when saving content

**Problem**: The application doesn't have write permissions for the data directory.

**Solutions**:
1. Check permissions on the data directory:
   ```bash
   ls -la data/
   ```

2. Change permissions if needed:
   ```bash
   chmod -R 755 data/
   ```

3. Specify a different data path:
   ```bash
   export KB_DATA_PATH=/path/to/writable/directory
   ```

### Content not being saved

**Problem**: Content is processed but not appearing in the data directory.

**Solutions**:
1. Check the return value from `process_stream_of_consciousness()` for errors.

2. Verify the data directory exists:
   ```bash
   mkdir -p data/notes data/todos data/calendar data/journal
   ```

3. Enable debug logging to see where files are being saved:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

## Token Intelligence Issues

### No intelligence results returned

**Problem**: The token intelligence engine is not returning any results.

**Solutions**:
1. Ensure your text contains properly formatted tokens:
   ```
   [PERSON_001], [PROJECT_002], etc.
   ```

2. Check that you're providing sufficient context:
   ```python
   request = TokenIntelligenceRequest(
       privacy_text="Meeting about [PROJECT_001]",
       preserved_context=["quarterly", "report", "deadline"],  # Add relevant context
       session_id="session-123"
   )
   ```

3. Use the same session ID for related operations to build up intelligence.

### Low confidence scores in intelligence results

**Problem**: Intelligence results have low confidence scores.

**Solutions**:
1. Provide more context in the `preserved_context` field.

2. Use consistent session IDs for related content.

3. Include entity relationships:
   ```python
   request = TokenIntelligenceRequest(
       privacy_text="Meeting with [PERSON_001] about [PROJECT_002]",
       preserved_context=["meeting", "project"],
       entity_relationships={
           "[PERSON_001]": {"type": "person", "linked_entities": ["[PROJECT_002]"]},
           "[PROJECT_002]": {"type": "project", "belongs_to": "[PERSON_001]"}
       },
       session_id="session-123"
   )
   ```

## Privacy Integration Issues

### Privacy layer integration errors

**Problem**: Issues with the Sankofa privacy integration.

**Solutions**:
1. Verify the Sankofa configuration:
   ```bash
   cat config/sankofa_integration.yaml
   ```

2. Check that the privacy configuration is correctly formatted YAML.

3. Manually validate that tokens follow the correct format.

### Bundle import failures

**Problem**: Unable to import privacy bundles.

**Solutions**:
1. Verify the bundle file exists and is readable:
   ```bash
   ls -la path/to/bundle.json
   ```

2. Check that the bundle is valid JSON:
   ```bash
   python -m json.tool path/to/bundle.json
   ```

3. Enable debug logging to see detailed import errors:
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

## Search Issues

### No search results returned

**Problem**: Searching returns no results even when content exists.

**Solutions**:
1. Try a more general search term.

2. Check that you're searching in the correct content type:
   ```python
   # Search all content types
   kb.search_content("meeting")
   
   # Search specific content type
   kb.search_content("meeting", content_type="calendar")
   ```

3. Verify content exists in the data directory:
   ```bash
   find data/ -type f -name "*.json" -o -name "*.md" | wc -l
   ```

### Search returning too many results

**Problem**: Search returns too many unrelated items.

**Solution**:
1. Make your search more specific:
   ```python
   # Instead of
   kb.search_content("meeting")
   
   # Try
   kb.search_content("quarterly meeting budget")
   ```

2. Specify the content type:
   ```python
   kb.search_content("meeting", content_type="todos")
   ```

## CLI Issues

### Command not found: kb-cli

**Problem**: The CLI command is not found after installation.

**Solutions**:
1. Check that the package is installed correctly:
   ```bash
   pip show knowledge-base-system
   ```

2. Verify the binary is in your PATH:
   ```bash
   which kb-cli
   ```

3. Reinstall the package:
   ```bash
   pip install -e .
   ```

### CLI commands failing

**Problem**: CLI commands return errors.

**Solutions**:
1. Run with the `--debug` flag for more information:
   ```bash
   kb-cli --debug search "term"
   ```

2. Check that file paths exist and are accessible.

3. Verify the command syntax:
   ```bash
   kb-cli --help
   ```

## Performance Issues

### Slow processing of content

**Problem**: Content processing is taking a long time.

**Solutions**:
1. Process smaller chunks of content at once.

2. Check system resources (CPU, memory) during processing.

3. Consider setting up a caching mechanism for repeat operations.

### High memory usage

**Problem**: The application is using too much memory.

**Solution**:
1. Process files in batches rather than all at once.

2. Close file handles explicitly after use.

3. Use a memory profiler to identify memory leaks:
   ```bash
   pip install memory_profiler
   python -m memory_profiler your_script.py
   ```

## Getting More Help

If you've tried the troubleshooting steps above and still have issues:

1. **Check the Documentation**: Review the [User Guide](user_guide.md) and [API Reference](api.md)

2. **Search Existing Issues**: Check if your issue has already been reported on the project's GitHub repository

3. **Ask the Community**: Post on the community forum or discussion channels

4. **File an Issue**: If you've found a bug, file an issue with:
   - A clear description of the problem
   - Steps to reproduce
   - Expected vs. actual behavior
   - System information (OS, Python version, package version)
   - Any relevant logs or error messages

5. **Contact Support**: For urgent issues, contact the support team directly

Remember to include as much relevant information as possible when seeking help, including error messages, code snippets, and the steps to reproduce the issue. 