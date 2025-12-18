# Organising Persona Research

Learn how to manage personas across multiple projects and track research over time.

**Level:** Intermediate | **Time:** 20 minutes

## What You'll Learn

- Organising research using the project system
- Managing multiple projects with the global registry
- Versioning research with output directories
- Comparing personas across iterations
- Exporting for team sharing
- Recommended directory structures

## Prerequisites

- Completed [Getting Started](01-getting-started.md)
- Generated personas from at least one data source

## Why Organise Your Research?

Research projects span months or years. A well-organised research library:

- **Prevents duplication** - Don't regenerate what you already have
- **Enables comparison** - Track how personas evolve with new data
- **Supports collaboration** - Share with team members
- **Maintains history** - Audit trail of methodology changes

## Step 1: Project-Based Organisation

Persona provides a project registry for organising research across multiple studies.

### Creating a New Project

```bash
# Create a new project
persona project create mobile-users

# With description
persona project create mobile-users \
  --description "Mobile app user research Q4 2024"

# In a specific location
persona project create mobile-users \
  --path ~/research/
```

This creates the project structure:

```
mobile-users/
├── project.yaml       # Project configuration
├── data/              # Input data
└── output/            # Generated personas
```

### Listing Your Projects

```bash
# View all registered projects
persona project list

# Output:
# Name           Path                              Status
# mobile-users   /Users/you/research/mobile-users  ✓
# enterprise     /Users/you/research/enterprise    ✓
```

### Viewing Project Details

```bash
# Show project configuration
persona project show mobile-users

# Output includes:
# - Project path and template
# - Default settings (provider, count, workflow)
# - Registered data sources
```

### Registering Existing Projects

Already have a research directory? Register it:

```bash
# Register an existing directory
persona project register my-old-research ./path/to/research
```

## Step 2: Versioning with Output Directories

Each time you generate personas, Persona creates a timestamped output directory. Use this for tracking research evolution.

### Understanding Output Structure

```bash
# Generate personas (creates timestamped output)
persona generate --from mobile-users

# Creates:
# output/20241217_143022/
#   ├── metadata.json
#   ├── personas.json
#   └── personas/
#       ├── persona_001.json
#       ├── persona_001.md
#       └── ...
```

### Naming Conventions for Experiments

While Persona creates timestamps automatically, use meaningful naming for your data and tracking:

| Pattern | Example | Use When |
|---------|---------|----------|
| **Version prefix** | `v1-initial`, `v2-refined` | Iterating on same dataset |
| **Phase name** | `discovery`, `validation` | Research phases |
| **Date prefix** | `2024-Q4-study` | Time-bounded research |

Example workflow:

```bash
# Initial baseline with 100 interviews
persona generate \
  --from ./data/v1-baseline/ \
  --count 5

# Note the output timestamp: 20241201_100530

# Later, with expanded dataset (200 interviews)
persona generate \
  --from ./data/v2-expanded/ \
  --count 5

# Note the output timestamp: 20241215_143022
```

Keep a simple tracking file in `.work/` (not committed):

```markdown
# .work/mobile-users-tracking.md

## Research Iterations

### v1-baseline (20241201_100530)
- 100 interviews
- 5 personas generated
- Focus: basic mobile usage patterns

### v2-expanded (20241215_143022)
- 200 interviews (added 100 power users)
- 5 personas generated
- Focus: expanded to include power users
```

## Step 3: Comparing Persona Sets

Use the compare command to analyse how personas change between iterations.

### Basic Comparison

```bash
# Compare all personas in an output directory
persona compare ./output/20241201_100530/
```

This shows:
- Overall similarity scores between all persona pairs
- Which personas are potentially duplicates (>70% similar)
- Similarity in goals, pain points, demographics, and behaviours

### Comparing Specific Personas

```bash
# Compare two specific personas
persona compare ./output/20241201_100530/ \
  --persona-a persona_001 \
  --persona-b persona_002
```

Output includes:
- Detailed similarity breakdown
- Shared goals and pain points
- Unique goals for each persona
- Demographic differences
- Recommendation on whether to consolidate

### Adjusting Similarity Threshold

```bash
# Find only very similar personas (>80%)
persona compare ./output/20241201_100530/ --threshold 80
```

### Manual Cross-Version Comparison

To compare across research iterations, you can:

1. Load both persona sets manually
2. Document findings in `.work/comparisons/`
3. Track evolution in your research notes

Example comparison workflow:

```bash
# Compare baseline
persona compare ./output/20241201_100530/

# Compare expanded version
persona compare ./output/20241215_143022/

# Document findings in .work/
# (Compare persona names, demographics, goals)
```

## Step 4: Exporting for Teams

Share personas with team members using the export command.

### Markdown Export

Perfect for sharing in documentation or wikis:

```bash
# Export to markdown
persona export ./output/20241215_143022/ \
  --format markdown \
  --output ./shared/personas-q4/
```

Creates individual markdown files for each persona with rich formatting.

### HTML Export

For standalone viewing or embedding in websites:

```bash
# Export to HTML
persona export ./output/20241215_143022/ \
  --format html \
  --output ./shared/personas-q4.html
```

### Design Tool Export

Export directly to design tools:

```bash
# Export for Figma
persona export ./output/20241215_143022/ \
  --format figma \
  --output ./figma-export/

# Export for Miro
persona export ./output/20241215_143022/ \
  --format miro \
  --output ./miro-board.json

# Export for UXPressia
persona export ./output/20241215_143022/ \
  --format uxpressia \
  --output ./uxpressia/
```

### JSON and CSV Export

For analysis or integration with other tools:

```bash
# Export as JSON (machine-readable)
persona export ./output/20241215_143022/ \
  --format json \
  --output ./exports/personas.json

# Export as CSV (spreadsheet-compatible)
persona export ./output/20241215_143022/ \
  --format csv \
  --output ./exports/personas.csv
```

### List Available Formats

```bash
# See all export formats
persona export formats
```

## Step 5: Recommended Directory Structures

### Single Project Structure

```
my-research/
├── project.yaml          # Project configuration
├── data/                 # Input data
│   ├── v1-initial/
│   │   └── interviews.csv
│   ├── v2-expanded/
│   │   └── interviews.csv
│   └── v3-validated/
│       └── interviews.csv
├── output/               # Generated personas (timestamped)
│   ├── 20241201_100530/  # v1 generation
│   ├── 20241215_143022/  # v2 generation
│   └── 20250110_093045/  # v3 generation
└── .work/                # Local tracking (not committed)
    ├── tracking.md
    └── comparisons/
```

### Multi-Project Structure

```
~/research/
├── mobile-users/
│   ├── project.yaml
│   ├── data/
│   └── output/
├── enterprise-admins/
│   ├── project.yaml
│   ├── data/
│   └── output/
├── consumer-survey/
│   ├── project.yaml
│   ├── data/
│   └── output/
└── .shared/              # Shared exports for team
    ├── mobile-users-q4/
    ├── enterprise-final/
    └── consumer-results/
```

Register all projects:

```bash
# Register each project
cd ~/research/mobile-users
persona project register mobile-users .

cd ~/research/enterprise-admins
persona project register enterprise-admins .

cd ~/research/consumer-survey
persona project register consumer-survey .

# Now you can reference them from anywhere
persona project list
persona generate --from mobile-users
```

### Team Collaboration Pattern

For teams working on shared storage:

```bash
# Each team member registers shared projects
persona project register mobile-users /shared/research/mobile-users

# Generate from anywhere
persona generate --from mobile-users --count 5

# Export to shared location
persona export ./output/latest/ \
  --format markdown \
  --output /shared/exports/mobile-users/
```

## Project Management Commands Reference

```bash
# Create new project
persona project create <name>

# List all registered projects
persona project list

# Show project details
persona project show <name>

# Register existing directory
persona project register <name> <path>

# Unregister (doesn't delete files)
persona project unregister <name>

# Set global defaults
persona project defaults --provider openai --count 5

# Add data source to project
persona project add-source interviews data/interviews.csv

# Remove data source
persona project remove-source interviews
```

## Best Practices

### Organisation Tips

1. **One project per research study** - Don't mix unrelated research
2. **Keep data versioned** - Use v1, v2, v3 folders for iterations
3. **Track output timestamps** - Note which output corresponds to which data version
4. **Use .work/ for notes** - Keep working notes out of version control
5. **Export regularly** - Share results with team as you progress

### Naming Conventions

- **Projects**: `mobile-users`, `enterprise-study`, `consumer-q4`
- **Data versions**: `v1-baseline`, `v2-expanded`, `v3-final`
- **Data sources**: `interviews`, `surveys`, `analytics`, `user-feedback`

### Avoid Common Mistakes

❌ **Don't** create separate projects for each iteration
✅ **Do** use one project with versioned data folders

❌ **Don't** manually rename timestamped output folders
✅ **Do** track which timestamp corresponds to which data version

❌ **Don't** commit `.work/` files to version control
✅ **Do** use `.work/` for personal tracking and notes

## Cleaning Up

### Unregister Old Projects

```bash
# Unregister (doesn't delete files)
persona project unregister old-project
```

### Archive Completed Research

Move completed projects to an archive directory:

```bash
# Manual archiving
mv ~/research/completed-study ~/research/archive/
persona project unregister completed-study
```

### Clear Old Outputs

Periodically clean old output directories:

```bash
# Keep only latest 3 outputs per project
cd ~/research/mobile-users/output
ls -t | tail -n +4 | xargs rm -rf
```

## What's Next?

Now that you can organise a research library:

1. **[Validating Quality](06-validating-quality.md)** - Ensure personas are accurate
2. **[Experiment Reproducibility](../explanation/reproducibility.md)** - Re-run experiments exactly
3. **[Data Privacy](../guides/data-privacy.md)** - Handle sensitive data safely

---

## Related Documentation

- [F-079: Project Management System](../development/roadmap/features/completed/F-079-project-management.md)
- [Experiment Reproducibility](../explanation/reproducibility.md)
- [Export Formats Reference](../reference/export-formats.md)
