# v1.10.0 Retrospective

**Milestone:** Remote Data & Automation

**Features:** F-126 (URL Data Ingestion), F-127 (Project Automation)

---

## What Went Well

### URL Data Ingestion Design
- Clean separation between fetching, caching, and attribution
- GitHub URL auto-conversion provides excellent UX
- Terms acceptance creates proper audit trail for research use
- SHA256 hashing enables data integrity verification

### Project Automation
- Makefile provides familiar interface for developers
- POSIX compatibility ensures cross-platform support
- Docker setup enables consistent development environments
- GitHub workflows automate release process

### Documentation
- Tutorial created alongside implementation
- Feature specs accurately reflected final implementation
- CLI help updated with new flags

---

## What Could Improve

### Testing Coverage
- Integration tests for URL fetching rely on external services
- Could add more mock-based unit tests for network failures
- Docker workflow testing is manual

### Error Messages
- Some HTTP errors could provide more actionable guidance
- Cache corruption errors could suggest recovery steps

### Performance
- Large file downloads don't show progress indication
- Could add streaming support for very large datasets

---

## Lessons Learned

### 1. Terms Acceptance UX Matters
Initial implementation required `--accept-terms` even for cached data. Users found this confusing. Solution: Only require terms acceptance on first fetch, not cache hits.

### 2. Shell Script Portability is Hard
macOS and Linux differ in subtle ways:
- `sed -i` requires backup extension on macOS
- `realpath` not available on older macOS
- String comparison differs between bash versions

Solution: Test on both platforms, use POSIX-compatible patterns.

### 3. Docker Layer Caching
Initial Dockerfile didn't optimise for layer caching, causing slow rebuilds. Solution: Order commands by change frequency, copy requirements before code.

---

## Decisions Made

### ADR: Content Hash for Attribution
**Decision:** Use SHA256 of content rather than URL for identifying data sources.

**Rationale:** URLs can change (redirects, CDN updates) while content remains the same. Hashing content provides stable identity.

### ADR: Separate Cache from Attribution
**Decision:** Keep URL cache separate from attribution metadata.

**Rationale:** Cache is ephemeral (can be cleared), attribution is permanent (part of experiment record).

---

## Metrics

| Metric | Value |
|--------|-------|
| Features completed | 2 |
| New files created | 15 |
| Tests added | 45 |
| Documentation pages | 3 |

---

## Follow-Up Actions

- [ ] Add progress bar for large downloads (future enhancement)
- [ ] Consider authentication support for private URLs (future enhancement)
- [ ] Add cache statistics command (nice to have)

---

## Related Documentation

- [v1.10.0 Devlog](../../devlogs/v1.10.0/)
- [v1.10.0 Milestone](../../roadmap/milestones/v1.10.0.md)
- [F-126 Specification](../../roadmap/features/completed/F-126-url-data-ingestion.md)
- [F-127 Specification](../../roadmap/features/completed/F-127-project-automation.md)

