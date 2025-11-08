#!/bin/bash
# ClearCraft Setup Script
# Automated installation and configuration

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     ClearCraft Setup Script          ║${NC}"
echo -e "${BLUE}║  Text Clarity Enhancement Tool       ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# Check Python version
echo -e "${YELLOW}[1/7]${NC} Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 is not installed${NC}"
    echo "Please install Python 3.10 or higher"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.10"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo -e "${RED}✗ Python $PYTHON_VERSION found, but $REQUIRED_VERSION or higher is required${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python $PYTHON_VERSION detected${NC}"

# Create virtual environment
echo -e "\n${YELLOW}[2/7]${NC} Creating virtual environment..."
if [ -d "venv" ]; then
    echo -e "${YELLOW}⚠ Virtual environment already exists${NC}"
    read -p "Remove and recreate? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf venv
        python3 -m venv venv
        echo -e "${GREEN}✓ Virtual environment recreated${NC}"
    else
        echo -e "${YELLOW}ℹ Using existing virtual environment${NC}"
    fi
else
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Activate virtual environment
echo -e "\n${YELLOW}[3/7]${NC} Activating virtual environment..."
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"

# Upgrade pip
echo -e "\n${YELLOW}[4/7]${NC} Upgrading pip..."
pip install --quiet --upgrade pip
echo -e "${GREEN}✓ pip upgraded${NC}"

# Install dependencies
echo -e "\n${YELLOW}[5/7]${NC} Installing dependencies..."
echo "This may take a few minutes..."
pip install --quiet -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Download spaCy model
echo -e "\n${YELLOW}[6/7]${NC} Downloading spaCy language model..."
python -m spacy download en_core_web_sm --quiet
echo -e "${GREEN}✓ spaCy model downloaded${NC}"

# Setup environment file
echo -e "\n${YELLOW}[7/7]${NC} Configuring environment..."
if [ ! -f ".env" ]; then
    cp .env.sample .env
    echo -e "${GREEN}✓ Created .env file from template${NC}"
    echo -e "${YELLOW}ℹ Edit .env to add your DeepInfra API token (optional)${NC}"
else
    echo -e "${YELLOW}⚠ .env file already exists, skipping${NC}"
fi

# Create necessary directories
mkdir -p .cache/huggingface .cache/sentence-transformers
echo -e "${GREEN}✓ Created cache directories${NC}"

# Success message
echo ""
echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║    Setup Complete! 🎉                 ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo ""
echo -e "  1. Activate the virtual environment:"
echo -e "     ${YELLOW}source venv/bin/activate${NC}"
echo ""
echo -e "  2. (Optional) Add DeepInfra API token to .env:"
echo -e "     ${YELLOW}nano .env${NC}"
echo ""
echo -e "  3. Start the web server:"
echo -e "     ${YELLOW}clearcraft server${NC}"
echo -e "     Then visit: ${BLUE}http://localhost:8000${NC}"
echo ""
echo -e "  4. Or try the demo:"
echo -e "     ${YELLOW}python examples/demo.py${NC}"
echo ""
echo -e "  5. Or use the CLI:"
echo -e "     ${YELLOW}clearcraft analyze --file examples/sample_complex.txt${NC}"
echo ""
echo -e "For more information, see ${BLUE}README.md${NC} and ${BLUE}USAGE.md${NC}"
echo ""
