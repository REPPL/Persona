# Getting Started with Persona

Learn how to generate your first personas from user research data.

## What You'll Learn

- Install and configure Persona
- Create your first experiment
- Generate personas from sample data
- Review and understand the output

## Prerequisites

- Python 3.12 or higher
- API key for at least one provider:
  - [OpenAI](https://platform.openai.com/api-keys)
  - [Anthropic](https://console.anthropic.com/settings/keys)
  - [Google AI](https://makersuite.google.com/app/apikey)

## Step 1: Installation

Clone the repository and set up your environment:

```bash
# Clone the repository
git clone https://github.com/REPPL/Persona.git
cd Persona

# Create virtual environment
python3.12 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e ".[all]"
```

## Step 2: Configuration

Set up your API key as an environment variable:

```bash
# OpenAI
export OPENAI_API_KEY="sk-..."

# Or Anthropic
export ANTHROPIC_API_KEY="sk-ant-..."

# Or Google Gemini
export GOOGLE_API_KEY="..."
```

**Tip:** Add these to your shell profile (`~/.bashrc`, `~/.zshrc`) for persistence.

## Step 3: Verify Installation

Check that everything is configured correctly:

```bash
persona check
```

**Expected output:**

```
System Check
───────────────────────────────────
Python      ✓ 3.12.x
Config      ✓ Valid

Providers
───────────────────────────────────
OpenAI      ✓ API key configured
            ✓ Models: gpt-4, gpt-4o
```

**Checkpoint:** At least one provider should show ✓.

## Step 4: Create a Project

Create a new project to organise your work:

```bash
persona project create my-first-project
```

This creates:

```
my-first-project/
├── persona.yaml
├── data/
├── output/
└── templates/
```

The `persona.yaml` file contains your project configuration with default settings.

## Step 5: Add Sample Data

Navigate to your project and add some sample data:

```bash
cd my-first-project
```

Create a `data/interviews.csv` file:

```csv
respondent_id,feedback
1,"I love the mobile app but wish it had offline mode"
2,"The web interface is confusing, too many options"
3,"Great for power users but not beginner friendly"
4,"I use it daily for work, essential tool"
5,"Would recommend but needs better documentation"
```

Or copy sample data from the examples:

```bash
cp ../examples/demo-project/data/*.csv data/
```

## Step 6: Generate Personas

Run the generation from within your project directory:

```bash
persona generate --from data/interviews.csv
```

**What happens:**
1. Data is loaded and tokenised
2. Cost estimate is shown
3. You confirm to proceed
4. Data is sent to the LLM
5. Personas are generated
6. Results are saved

**Expected output:**

```
Persona 1.7.5

Loading data from: data/interviews.csv
✓ Loaded 324 characters (89 tokens)

Generating 3 personas...
━━━━━━━━━━━━━━━━━━━━ 100%

✓ Generated 3 personas
✓ Saved to: output/20241213_143022/

Generated 3 personas:
  1. Sarah Chen (persona_001)
  2. James Wilson (persona_002)
  3. Maria Garcia (persona_003)
```

## Step 7: Review Results

Navigate to the output folder and examine the results:

```bash
cd output/20241213_143022/
ls -la
```

**Output structure:**

```
20241213_143022/
├── metadata.json         # Generation details
├── prompt.txt            # Prompt sent to LLM
├── personas.json         # All personas (structured)
├── persona_001.json      # Individual persona files
├── persona_001.txt
├── persona_002.json
├── persona_002.txt
├── persona_003.json
└── persona_003.txt
```

**Read a persona:**

```bash
cat persona_001.txt
```

**Example output:**

```
# Sarah Chen - The Mobile Professional

## Demographics
- Age: 32
- Role: Marketing Manager
- Tech proficiency: Intermediate

## Goals
- Complete tasks efficiently on the go
- Stay productive during commutes
- Access key features without internet

## Pain Points
- Frustration when offline
- Limited mobile functionality
- Needs better documentation
```

## What's Next?

You've completed the basics! Here's what to explore:

### Use Different Providers

```bash
persona generate --from data/interviews.csv --provider anthropic --model claude-sonnet-4-20250514
```

### Adjust Persona Count

Edit your project's `persona.yaml`:

```yaml
project:
  name: my-first-project

defaults:
  provider: anthropic
  count: 5
  workflow: default
```

Then generate with project defaults:

```bash
persona generate --from data/interviews.csv
```

### Process Your Own Data

Add your research data to the `data/` directory and regenerate.

## Troubleshooting

### "API key not found"

```bash
# Check your environment
echo $OPENAI_API_KEY

# Verify it's set correctly
persona check
```

### "No data files found"

```bash
# Check data directory
ls data/

# Ensure supported formats: .csv, .json, .txt, .md
```

### "Rate limit exceeded"

Wait a moment and try again, or switch to a different provider.

---

## Related Documentation

- [Use Cases](../use-cases/)
- [How-To Guides](../guides/)
- [CLI Reference](../reference/)
