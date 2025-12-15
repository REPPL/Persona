# PII Scan Checklist

**CRITICAL: Run this checklist before EVERY commit. No exceptions.**

This checklist ensures no Personal Identifiable Information (PII) is committed to the repository.

---

## Automated Scans

Run ALL of these commands and verify ZERO matches before committing:

### 1. Personal Paths Scan

```bash
# Check for home directory paths
grep -rn "/Users/" src/ docs/ tests/ --include="*.py" --include="*.md" --include="*.yaml" --include="*.toml" --include="*.json" 2>/dev/null | grep -v ".venv" | grep -v "node_modules"

grep -rn "/home/" src/ docs/ tests/ --include="*.py" --include="*.md" --include="*.yaml" --include="*.toml" --include="*.json" 2>/dev/null | grep -v ".venv" | grep -v "node_modules"

# Expected: No output (zero matches)
```

**Pass Criteria:**
- [ ] No `/Users/<username>/` paths found
- [ ] No `/home/<username>/` paths found
- [ ] No `C:\Users\<username>\` paths found

### 2. Email Address Scan

```bash
# Check for email addresses (excluding safe domains)
grep -rnoE "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}" src/ docs/ tests/ --include="*.py" --include="*.md" 2>/dev/null | grep -v "@example.com" | grep -v "@anthropic.com" | grep -v "@users.noreply.github.com" | grep -v ".venv"

# Expected: No output (zero matches)
```

**Pass Criteria:**
- [ ] No personal email addresses
- [ ] Only @example.com for examples
- [ ] Only @anthropic.com for AI attribution
- [ ] Only @users.noreply.github.com for git

### 3. Author/Maintainer Fields

```bash
# Check for author fields that might contain real names
grep -rniE "(author|maintained by|created by|written by):" src/ docs/ tests/ --include="*.py" --include="*.md" 2>/dev/null | grep -v "Co-Authored-By: Claude"

# Expected: No output (zero matches)
```

**Pass Criteria:**
- [ ] No "Author:" fields with real names
- [ ] No "Maintained by:" fields
- [ ] No "Created by:" fields with names
- [ ] Only AI attribution allowed

### 4. API Key Patterns

```bash
# Check for potential API keys
grep -rnoE "(sk-[a-zA-Z0-9]{20,}|api[_-]?key\s*[:=]\s*['\"][^'\"]+['\"])" src/ docs/ tests/ --include="*.py" --include="*.md" --include="*.yaml" --include="*.env*" 2>/dev/null | grep -v ".env.example"

# Expected: No output (zero matches)
```

**Pass Criteria:**
- [ ] No API keys in source code
- [ ] No API keys in documentation
- [ ] Keys only in .env.example with placeholders

### 5. Hardcoded Secrets

```bash
# Check for password/secret patterns
grep -rniE "(password|secret|token)\s*[:=]\s*['\"][^'\"]+['\"]" src/ docs/ tests/ --include="*.py" --include="*.yaml" --include="*.json" 2>/dev/null | grep -v "example" | grep -v "placeholder" | grep -v "your-"

# Expected: No output (zero matches)
```

**Pass Criteria:**
- [ ] No hardcoded passwords
- [ ] No hardcoded secrets
- [ ] Only placeholder values

---

## Manual Verification

### 6. Git Config Check

```bash
# Verify git identity
git config user.name
git config user.email

# Expected: GitHub username (not real name)
# Expected: <username>@users.noreply.github.com
```

**Pass Criteria:**
- [ ] user.name is GitHub username
- [ ] user.email is noreply address

### 7. Staged Files Review

```bash
# Review all staged files
git diff --cached --name-only

# For each file, verify no PII
git diff --cached | grep -E "(\/Users\/|\/home\/|@[a-z]+\.[a-z]+)" | grep -v "@example.com" | grep -v "@anthropic.com"
```

**Pass Criteria:**
- [ ] Each staged file manually reviewed
- [ ] No PII in diff output

### 8. New Files Deep Check

For any NEW files being added:

```bash
# List new files
git diff --cached --name-only --diff-filter=A

# For each new file, run individual scan
cat <new_file> | grep -E "(\/Users\/|\/home\/|@[a-z]+\.)" | grep -v "@example" | grep -v "@anthropic"
```

**Pass Criteria:**
- [ ] Each new file individually scanned
- [ ] No PII in new files

---

## Documentation-Specific Checks

### 9. Example Paths

```bash
# Verify example paths use safe patterns
grep -rn "path" docs/ --include="*.md" | grep -v "\$HOME" | grep -v "~/" | grep -v "./relative" | grep -v "example" | head -20
```

**Pass Criteria:**
- [ ] Examples use `~/` or `$HOME`
- [ ] No absolute paths with usernames
- [ ] Relative paths where appropriate

### 10. Schema $id Fields

```bash
# Check JSON schema files for personal domains
grep -rn '"\$id"' src/ docs/ --include="*.json" --include="*.schema.json"

# Expected: No personal domain URLs
```

**Pass Criteria:**
- [ ] No personal domains in $id
- [ ] Use relative references or omit

---

## Pre-Commit Command

Run this comprehensive scan before every commit:

```bash
# Full PII scan - must return empty
echo "=== PII SCAN ===" && \
grep -rn "/Users/\|/home/" src/ docs/ tests/ --include="*.py" --include="*.md" 2>/dev/null | grep -v ".venv" && \
grep -rnoE "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}" src/ docs/ tests/ 2>/dev/null | grep -v "@example.com\|@anthropic.com\|@users.noreply.github.com" | grep -v ".venv" && \
grep -rniE "(author|maintained by):" src/ docs/ tests/ 2>/dev/null | grep -v "Co-Authored-By" && \
echo "=== SCAN COMPLETE ==="

# If ANY output appears between the markers, DO NOT COMMIT
```

---

## Remediation Actions

If PII is found:

1. **Personal paths**: Replace with `~/`, `$HOME/`, or `./`
2. **Email addresses**: Replace with `user@example.com`
3. **Author fields**: Remove or use "See git history"
4. **API keys**: Move to environment variables
5. **Real names**: Replace with GitHub username

---

## Sign-Off

Before committing, confirm:

- [ ] All automated scans return zero matches
- [ ] Git identity verified
- [ ] Staged files manually reviewed
- [ ] New files individually checked
- [ ] Documentation examples use safe paths

**Scanned by:** ________________
**Date:** ________________
**Commit hash:** ________________
