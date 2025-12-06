#!/bin/bash

# Quick launcher for MCP Inspector
# Tests FastQC & MultiQC MCP Server

echo "🔍 Starting MCP Inspector for FastQC & MultiQC Server"
echo "======================================================"
echo ""

# Check if npx is available
if ! command -v npx &> /dev/null; then
    echo "❌ Error: npx not found"
    echo "Please install Node.js first:"
    echo "  brew install node"
    exit 1
fi

echo "📦 Launching MCP Inspector..."
echo ""
echo "Once the Inspector opens in your browser:"
echo ""
echo "1. Click 'Add Server' or configure manually"
echo "2. Enter these details:"
echo "   Server Name: fastqc-multiqc"
echo "   Command: $(pwd)/venv/bin/python3"
echo "   Arguments: $(pwd)/src/server.py"
echo ""
echo "3. Click 'Connect'"
echo "4. You should see 6 tools available"
echo ""
echo "Press Ctrl+C to stop the Inspector when done"
echo ""
echo "======================================================"
echo ""

# Launch inspector
npx @modelcontextprotocol/inspector
