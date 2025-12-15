#!/bin/bash
# PII Scan Script for Persona Project
# Run this BEFORE every commit to ensure no PII is included
#
# Usage: ./scripts/pii_scan.sh [path]
#   path: Optional path to scan (defaults to src/ docs/ tests/)
#
# Exit codes:
#   0: No PII found
#   1: PII found - DO NOT COMMIT

set -e

# Colours for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Colour

ERRORS=0
WARNINGS=0

# Default paths to scan
SCAN_PATHS="${1:-src/ docs/ tests/}"

echo "=========================================="
echo "       PII SCAN - Persona Project         "
echo "=========================================="
echo ""

# Function to report error
report_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    ((ERRORS++))
}

# Function to report warning
report_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
    ((WARNINGS++))
}

# Function to report success
report_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

# 1. Check for personal paths
echo "Scanning for personal paths..."
PERSONAL_PATHS=$(grep -rn "/Users/\|/home/" $SCAN_PATHS --include="*.py" --include="*.md" --include="*.yaml" --include="*.toml" --include="*.json" 2>/dev/null | grep -v ".venv" | grep -v "node_modules" | grep -v "__pycache__" || true)

if [ -n "$PERSONAL_PATHS" ]; then
    report_error "Personal paths found:"
    echo "$PERSONAL_PATHS"
    echo ""
else
    report_success "No personal paths found"
fi

# 2. Check for email addresses
echo ""
echo "Scanning for email addresses..."
EMAIL_MATCHES=$(grep -rnoE "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}" $SCAN_PATHS --include="*.py" --include="*.md" 2>/dev/null | grep -v "@example.com" | grep -v "@anthropic.com" | grep -v "@users.noreply.github.com" | grep -v ".venv" || true)

if [ -n "$EMAIL_MATCHES" ]; then
    report_error "Personal email addresses found:"
    echo "$EMAIL_MATCHES"
    echo ""
else
    report_success "No personal email addresses found"
fi

# 3. Check for author/maintainer fields
echo ""
echo "Scanning for author fields..."
AUTHOR_MATCHES=$(grep -rniE "(author|maintained by|created by|written by):" $SCAN_PATHS --include="*.py" --include="*.md" 2>/dev/null | grep -v "Co-Authored-By: Claude" | grep -v ".venv" || true)

if [ -n "$AUTHOR_MATCHES" ]; then
    report_warning "Author fields found (verify no real names):"
    echo "$AUTHOR_MATCHES"
    echo ""
else
    report_success "No author fields found"
fi

# 4. Check for API keys
echo ""
echo "Scanning for API keys..."
API_KEY_MATCHES=$(grep -rnoE "(sk-[a-zA-Z0-9]{20,}|api[_-]?key\s*[:=]\s*['\"][^'\"]{10,}['\"])" $SCAN_PATHS --include="*.py" --include="*.md" --include="*.yaml" --include="*.env*" 2>/dev/null | grep -v ".env.example" | grep -v "your-api-key" | grep -v "placeholder" || true)

if [ -n "$API_KEY_MATCHES" ]; then
    report_error "Potential API keys found:"
    echo "$API_KEY_MATCHES"
    echo ""
else
    report_success "No API keys found"
fi

# 5. Check for hardcoded secrets
echo ""
echo "Scanning for hardcoded secrets..."
SECRET_MATCHES=$(grep -rniE "(password|secret|token)\s*[:=]\s*['\"][^'\"]{8,}['\"]" $SCAN_PATHS --include="*.py" --include="*.yaml" --include="*.json" 2>/dev/null | grep -v "example" | grep -v "placeholder" | grep -v "your-" | grep -v "test-" | grep -v ".venv" || true)

if [ -n "$SECRET_MATCHES" ]; then
    report_warning "Potential secrets found (verify not real):"
    echo "$SECRET_MATCHES"
    echo ""
else
    report_success "No hardcoded secrets found"
fi

# 6. Check git config
echo ""
echo "Checking git configuration..."
GIT_NAME=$(git config user.name 2>/dev/null || echo "not set")
GIT_EMAIL=$(git config user.email 2>/dev/null || echo "not set")

echo "  Git user.name: $GIT_NAME"
echo "  Git user.email: $GIT_EMAIL"

if [[ "$GIT_EMAIL" != *"@users.noreply.github.com"* ]] && [[ "$GIT_EMAIL" != "not set" ]]; then
    report_warning "Git email is not a noreply address"
fi

# 7. Check staged files if in git repo
if git rev-parse --git-dir > /dev/null 2>&1; then
    echo ""
    echo "Checking staged files..."
    STAGED_PII=$(git diff --cached 2>/dev/null | grep -E "(\/Users\/|\/home\/|@[a-z]+\.[a-z]+)" | grep -v "@example.com" | grep -v "@anthropic.com" || true)

    if [ -n "$STAGED_PII" ]; then
        report_error "PII in staged changes:"
        echo "$STAGED_PII"
        echo ""
    else
        report_success "No PII in staged changes"
    fi
fi

# Summary
echo ""
echo "=========================================="
echo "                SUMMARY                   "
echo "=========================================="
echo -e "Errors:   ${RED}$ERRORS${NC}"
echo -e "Warnings: ${YELLOW}$WARNINGS${NC}"
echo ""

if [ $ERRORS -gt 0 ]; then
    echo -e "${RED}PII SCAN FAILED - DO NOT COMMIT${NC}"
    echo "Fix all errors before committing."
    exit 1
elif [ $WARNINGS -gt 0 ]; then
    echo -e "${YELLOW}PII SCAN PASSED WITH WARNINGS${NC}"
    echo "Review warnings before committing."
    exit 0
else
    echo -e "${GREEN}PII SCAN PASSED${NC}"
    echo "Safe to commit."
    exit 0
fi
