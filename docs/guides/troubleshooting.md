# Troubleshooting Common Issues

A problem-solving guide for resolving common Persona issues.

## Goal

Quickly diagnose and fix common issues with installation, configuration, and generation.

## Quick Diagnostics

Run the health check first:

```bash
persona check
```

This identifies most common issues automatically.

## API Key Issues

### "API key not found"

**Symptom:**
```
Error: No API key configured for provider 'openai'
```

**Diagnosis:**
```bash
# Check if key is set
echo $OPENAI_API_KEY

# Check Persona's view
persona check
```

**Solutions:**

1. **Set environment variable:**
   ```bash
   export OPENAI_API_KEY="sk-..."
   ```

2. **Add to shell profile:**
   ```bash
   # Add to ~/.bashrc or ~/.zshrc
   echo 'export OPENAI_API_KEY="sk-..."' >> ~/.zshrc
   source ~/.zshrc
   ```

3. **Use config file:**
   ```bash
   persona config set api.openai.key "sk-..."
   ```

### "Invalid API key"

**Symptom:**
```
Error: Authentication failed. Invalid API key.
```

**Diagnosis:**
- Key may be expired, revoked, or mistyped

**Solutions:**

1. **Verify key format:**
   - OpenAI: starts with `sk-`
   - Anthropic: starts with `sk-ant-`
   - Google: alphanumeric string

2. **Check key in provider dashboard:**
   - [OpenAI Keys](https://platform.openai.com/api-keys)
   - [Anthropic Keys](https://console.anthropic.com/settings/keys)
   - [Google AI Keys](https://makersuite.google.com/app/apikey)

3. **Generate new key** if expired

### "Insufficient credits/quota"

**Symptom:**
```
Error: Quota exceeded. Please check your billing.
```

**Solutions:**

1. Check billing in provider dashboard
2. Add payment method or credits
3. Switch to different provider temporarily

## Rate Limiting

### "Rate limit exceeded"

**Symptom:**
```
Error: Rate limit exceeded. Please retry after X seconds.
```

**Automatic handling:**
Persona automatically retries with exponential backoff.

**Manual solutions:**

1. **Wait and retry:**
   ```bash
   # Wait 60 seconds, then retry
   sleep 60 && persona generate --from my-experiment
   ```

2. **Reduce concurrent requests:**
   ```bash
   persona config set generation.concurrency 1
   ```

3. **Use different model:**
   ```bash
   persona generate --from my-experiment --model gpt-3.5-turbo
   ```

4. **Switch provider:**
   ```bash
   persona generate --from my-experiment --provider anthropic
   ```

## Data Format Issues

### "No data files found"

**Symptom:**
```
Error: No supported data files found in experiments/my-experiment/data/
```

**Diagnosis:**
```bash
# Check directory contents
ls -la experiments/my-experiment/data/
```

**Solutions:**

1. **Verify file location:**
   Files must be in `data/` subdirectory

2. **Check file extensions:**
   Supported: `.csv`, `.json`, `.md`, `.yaml`, `.yml`, `.txt`

3. **Create data directory:**
   ```bash
   mkdir -p experiments/my-experiment/data/
   cp your-data.csv experiments/my-experiment/data/
   ```

### "Unable to parse file"

**Symptom:**
```
Error: Failed to parse interviews.csv: Invalid CSV format
```

**Diagnosis:**
```bash
# Preview file
head -5 experiments/my-experiment/data/interviews.csv

# Check encoding
file experiments/my-experiment/data/interviews.csv
```

**Solutions:**

1. **Fix encoding:**
   ```bash
   iconv -f ISO-8859-1 -t UTF-8 input.csv > output.csv
   ```

2. **Validate CSV:**
   ```bash
   # Check for common issues
   csvlint input.csv
   ```

3. **Check quotes and escaping:**
   Ensure text fields with commas are quoted:
   ```csv
   id,feedback
   1,"Good, but needs work"
   ```

### "Empty data file"

**Symptom:**
```
Warning: File interviews.csv contains no content
```

**Solutions:**

1. Verify file has content (not just headers)
2. Remove empty files from data directory
3. Check file permissions

## Generation Issues

### "Generation timeout"

**Symptom:**
```
Error: Request timed out after 120 seconds
```

**Solutions:**

1. **Increase timeout:**
   ```bash
   persona config set generation.timeout 300
   ```

2. **Reduce data size:**
   Split large files into smaller chunks

3. **Use faster model:**
   ```bash
   persona generate --from my-experiment --model claude-3-haiku
   ```

### "Poor quality output"

**Symptom:**
Personas are generic, shallow, or don't reflect source data

**Diagnosis:**
```bash
# Validate output quality
persona validate <persona-id>
```

**Solutions:**

1. **Add more source data:**
   - Include more interviews/responses
   - Add variety of perspectives

2. **Improve data quality:**
   - Remove noise and filler
   - Include specific quotes
   - See [Preparing Data](preparing-data.md)

3. **Try different model:**
   ```bash
   persona generate --from my-experiment --model claude-3-opus
   ```

4. **Adjust persona count:**
   Fewer personas = more depth each
   ```bash
   persona generate --from my-experiment --count 3
   ```

### "Personas too similar"

**Symptom:**
Generated personas overlap significantly

**Solutions:**

1. **Reduce persona count:**
   ```bash
   persona generate --from my-experiment --count 3
   ```

2. **Add segment hints:**
   Include participant categories in data

3. **Use clustering:**
   ```bash
   persona cluster --from my-experiment
   ```

## Installation Issues

### "Python version too old"

**Symptom:**
```
Error: Python 3.12 or higher required. Found: 3.9.x
```

**Solutions:**

1. **Install Python 3.12:**
   ```bash
   # macOS with Homebrew
   brew install python@3.12

   # Ubuntu/Debian
   sudo apt install python3.12
   ```

2. **Use pyenv:**
   ```bash
   pyenv install 3.12
   pyenv local 3.12
   ```

3. **Verify version:**
   ```bash
   python3.12 --version
   ```

### "Module not found"

**Symptom:**
```
ModuleNotFoundError: No module named 'persona'
```

**Solutions:**

1. **Activate virtual environment:**
   ```bash
   source .venv/bin/activate
   ```

2. **Reinstall package:**
   ```bash
   pip install -e ".[all]"
   ```

3. **Verify installation:**
   ```bash
   pip list | grep persona
   ```

### "Permission denied"

**Symptom:**
```
PermissionError: [Errno 13] Permission denied
```

**Solutions:**

1. **Fix directory permissions:**
   ```bash
   chmod -R u+w experiments/
   ```

2. **Don't use sudo with pip:**
   Use virtual environment instead

3. **Check disk space:**
   ```bash
   df -h
   ```

## Output Issues

### "Output folder not created"

**Symptom:**
Generation completes but no output folder exists

**Diagnosis:**
```bash
ls -la experiments/my-experiment/outputs/
```

**Solutions:**

1. **Check permissions:**
   ```bash
   chmod u+w experiments/my-experiment/
   ```

2. **Verify experiment exists:**
   ```bash
   persona experiment list
   ```

3. **Manual output directory:**
   ```bash
   persona generate --from my-experiment --output ./custom-output/
   ```

### "Cannot read output files"

**Symptom:**
Output files exist but can't be opened

**Solutions:**

1. **Check file encoding:**
   All outputs are UTF-8

2. **Use appropriate viewer:**
   - `.json` - JSON viewer or text editor
   - `.md` - Markdown viewer
   - `.txt` - Text editor

3. **Verify file integrity:**
   ```bash
   cat experiments/my-experiment/outputs/latest/personas/01/persona.json | python -m json.tool
   ```

## Getting Help

If these solutions don't resolve your issue:

### Collect Diagnostic Information

```bash
# Full system check
persona check --verbose > diagnostics.txt

# Add version info
persona --version >> diagnostics.txt

# Add Python environment
pip list >> diagnostics.txt
```

### Report an Issue

1. Search [existing issues](https://github.com/REPPL/Persona/issues)
2. If not found, [create new issue](https://github.com/REPPL/Persona/issues/new)
3. Include:
   - Error message (full text)
   - Steps to reproduce
   - Diagnostic information
   - Data sample (anonymised)

---

## Related Documentation

- [Getting Started](../tutorials/01-getting-started.md)
- [CLI Reference](../reference/cli-reference.md)
- [F-009: Health Check](../development/roadmap/features/completed/F-009-health-check.md)
