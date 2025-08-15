---
name: Provider Implementation
about: Implement a new data provider for CVRGPT v2
title: 'feat(provider): implement [provider name]'
labels: ['enhancement', 'provider']
assignees: ''
---

## Provider Overview
**Provider Name**: [e.g. CVR API, RegnskabsData, Custom]
**Data Source**: [URL or description of the data source]
**Priority**: [High/Medium/Low]

## Implementation Checklist
- [ ] Create provider class extending `cvrgpt_core.providers.base.Provider`
- [ ] Implement required methods:
  - [ ] `search_companies(query: str, limit: int)`
  - [ ] `get_company(cvr: str)`
  - [ ] `list_filings(cvr: str, limit: int)`
  - [ ] `get_latest_accounts(cvr: str)`
- [ ] Add error handling and retries
- [ ] Add caching support
- [ ] Add rate limiting compliance
- [ ] Write unit tests
- [ ] Add integration tests
- [ ] Update provider factory
- [ ] Add configuration options
- [ ] Update documentation

## Technical Requirements
- [ ] Follow existing provider patterns
- [ ] Use httpx client from `app.http`
- [ ] Include proper source citations
- [ ] Handle pagination if applicable
- [ ] Validate CVR format (8 digits)

## Testing Requirements
- [ ] Mock external API calls
- [ ] Test error scenarios (404, 500, timeout)
- [ ] Test rate limiting behavior
- [ ] Test caching behavior
- [ ] Test with fixture data

## Documentation
- [ ] Add provider to README
- [ ] Document configuration options
- [ ] Add usage examples
- [ ] Update API documentation if needed
