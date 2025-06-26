# Privacy Component Migration Plan

## Overview

This document outlines the plan for migrating from the legacy `privacy.py` module to the new privacy components in the `privacy/` package.

## Current Status

- Legacy `knowledge_base/privacy.py` (0% test coverage)
  - Contains `PrivacyIntegration`, `PrivacyBundle`, and `PrivacyValidator` classes
  - Handles integration with the Sankofa privacy layer
  - Lacks tests and proper integration with the rest of the system

- New Privacy Components (89-100% test coverage)
  - `knowledge_base/privacy/smart_anonymization.py` (89% coverage)
  - `knowledge_base/privacy/session_manager.py` (100% coverage)
  - `knowledge_base/privacy/token_intelligence_bridge.py` (90% coverage)
  - Modern, well-tested implementation of privacy features

## Migration Path

### Phase 1: Deprecation (Current)

1. ✅ Mark legacy `privacy.py` module as deprecated
2. ✅ Update imports to use new privacy components
3. ✅ Add deprecation warnings for legacy module usage
4. ✅ Keep legacy module available for backwards compatibility

### Phase 2: Mapping & Transition Support

1. Create adapter/wrapper classes that provide the same interface as legacy components
   - Implement `PrivacyIntegrationAdapter` that wraps the new `PrivacyEngine`
   - Map `PrivacyBundle` functionality to modern equivalents
   - Redirect `PrivacyValidator` calls to appropriate new validation methods

2. Update documentation to guide users from legacy to new components
   - Add migration examples in documentation
   - Document breaking changes and benefits of the new approach

### Phase 3: Full Migration

1. Implement full replacement of Sankofa integration within the new privacy infrastructure
   - Port any unique features from legacy code not yet in the modern components
   - Implement full test coverage for the migrated features
   
2. Update any remaining code that depends on legacy features
   - Focus on better error handling and performance
   - Ensure all edge cases are covered by tests

### Phase 4: Removal

1. Remove legacy `privacy.py` module in a major version update
2. Update all documentation and code examples to use only new privacy components
3. Update test documentation and framework to reflect changes

## Timeline

- **Phase 1**: Complete
- **Phase 2**: 1 week
- **Phase 3**: 2 weeks
- **Phase 4**: Next major version release

## Benefits of Migration

1. **Improved Test Coverage**: New components have 89-100% test coverage vs 0% for legacy
2. **Better Performance**: Modern implementation includes optimizations like:
   - Batch processing with ThreadPoolExecutor
   - Client-side caching for token intelligence
   - Pre-compiled regex patterns
   
3. **Enhanced Maintainability**: 
   - Clear separation of concerns
   - Modern typing and documentation
   - Better error handling
   - Consistent interfaces

4. **New Features**:
   - Privacy session management
   - Token intelligence integration
   - Multiple privacy levels
   - Enhanced entity relationship tracking

## Migration Assistance

For assistance with migrating from legacy components to the new privacy system, refer to:

1. Privacy Integration Guide: `docs/privacy_integration.md`
2. API Documentation: `docs/api.md`
3. See examples in `tests/privacy/test_privacy_integration.py` 