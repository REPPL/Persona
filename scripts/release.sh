#!/bin/bash
# Release Script for Persona
#
# Automates the release process with safety checks.
#
# Usage: ./scripts/release.sh [major|minor|patch]
#
# What it does:
#   1. Verifies clean git state
#   2. Verifies on main branch
#   3. Verifies up-to-date with remote
#   4. Runs tests
#   5. Runs PII scan
#   6. Calculates new version
#   7. Updates pyproject.toml
#   8. Creates commit and tag
#   9. Prints push instructions
#
# Options:
#   --dry-run    Show what would happen without making changes
#
# Exit codes:
#   0: Success
#   1: Pre-flight check failed
#   2: Release aborted by user

set -e

# Colours for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Colour

# Print with colour
print_step() {
    printf "${BLUE}==>${NC} %s\n" "$1"
}

print_success() {
    printf "${GREEN}[OK]${NC} %s\n" "$1"
}

print_warning() {
    printf "${YELLOW}[WARN]${NC} %s\n" "$1"
}

print_error() {
    printf "${RED}[ERROR]${NC} %s\n" "$1"
}

# Parse arguments
DRY_RUN=false
BUMP_TYPE=""

for arg in "$@"; do
    case $arg in
        --dry-run)
            DRY_RUN=true
            ;;
        major|minor|patch)
            BUMP_TYPE="$arg"
            ;;
        *)
            print_error "Unknown argument: $arg"
            echo "Usage: $0 [major|minor|patch] [--dry-run]"
            exit 1
            ;;
    esac
done

if [ -z "$BUMP_TYPE" ]; then
    print_error "Version bump type required"
    echo "Usage: $0 [major|minor|patch] [--dry-run]"
    echo ""
    echo "  major  - Breaking changes (1.0.0 -> 2.0.0)"
    echo "  minor  - New features (1.0.0 -> 1.1.0)"
    echo "  patch  - Bug fixes (1.0.0 -> 1.0.1)"
    exit 1
fi

# Header
echo ""
echo "=========================================="
echo "         Persona Release Script          "
echo "=========================================="
if [ "$DRY_RUN" = true ]; then
    printf "${YELLOW}DRY RUN MODE - No changes will be made${NC}\n"
fi
echo ""

# 1. Verify clean git state
print_step "Checking git state..."

if [ -n "$(git status --porcelain)" ]; then
    print_error "Working directory is not clean"
    echo ""
    git status --short
    echo ""
    echo "Commit or stash your changes first."
    exit 1
fi
print_success "Working directory is clean"

# 2. Verify on main branch
print_step "Checking branch..."

CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    print_error "Not on main branch (currently on: $CURRENT_BRANCH)"
    echo "Switch to main branch: git checkout main"
    exit 1
fi
print_success "On main branch"

# 3. Verify up-to-date with remote
print_step "Checking remote sync..."

git fetch origin main --quiet
LOCAL_HASH=$(git rev-parse HEAD)
REMOTE_HASH=$(git rev-parse origin/main)

if [ "$LOCAL_HASH" != "$REMOTE_HASH" ]; then
    print_error "Local main is not in sync with origin/main"
    echo "Pull latest changes: git pull origin main"
    exit 1
fi
print_success "Up-to-date with remote"

# 4. Run tests
print_step "Running tests..."

if ! pytest tests/ -m "not real_api" --quiet; then
    print_error "Tests failed"
    exit 1
fi
print_success "All tests passed"

# 5. Run PII scan
print_step "Running PII scan..."

if ! ./scripts/pii_scan.sh > /dev/null 2>&1; then
    print_error "PII scan failed"
    echo "Run './scripts/pii_scan.sh' for details"
    exit 1
fi
print_success "PII scan passed"

# 6. Calculate new version
print_step "Calculating version..."

# Get current version from pyproject.toml
CURRENT_VERSION=$(grep -m1 'version = ' pyproject.toml | cut -d'"' -f2)

# Parse version components
IFS='.' read -r MAJOR MINOR PATCH <<< "$CURRENT_VERSION"

# Calculate new version
case $BUMP_TYPE in
    major)
        NEW_VERSION="$((MAJOR + 1)).0.0"
        ;;
    minor)
        NEW_VERSION="${MAJOR}.$((MINOR + 1)).0"
        ;;
    patch)
        NEW_VERSION="${MAJOR}.${MINOR}.$((PATCH + 1))"
        ;;
esac

print_success "Version: $CURRENT_VERSION -> $NEW_VERSION"

# 7. Confirm with user
echo ""
echo "=========================================="
echo "            Release Summary              "
echo "=========================================="
echo ""
echo "  Version bump: $BUMP_TYPE"
echo "  Current:      v$CURRENT_VERSION"
echo "  New:          v$NEW_VERSION"
echo ""

if [ "$DRY_RUN" = true ]; then
    echo "DRY RUN - No changes made"
    exit 0
fi

read -p "Proceed with release? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_warning "Release aborted"
    exit 2
fi

# 8. Update pyproject.toml
print_step "Updating version in pyproject.toml..."

# POSIX-compatible sed (works on both macOS and Linux)
sed -i.bak "s/version = \"$CURRENT_VERSION\"/version = \"$NEW_VERSION\"/" pyproject.toml
rm pyproject.toml.bak

print_success "Version updated"

# 9. Create commit
print_step "Creating release commit..."

git add pyproject.toml
git commit -m "chore(release): v$NEW_VERSION

Release version $NEW_VERSION

Changes since v$CURRENT_VERSION:
$(git log --oneline v$CURRENT_VERSION..HEAD 2>/dev/null || echo "  - Initial release")
"

print_success "Commit created"

# 10. Create tag
print_step "Creating tag..."

git tag -a "v$NEW_VERSION" -m "Release v$NEW_VERSION"

print_success "Tag v$NEW_VERSION created"

# Success message
echo ""
echo "=========================================="
echo "         Release Ready to Push           "
echo "=========================================="
echo ""
echo "To complete the release, run:"
echo ""
printf "  ${BLUE}git push origin main${NC}\n"
printf "  ${BLUE}git push origin v$NEW_VERSION${NC}\n"
echo ""
echo "Or push both at once:"
echo ""
printf "  ${BLUE}git push origin main --tags${NC}\n"
echo ""
print_warning "Remember to update CHANGELOG.md if needed"
echo ""
