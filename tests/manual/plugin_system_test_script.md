# Manual Test Script: Plugin System (F-107)

This script verifies the plugin system functionality. Execute tests in order and record results.

## Prerequisites

- Python 3.12+
- Persona installed with `pip install -e ".[all]"`

## Setup

```bash
# 1. Activate virtual environment
source .venv-test/bin/activate  # On Windows: .venv-test\Scripts\activate

# 2. Verify installation
persona --version
```

**Expected:** Shows Persona version

---

## Test 1: Plugin Help

**Command:**
```bash
persona plugin --help
```

**Expected:** Shows help text with subcommands: list, info, summary, check, reload

**Pass Criteria:**
- [ ] Help text displays correctly
- [ ] All subcommands documented
- [ ] No import errors

---

## Test 2: List All Plugins

**Command:**
```bash
persona plugin list
```

**Expected:** Table showing all registered plugins with name, type, description, version, status

**Pass Criteria:**
- [ ] Table displays correctly
- [ ] Built-in formatters shown (json, markdown, text)
- [ ] Built-in loaders shown (csv, json, yaml, etc.)
- [ ] Built-in providers shown (openai, anthropic, gemini)
- [ ] Built-in validator shown (persona)
- [ ] All plugins show "builtin" status

---

## Test 3: Filter by Type

**Command:**
```bash
persona plugin list --type formatter
```

**Expected:** Only formatter plugins shown

**Pass Criteria:**
- [ ] Only formatters displayed
- [ ] json, markdown, text shown
- [ ] No loaders or providers shown

---

## Test 4: JSON Output

**Command:**
```bash
persona plugin list --output json
```

**Expected:** Valid JSON array with plugin data

**Pass Criteria:**
- [ ] Output is valid JSON
- [ ] Contains name, type, description, version fields
- [ ] Can be piped to `jq` for processing

---

## Test 5: Plugin Info

**Command:**
```bash
persona plugin info json --type formatter
```

**Expected:** Detailed information panel for json formatter

**Pass Criteria:**
- [ ] Panel displays with plugin name
- [ ] Shows type, description, version
- [ ] Shows status (Enabled)
- [ ] Shows built-in status (Yes)

---

## Test 6: Plugin Summary

**Command:**
```bash
persona plugin summary
```

**Expected:** Summary panel and by-type breakdown table

**Pass Criteria:**
- [ ] Total plugins count shown
- [ ] Enabled/disabled counts shown
- [ ] Built-in/external counts shown
- [ ] By-type table with formatter, loader, provider, validator rows

---

## Test 7: Check Plugins

**Command:**
```bash
persona plugin check
```

**Expected:** All plugins verified as loadable

**Pass Criteria:**
- [ ] Each plugin shows green checkmark
- [ ] Success message at end
- [ ] Exit code 0

---

## Test 8: Check Specific Type

**Command:**
```bash
persona plugin check --type loader
```

**Expected:** Only loaders verified

**Pass Criteria:**
- [ ] Only loader plugins checked
- [ ] All show success

---

## Test 9: Reload Plugins

**Command:**
```bash
persona plugin reload
```

**Expected:** Plugins reloaded successfully

**Pass Criteria:**
- [ ] Shows "Reloading plugins..." message
- [ ] Shows total count after reload
- [ ] No errors

---

## Test 10: Plugin Info Not Found

**Command:**
```bash
persona plugin info nonexistent --type formatter
echo "Exit code: $?"
```

**Expected:** Error message and exit code 1

**Pass Criteria:**
- [ ] Error message indicates plugin not found
- [ ] Exit code is 1

---

## Test 11: Invalid Type

**Command:**
```bash
persona plugin list --type invalid
echo "Exit code: $?"
```

**Expected:** Error message with valid types

**Pass Criteria:**
- [ ] Error message shows invalid type
- [ ] Lists valid types (formatter, loader, provider, validator)
- [ ] Exit code is 1

---

## Test 12: Python API Usage

**Command:**
```python
from persona.core.plugins import get_plugin_manager, PluginType

manager = get_plugin_manager()
summary = manager.get_summary()

print(f"Total plugins: {summary['total']}")
print(f"By type: {list(summary['by_type'].keys())}")

# Get a specific plugin
formatter = manager.get_plugin(PluginType.FORMATTER, "json")
print(f"Formatter class: {type(formatter)}")
```

**Expected:** API works correctly

**Pass Criteria:**
- [ ] No import errors
- [ ] Summary returns expected structure
- [ ] Can get plugin instances

---

## Cleanup

No cleanup required for plugin system tests.

---

## Results Summary

| Test | Status |
|------|--------|
| Test 1: Help | [ ] |
| Test 2: List All | [ ] |
| Test 3: Filter by Type | [ ] |
| Test 4: JSON Output | [ ] |
| Test 5: Plugin Info | [ ] |
| Test 6: Summary | [ ] |
| Test 7: Check Plugins | [ ] |
| Test 8: Check Type | [ ] |
| Test 9: Reload | [ ] |
| Test 10: Not Found | [ ] |
| Test 11: Invalid Type | [ ] |
| Test 12: Python API | [ ] |

**Tested by:** ________________
**Date:** ________________
**Notes:**
