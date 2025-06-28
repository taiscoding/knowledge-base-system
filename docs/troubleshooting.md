# Knowledge Base System: Troubleshooting Guide

This document provides guidance for troubleshooting common issues in the Knowledge Base system.

## Error Handling System

The Knowledge Base system implements a comprehensive error handling system with a hierarchy of exception types to help diagnose and fix issues.

### Exception Hierarchy

The system uses the following exception types, all derived from the base `KnowledgeBaseError`:

| Exception Type | Description | Common Causes |
|----------------|-------------|---------------|
| `ConfigurationError` | Issues with configuration loading or validation | Missing config files, invalid YAML format, missing required settings |
| `StorageError` | Problems with file I/O and storage operations | Disk full, permission issues, corrupted files |
| `ContentProcessingError` | Failures in content extraction or processing | Invalid regex patterns, unexpected input format |
| `PrivacyError` | Issues with privacy-preserving operations | Token generation failures, session issues |
| `ValidationError` | Data validation failures | Invalid data format, schema violations |
| `NotFoundError` | Requested resources not found | Missing files, invalid paths |
| `RecoveryError` | Failed recovery attempts | Unable to recover from previous errors |

### Logging Levels

The system uses different logging levels to provide details about operations:

- `ERROR` - Critical issues that need immediate attention
- `WARNING` - Issues that don't cause failures but should be addressed
- `INFO` - Normal operation information
- `DEBUG` - Detailed information for troubleshooting

### Checking Logs

Log files are stored in the `logs` directory by default. To check logs:

```bash
# View recent log entries
tail -n 100 logs/knowledge_base.log

# Search for errors
grep "ERROR" logs/knowledge_base.log

# Search for a specific error type
grep "ConfigurationError" logs/knowledge_base.log
```

## Circuit Breaker Status

The system implements the Circuit Breaker pattern for fault tolerance in critical components. If you're experiencing issues, check the circuit breaker status:

### API Endpoint

```bash
# Check circuit breaker status via API
curl http://localhost:8000/api/v1/system/circuit-breakers
```

### Log Inspection

Look for circuit breaker state changes in logs:

```bash
grep "Circuit .* state changed" logs/knowledge_base.log
```

### Circuit Breaker States

- `CLOSED` - Normal operation, all requests passing through
- `OPEN` - Failure threshold reached, requests short-circuited to fallbacks
- `HALF_OPEN` - Testing recovery, limited requests passing through

### Resetting Circuit Breakers

If a circuit is stuck in the OPEN state and you want to force it to reset:

```bash
curl -X POST http://localhost:8000/api/v1/system/circuit-breakers/reset
```

## Common Issues and Solutions

### 1. Configuration Issues

**Symptoms:**
- `ConfigurationError` exceptions
- Application fails to start
- Features using specific configurations don't work

**Solutions:**
- Check that config files exist in the `config/` directory
- Validate YAML syntax in config files
- Ensure required settings are present
- Check environment variables that might override configurations

### 2. Storage Issues

**Symptoms:**
- `StorageError` exceptions
- Files not saved or corrupted
- Search functionality not returning results

**Solutions:**
- Verify write permissions on data directories
- Check disk space
- Ensure file paths don't contain invalid characters
- Verify no other processes are locking files

### 3. Privacy Issues

**Symptoms:**
- `PrivacyError` exceptions
- Content not properly anonymized
- Tokens not being reconstructed correctly

**Solutions:**
- Check privacy session existence and validity
- Verify token mappings in the session
- Look for circuit breaker issues in privacy components
- Check token intelligence service connectivity

### 4. Content Processing Issues

**Symptoms:**
- `ContentProcessingError` exceptions
- Missing todos, events, or tags in results
- Incorrect categorization of content

**Solutions:**
- Review the input format
- Check regex patterns in extraction methods
- Ensure content types are properly configured
- Verify necessary dependencies are available

## Recovery Mechanisms

### Fallback Behaviors

The system implements various fallback behaviors to maintain operation during failures:

1. **Privacy Engine Fallbacks**:
   - Minimal privacy processing when full processing fails
   - Reuse of existing tokens when intelligence services are unavailable
   - Preservation of original text when reconstruction fails

2. **Content Processing Fallbacks**:
   - Default values for tag extraction failures
   - Safe title generation when parsing fails
   - Conservative behavior with incomplete data

3. **Storage Fallbacks**:
   - In-memory operation when persistence fails
   - Automatic retry logic for transient errors

### Manual Recovery

For serious issues requiring manual recovery:

1. **Session Recovery**:
   ```bash
   # Re-initialize privacy session
   curl -X POST http://localhost:8000/api/v1/privacy/reset-session
   ```

2. **Cache Clearing**:
   ```bash
   # Clear all caches
   curl -X POST http://localhost:8000/api/v1/system/clear-caches
   ```

3. **Index Rebuilding**:
   ```bash
   # Rebuild search indices
   curl -X POST http://localhost:8000/api/v1/search/rebuild-index
   ```

## Performance Issues

If you're experiencing performance issues:

1. **Check Circuit Breaker Metrics**:
   - Are circuits frequently opening and closing?
   - Are fallbacks being used excessively?

2. **Monitor Cache Efficiency**:
   - Check cache hit rates
   - Verify TTL settings are appropriate

3. **Examine Batch Processing**:
   - Are batch operations completing?
   - Is parallelism configured correctly?

For more help with performance issues, refer to [performance_optimization.md](./performance_optimization.md).

## Web Interface Issues

### 1. Frontend Runtime Errors

**Symptoms:**
- Blank pages or screens
- Error messages in browser console
- Animations not working correctly
- Pages fail to render completely

**Solutions:**
- Check browser console for specific error messages
- Verify that the backend server is running and accessible
- Clear browser cache and reload the page
- Ensure all required dependencies are installed

### 2. Animation and Transition Issues

**Symptoms:**
- Error: `Invalid easing type 'cubic-bezier(0.4, 0, 0.2, 1)'`
- Pages fail to transition smoothly
- Components appear without animation

**Solutions:**
- Ensure animation easing values are in the correct format (arrays for framer-motion)
- Check that the `PageTransition` component is properly configured
- Verify that `framer-motion` library is correctly installed

### 3. Backend Connection Problems

**Symptoms:**
- 404 Not Found errors in console
- API endpoints not responding
- Data not loading in the interface

**Solutions:**
- Check if the backend server is running on the expected port
- Verify that the API endpoints match what the frontend expects
- Ensure sample data exists for testing
- Check for port conflicts with other applications

### 4. Infinite Loading Screens

**Symptoms:**
- Loading spinner never completes
- Application appears to start but never shows content
- Backend logs show connection attempts

**Solutions:**
- Check for port conflicts using `lsof -i :<port_number>`
- Kill any lingering processes using the required ports
- Restart both frontend and backend servers
- Verify that authentication is working correctly

For detailed information about recent fixes to these issues, see our [Troubleshooting Fixes Summary](../development/records/TROUBLESHOOTING_FIXES_SUMMARY.md).

## Getting More Help

If you're unable to resolve an issue using this guide, you can:

1. Check the [FAQ](./faq.md) for common questions
2. Open an issue in the project repository
3. Contact the development team via the support channels listed in the [README](../README.md) 