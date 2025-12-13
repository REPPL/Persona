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
export GEMINI_API_KEY="..."
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

## Step 4: Create an Experiment

Create a new experiment to organise your work:

```bash
persona create experiment
```

You'll be prompted for:
- **Name:** `my-first-experiment`
- **Description:** `Learning how to use Persona`
- **Provider:** Select your configured provider
- **Model:** Select a model (e.g., gpt-4o)
- **Personas:** `3` (start small)

This creates:

```
experiments/
└── my-first-experiment/
    ├── config.yaml
    ├── data/
    └── outputs/
```

## Step 5: Add Sample Data

Copy some sample data to your experiment:

```bash
# Use the provided synthetic data
cp config/synthetic_data/*.csv experiments/my-first-experiment/data/
```

Or create your own `data.csv`:

```csv
respondent_id,feedback
1,"I love the mobile app but wish it had offline mode"
2,"The web interface is confusing, too many options"
3,"Great for power users but not beginner friendly"
4,"I use it daily for work, essential tool"
5,"Would recommend but needs better documentation"
```

## Step 6: Generate Personas

Run the generation:

```bash
persona generate --from my-first-experiment
```

**What happens:**
1. Cost estimate is shown
2. You confirm to proceed
3. Data is sent to the LLM
4. Personas are generated
5. Results are saved

**Expected output:**

```
Generating personas from my-first-experiment

Cost Estimate
───────────────────────────────────
Input tokens:  ~1,200
Output tokens: ~2,000
Estimated cost: $0.08

Proceed? [Y/n]: y

Generating... ━━━━━━━━━━━━━━━━━━━━ 100%

✓ Generated 3 personas
  Output: experiments/my-first-experiment/outputs/20241213_143022/
```

## Step 7: Review Results

Navigate to the output folder and examine the results:

```bash
cd experiments/my-first-experiment/outputs/20241213_143022/
ls -la
```

**Output structure:**

```
20241213_143022/
├── metadata.json      # Generation details
├── prompt.json        # Template used
├── files.txt          # Input files
├── full_output.txt    # Complete LLM response
└── personas/
    ├── 01/
    │   ├── persona.txt   # Human-readable
    │   └── persona.json  # Structured data
    ├── 02/
    │   └── ...
    └── 03/
        └── ...
```

**Read a persona:**

```bash
cat personas/01/persona.txt
```

**Example output:**

```
# Sarah - The Mobile Professional

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
- ...
```

## What's Next?

You've completed the basics! Here's what to explore:

### Use Different Providers

```bash
persona generate --from my-first-experiment --vendor anthropic --model claude-3-sonnet
```

### Adjust Persona Count

Edit `experiments/my-first-experiment/config.yaml`:

```yaml
personas:
  count: 5
```

### Process Your Own Data

Add your research data to `experiments/my-first-experiment/data/` and regenerate.

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
ls experiments/my-first-experiment/data/

# Ensure supported formats: .csv, .json, .txt, .md
```

### "Rate limit exceeded"

Wait a moment and try again, or switch to a different provider.

---

## Related Documentation

- [Use Cases](../use-cases/)
- [How-To Guides](../guides/)
- [CLI Reference](../reference/)
