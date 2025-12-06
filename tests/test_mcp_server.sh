#!/bin/bash

# Test script for FastQC & MultiQC MCP Server
# This script helps verify the MCP server works before configuring it in Cursor

echo "=================================="
echo "FastQC & MultiQC MCP Server Test"
echo "=================================="
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "Step 1: Checking Python virtual environment..."
if [ -d "$SCRIPT_DIR/venv" ]; then
    echo -e "${GREEN}✓${NC} Virtual environment found"
else
    echo -e "${RED}✗${NC} Virtual environment not found"
    echo "Please create one with: python3 -m venv venv"
    exit 1
fi

echo ""
echo "Step 2: Activating virtual environment..."
source "$SCRIPT_DIR/venv/bin/activate"
echo -e "${GREEN}✓${NC} Virtual environment activated"

echo ""
echo "Step 3: Checking Python version..."
PYTHON_VERSION=$(python3 --version)
echo -e "${GREEN}✓${NC} $PYTHON_VERSION"

echo ""
echo "Step 4: Checking required dependencies..."

# Check for required packages
REQUIRED_PACKAGES=("mcp" "pydantic" "matplotlib" "seaborn" "plotly" "pandas" "numpy")
MISSING_PACKAGES=()

for package in "${REQUIRED_PACKAGES[@]}"; do
    if python3 -c "import $package" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} $package installed"
    else
        echo -e "${RED}✗${NC} $package not found"
        MISSING_PACKAGES+=("$package")
    fi
done

if [ ${#MISSING_PACKAGES[@]} -ne 0 ]; then
    echo ""
    echo -e "${YELLOW}Warning:${NC} Missing packages detected"
    echo "Install them with: pip install -r requirements.txt"
    exit 1
fi

echo ""
echo "Step 5: Checking external tools..."

# Check for FastQC
if command -v fastqc &> /dev/null; then
    FASTQC_VERSION=$(fastqc --version 2>&1 | head -n 1)
    echo -e "${GREEN}✓${NC} FastQC found: $FASTQC_VERSION"
else
    echo -e "${YELLOW}⚠${NC} FastQC not found (install with: brew install fastqc)"
fi

# Check for MultiQC
if command -v multiqc &> /dev/null; then
    MULTIQC_VERSION=$(multiqc --version 2>&1)
    echo -e "${GREEN}✓${NC} MultiQC found: $MULTIQC_VERSION"
else
    echo -e "${YELLOW}⚠${NC} MultiQC not found (install with: pip install multiqc)"
fi

echo ""
echo "Step 6: Checking server script..."
if [ -f "$SCRIPT_DIR/src/server.py" ]; then
    echo -e "${GREEN}✓${NC} Server script found"
    
    # Check if script is executable
    if [ -x "$SCRIPT_DIR/src/server.py" ]; then
        echo -e "${GREEN}✓${NC} Server script is executable"
    else
        echo -e "${YELLOW}⚠${NC} Server script not executable, fixing..."
        chmod +x "$SCRIPT_DIR/src/server.py"
    fi
else
    echo -e "${RED}✗${NC} Server script not found at $SCRIPT_DIR/src/server.py"
    exit 1
fi

echo ""
echo "Step 7: Testing server syntax..."
if python3 -m py_compile "$SCRIPT_DIR/src/server.py" 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Server syntax is valid"
else
    echo -e "${RED}✗${NC} Server has syntax errors"
    python3 -m py_compile "$SCRIPT_DIR/src/server.py"
    exit 1
fi

echo ""
echo "=================================="
echo -e "${GREEN}All checks passed!${NC}"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Copy the configuration from cursor-mcp-config.json"
echo "2. Add it to Cursor's MCP configuration file"
echo "3. Restart Cursor"
echo "4. Test the MCP server in Cursor's AI chat"
echo ""
echo "Configuration file locations:"
echo "  - ~/Library/Application Support/Cursor/User/globalStorage/mcp.json"
echo "  - ~/Library/Application Support/Cursor/User/settings.json"
echo ""
echo "For detailed setup instructions, see CURSOR_SETUP.md"
echo ""
