# Manual Testing Guide

This directory contains manual testing scripts for each Persona release. These scripts enable human verification of functionality that automated tests cannot fully cover.

## Purpose

Manual testing serves as the final verification layer in Persona's testing pyramid:

```
                    ┌─────────────────┐
                    │  Manual Tests   │  ← You are here
                    │  (This guide)   │
                    └────────┬────────┘
               ┌─────────────┴─────────────┐
               │    Integration Tests      │
               │    (tests/integration/)   │
               └─────────────┬─────────────┘
          ┌──────────────────┴──────────────────┐
          │           Unit Tests                │
          │        (tests/unit/)                │
          └─────────────────────────────────────┘
```

## Test Scripts by Version

| Version | Script | Status |
|---------|--------|--------|
| v0.1.0 | [v0.1.0_test_script.md](v0.1.0_test_script.md) | Pending |
| v0.2.0 | v0.2.0_test_script.md | Not started |
| v0.3.0 | v0.3.0_test_script.md | Not started |

*Scripts are created when each version is implemented.*

## Testing Workflow

### For Users

1. **Checkout the version to test**:
   ```bash
   git checkout v0.1.0
   ```

2. **Create a fresh virtual environment**:
   ```bash
   python3.12 -m venv .venv-test
   source .venv-test/bin/activate
   ```

3. **Install Persona**:
   ```bash
   pip install -e .
   ```

4. **Follow the test script**:
   - Open the relevant `vX.Y.Z_test_script.md`
   - Execute each test in order
   - Record results (pass/fail)
   - Copy console output for failed tests

5. **Share results**:
   - Provide console output to Claude for review
   - Note any unexpected behaviour

### For Developers

When implementing a new version:

1. Create the test script at start of implementation
2. Add tests as features are completed
3. Each test should include:
   - Clear command to run
   - Expected output description
   - Pass/fail criteria

## Test Script Format

Each test script follows this structure:

```markdown
# Manual Test Script: vX.Y.Z

## Prerequisites
- Required Python version
- Required environment setup
- Required API keys (if any)

## Installation
Step-by-step installation commands

## Test 1: [Feature Name]
**Command:**
\`\`\`bash
persona <command>
\`\`\`

**Expected Result:**
Description of what should happen

**Pass Criteria:**
- [ ] Criterion 1
- [ ] Criterion 2

---

## Test 2: [Next Feature]
...
```

## Reporting Issues

When a test fails:

1. **Capture full output**:
   ```bash
   persona <command> 2>&1 | tee test_output.txt
   ```

2. **Note environment details**:
   - Operating system
   - Python version (`python --version`)
   - Persona version (`persona --version`)

3. **Share with Claude**:
   - Paste the test output
   - Describe expected vs actual behaviour
   - Note any error messages

## API Key Requirements

Some tests require real API keys. Tests are designed to:
- Use minimal tokens (cost-effective)
- Work with any single provider
- Fall back gracefully without keys

### Setting Up API Keys

```bash
export OPENAI_API_KEY="your-key-here"
# OR
export ANTHROPIC_API_KEY="your-key-here"
# OR
export GOOGLE_API_KEY="your-key-here"
```

### Mock Mode

For testing without API keys, use mock mode where available:
```bash
persona generate --from data/ --mock
```

---

## Related Documentation

- [Testing Guide](../../docs/development/testing.md) - Full testing documentation
- [Test Fixtures](../fixtures/README.md) - How to use test fixtures
