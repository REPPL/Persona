# Building a Persona Library

Learn how to manage personas across multiple projects over time.

**Level:** Intermediate | **Time:** 25 minutes

## What You'll Learn

- Organising experiments by project
- Versioning personas over time
- Creating persona collections
- Exporting for team sharing
- Archiving completed projects

## Prerequisites

- Completed [Getting Started](01-getting-started.md)
- Several generated personas from different projects

## Why Build a Library?

Research projects span months or years. A well-organised persona library:

- **Prevents duplication** - Don't regenerate what you already have
- **Enables comparison** - Track how personas evolve with new data
- **Supports collaboration** - Share with team members
- **Maintains history** - Audit trail of methodology changes

## Step 1: Project-Based Organisation

Structure your experiments by project:

```
experiments/
├── project-alpha/
│   ├── v1-initial-research/
│   │   ├── config.yaml
│   │   ├── data/
│   │   └── outputs/
│   ├── v2-expanded-sample/
│   │   ├── config.yaml
│   │   ├── data/
│   │   └── outputs/
│   └── v3-validation/
│       ├── config.yaml
│       ├── data/
│       └── outputs/
│
├── project-beta/
│   ├── discovery-phase/
│   ├── user-testing/
│   └── final-personas/
│
└── templates/
    └── standard-experiment/
```

### Naming Conventions

| Pattern | Example | Use When |
|---------|---------|----------|
| **Version prefix** | `v1-initial`, `v2-refined` | Iterating on same dataset |
| **Phase name** | `discovery`, `validation` | Research phases |
| **Date prefix** | `2024-Q4-study` | Time-bounded research |

## Step 2: Versioning Personas

Track persona evolution with versioned outputs:

```bash
# Initial generation
persona generate \
  --from project-alpha/v1-initial-research \
  --tag "baseline"

# After adding more data
persona generate \
  --from project-alpha/v2-expanded-sample \
  --tag "expanded"
```

This creates tagged outputs:

```
outputs/
├── 20241201_baseline/
│   ├── metadata.json  # includes tag: "baseline"
│   └── personas/
└── 20241215_expanded/
    ├── metadata.json  # includes tag: "expanded"
    └── personas/
```

### Comparing Versions

See how personas changed:

```bash
persona compare \
  --tag baseline \
  --tag expanded \
  --project project-alpha
```

**Output:**

```
Version Comparison: baseline → expanded
───────────────────────────────────

Persona 1: Sarah → Sarah (refined)
  + Added: "Uses keyboard shortcuts extensively"
  - Removed: Generic tech proficiency claim
  ~ Changed: Age range 25-35 → 30-35 (more specific)

Persona 2: James → Merged into Marcus
  Note: Similar personas consolidated

New Persona: Elena (first appeared in v2)
  Source: New interview participants
```

## Step 3: Creating Collections

Group personas across experiments:

```bash
# Create a collection
persona collection create "Mobile Users" \
  --from project-alpha/v2-expanded-sample/outputs/latest/personas/01 \
  --from project-beta/discovery-phase/outputs/latest/personas/02 \
  --from project-beta/discovery-phase/outputs/latest/personas/03
```

This creates:

```
collections/
└── mobile-users/
    ├── collection.yaml
    ├── sarah-chen/           # Linked from project-alpha
    ├── james-developer/      # Linked from project-beta
    └── elena-commuter/       # Linked from project-beta
```

### Collection Metadata

```yaml
# collections/mobile-users/collection.yaml
name: Mobile Users
description: "Personas focused on mobile usage patterns"
created: 2024-12-15
personas:
  - source: project-alpha/v2-expanded-sample
    id: persona-01
    alias: sarah-chen
  - source: project-beta/discovery-phase
    id: persona-02
    alias: james-developer
  - source: project-beta/discovery-phase
    id: persona-03
    alias: elena-commuter
tags:
  - mobile
  - commuters
  - power-users
```

## Step 4: Exporting for Teams

Share personas with your team:

### Export to Shared Folder

```bash
# Export collection as standalone package
persona export collection "Mobile Users" \
  --output ~/Dropbox/Research/persona-exports/ \
  --format bundle
```

Creates:

```
persona-exports/
└── mobile-users-2024-12-15/
    ├── README.md           # Overview and usage
    ├── personas/
    │   ├── sarah-chen.md
    │   ├── sarah-chen.json
    │   ├── james-developer.md
    │   └── ...
    ├── metadata.json       # Generation details
    └── sources.txt         # Data provenance
```

### Export to Design Tools

```bash
# Export for Figma
persona export collection "Mobile Users" \
  --format figma \
  --output persona-cards.fig

# Export for Miro
persona export collection "Mobile Users" \
  --format miro \
  --output persona-board.json
```

## Step 5: Archiving Projects

When a project completes, archive it:

```bash
# Archive a project
persona archive project-alpha \
  --reason "Project completed, product launched"
```

This:
1. Compresses the experiment folder
2. Moves to `archives/` directory
3. Preserves metadata for future reference
4. Removes from active listings

```
archives/
└── project-alpha-2024-12-20.tar.gz
```

### Restoring Archived Projects

```bash
# List archives
persona archive list

# Restore
persona archive restore project-alpha-2024-12-20
```

## Step 6: Library Dashboard

View your entire library:

```bash
persona library status
```

**Output:**

```
Persona Library
───────────────────────────────────

Active Projects: 3
  project-beta (12 personas, updated 2 days ago)
  project-gamma (5 personas, updated 1 week ago)
  project-delta (in progress, 0 personas)

Collections: 2
  Mobile Users (3 personas)
  Enterprise Admins (4 personas)

Archived: 1
  project-alpha (8 personas, archived 2024-12-20)

Total Personas: 32
Total Experiments: 15
Storage Used: 45 MB

Recent Activity:
  2024-12-15: Generated 5 personas in project-gamma
  2024-12-13: Created collection "Mobile Users"
  2024-12-10: Archived project-alpha
```

## Library Maintenance

### Regular Tasks

| Task | Frequency | Command |
|------|-----------|---------|
| Review unused experiments | Monthly | `persona library cleanup --dry-run` |
| Update collections | After major research | `persona collection update` |
| Archive completed projects | End of project | `persona archive <project>` |
| Export for backup | Weekly | `persona export all --to backup/` |

### Cleanup Unused Data

```bash
# See what would be removed
persona library cleanup --dry-run

# Remove experiments older than 6 months with no personas
persona library cleanup --older-than 6m --empty-only
```

## Team Collaboration Patterns

### Shared Library

```bash
# Set library location to shared drive
persona config set library.path "/shared/research/personas"

# All team members use same library
```

### Individual + Sync

```bash
# Local development
persona config set library.path "./experiments"

# Export to shared on completion
persona export experiment my-research --to /shared/personas/
```

## What's Next?

Now that you can manage a persona library:

1. **[Validating Quality](06-validating-quality.md)** - Ensure personas are accurate
2. **[G-03: Design Integration](../guides/design-integration.md)** - Use personas in design tools
3. **[Experiment Reproducibility](../explanation/reproducibility.md)** - Re-run experiments exactly

---

## Related Documentation

- [F-006: Experiment Management](../development/roadmap/features/planned/F-006-experiment-management.md)
- [Experiment Reproducibility](../explanation/reproducibility.md)
- [G-03: Design Integration](../guides/design-integration.md)

