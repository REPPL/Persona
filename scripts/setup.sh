#!/bin/bash
# Developer Setup Script for Persona
#
# This script sets up a complete development environment.
#
# Usage: ./scripts/setup.sh
#
# Requirements:
#   - Python 3.12 or higher
#   - Git
#   - pip
#
# What it does:
#   1. Verifies Python version
#   2. Creates virtual environment
#   3. Installs all dependencies
#   4. Sets up pre-commit hooks
#   5. Creates .env from template
#   6. Verifies installation
#
# Exit codes:
#   0: Success
#   1: Python version too low
#   2: Installation failed

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

# Header
echo ""
echo "=========================================="
echo "       Persona Development Setup         "
echo "=========================================="
echo ""

# 1. Find Python
print_step "Checking Python version..."

# Try different Python commands
PYTHON=""
for cmd in python3.12 python3 python; do
    if command -v "$cmd" &> /dev/null; then
        version=$("$cmd" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
        major=$(echo "$version" | cut -d. -f1)
        minor=$(echo "$version" | cut -d. -f2)
        if [ "$major" -ge 3 ] && [ "$minor" -ge 12 ]; then
            PYTHON="$cmd"
            break
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    print_error "Python 3.12 or higher is required"
    echo "  Found versions:"
    for cmd in python3.12 python3 python; do
        if command -v "$cmd" &> /dev/null; then
            version=$("$cmd" --version 2>&1)
            echo "    $cmd: $version"
        fi
    done
    echo ""
    echo "  Install Python 3.12+ from https://www.python.org/"
    exit 1
fi

print_success "Using $PYTHON ($($PYTHON --version))"

# 2. Create virtual environment
print_step "Creating virtual environment..."

if [ -d ".venv" ]; then
    print_warning "Virtual environment already exists"
    read -p "  Recreate? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf .venv
        $PYTHON -m venv .venv
        print_success "Virtual environment recreated"
    fi
else
    $PYTHON -m venv .venv
    print_success "Virtual environment created"
fi

# 3. Activate virtual environment
print_step "Activating virtual environment..."

# shellcheck disable=SC1091
source .venv/bin/activate
print_success "Virtual environment activated"

# 4. Upgrade pip
print_step "Upgrading pip..."
python -m pip install --upgrade pip --quiet
print_success "pip upgraded"

# 5. Install dependencies
print_step "Installing dependencies (this may take a few minutes)..."

if pip install -e ".[all]" --quiet; then
    print_success "Dependencies installed"
else
    print_error "Failed to install dependencies"
    exit 2
fi

# 6. Install pre-commit hooks
print_step "Setting up pre-commit hooks..."

if command -v pre-commit &> /dev/null; then
    pre-commit install --quiet
    print_success "Pre-commit hooks installed"
else
    print_warning "pre-commit not found - skipping hooks"
fi

# 7. Create .env file
print_step "Checking environment configuration..."

if [ -f ".env" ]; then
    print_warning ".env file already exists - not overwriting"
else
    if [ -f ".env.example" ]; then
        cp .env.example .env
        print_success ".env created from template"
        print_warning "Edit .env and add your API keys"
    else
        # Create minimal .env
        cat > .env << 'EOF'
# Persona Environment Configuration
# Add your API keys below

# At least one provider is required
# ANTHROPIC_API_KEY=sk-ant-your-key-here
# OPENAI_API_KEY=sk-your-key-here
# GOOGLE_API_KEY=AIza-your-key-here

# Optional: Set default provider
# PERSONA_DEFAULT_PROVIDER=anthropic

# Optional: Cost controls
# PERSONA_BUDGET_WARNING=5.00
# PERSONA_BUDGET_LIMIT=20.00
EOF
        print_success ".env template created"
        print_warning "Edit .env and add your API keys"
    fi
fi

# 8. Verify installation
print_step "Verifying installation..."

if persona --version &> /dev/null; then
    VERSION=$(persona --version)
    print_success "Persona installed: $VERSION"
else
    print_error "Installation verification failed"
    exit 2
fi

# 9. Run health check
print_step "Running health check..."

if persona check &> /dev/null; then
    print_success "Health check passed"
else
    print_warning "Health check failed - check your API keys in .env"
fi

# Summary
echo ""
echo "=========================================="
echo "            Setup Complete!              "
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "  1. Activate the virtual environment:"
printf "     ${BLUE}source .venv/bin/activate${NC}\n"
echo ""
echo "  2. Add your API keys to .env:"
printf "     ${BLUE}nano .env${NC}\n"
echo ""
echo "  3. Verify your setup:"
printf "     ${BLUE}persona check${NC}\n"
echo ""
echo "  4. Run tests:"
printf "     ${BLUE}make test${NC}\n"
echo ""
echo "Common commands:"
echo "  make help      - Show all available commands"
echo "  make test      - Run tests"
echo "  make lint      - Run linter"
echo "  make check     - Run all quality checks"
echo "  make docs      - Serve documentation"
echo ""
