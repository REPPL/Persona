# F-149: Audit Log Export

## Overview

| Attribute | Value |
|-----------|-------|
| **Feature ID** | F-149 |
| **Title** | Audit Log Export |
| **Priority** | P1 (High) |
| **Category** | Compliance |
| **Milestone** | [v1.14.0](../../milestones/v1.14.0.md) |
| **Status** | 📋 Planned |
| **Dependencies** | F-123 (Generation Audit Trail), F-125 (Data Lineage) |

---

## Problem Statement

Compliance requirements (GDPR, HIPAA, EU AI Act) require:
- Complete audit trails of data processing
- Exportable evidence for auditors
- Lineage documentation
- Processing activity records

Currently, audit data exists but lacks compliance-ready export.

---

## Design Approach

Export audit trails in formats suitable for compliance reporting.

---

## Key Capabilities

### 1. Audit Export

Export audit logs in various formats.

```bash
# Export to CSV
persona audit export --format csv --output audit.csv

# Export to JSON
persona audit export --format json --output audit.json

# Export to PDF (report format)
persona audit export --format pdf --output audit-report.pdf
```

### 2. Date Range Filtering

Filter exports by time period.

```bash
# Last 30 days
persona audit export --days 30

# Specific date range
persona audit export --from 2025-01-01 --to 2025-01-31

# Since last export
persona audit export --since-last-export
```

### 3. Compliance Reports

Generate compliance-specific reports.

```bash
# GDPR processing record
persona audit report --compliance gdpr --output gdpr-report.pdf

# Research ethics
persona audit report --compliance research-ethics --output ethics.pdf
```

**GDPR Report Contents:**
```
GDPR Article 30 Processing Record
═════════════════════════════════════════════════════════════════

Data Controller: [Organisation Name]
Report Period: 2025-01-01 to 2025-01-31

Processing Activities
─────────────────────
| Date | Activity | Data Categories | Legal Basis |
|------|----------|-----------------|-------------|
| 2025-01-15 | Persona Generation | Interview data | Legitimate interest |
| 2025-01-16 | PII Anonymisation | Personal data | Legal obligation |

Data Lineage Summary
────────────────────
- Input sources: 12 files
- Generated personas: 47
- PII detected and anonymised: 156 instances

Retention Status
────────────────
- Data older than 90 days: 0 records
- Scheduled for deletion: 0 records
```

### 4. Lineage Export

Export data lineage in standard formats.

```bash
# PROV-JSON format
persona audit lineage --format prov-json --output lineage.json

# Graphviz DOT
persona audit lineage --format dot --output lineage.dot

# Visualise
persona audit lineage --visualise --output lineage.svg
```

---

## CLI Commands

```bash
# Basic export
persona audit export [--format csv|json|pdf] [--output FILE]

# Filtered export
persona audit export --from DATE --to DATE
persona audit export --user USER_ID
persona audit export --action generate|validate|export

# Compliance reports
persona audit report --compliance gdpr|hipaa|research-ethics

# Lineage export
persona audit lineage [--format prov-json|dot|svg] [--output FILE]
persona audit lineage --entity ENTITY_ID --depth N

# Summary
persona audit summary [--days N]
```

---

## Success Criteria

- [ ] CSV/JSON export includes all audit fields
- [ ] PDF reports are professionally formatted
- [ ] GDPR Article 30 report template complete
- [ ] Lineage export in PROV-JSON format
- [ ] Date filtering works correctly
- [ ] Large exports stream without memory issues
- [ ] Test coverage >= 85%

---

## Related Documentation

- [v1.14.0 Milestone](../../milestones/v1.14.0.md)
- [F-123: Generation Audit Trail](../completed/F-123-generation-audit-trail.md)
- [F-125: Data Lineage & Provenance](../completed/F-125-data-lineage-provenance.md)
- [ADR-0027: Data Lineage Implementation](../../../decisions/adrs/ADR-0027-data-lineage-implementation.md)

---

**Status**: Planned
