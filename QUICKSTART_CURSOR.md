# Quick Start: Testing MCP Server in Cursor

## ✅ Pre-flight Check Complete
Run the test script to verify setup:
```bash
./test_mcp_server.sh
```

## 🚀 3-Step Setup for Cursor

### Step 1: Copy Configuration
The configuration is ready in `cursor-mcp-config.json`:

```json
{
  "mcpServers": {
    "fastqc-multiqc": {
      "command": "/Users/jaan/Desktop/Ai-text/fastqc-multiqc-mcp-server/venv/bin/python3",
      "args": [
        "/Users/jaan/Desktop/Ai-text/fastqc-multiqc-mcp-server/src/server.py"
      ],
      "env": {
        "PATH": "/usr/local/bin:/opt/homebrew/bin:${PATH}",
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

### Step 2: Add to Cursor Configuration

**Option A - Create/Edit MCP config file (Recommended):**
```bash
# Create the directory if it doesn't exist
mkdir -p ~/Library/Application\ Support/Cursor/User/globalStorage

# Copy the config
cp cursor-mcp-config.json ~/Library/Application\ Support/Cursor/User/globalStorage/mcp.json
```

**Option B - Manual edit:**
1. Open: `~/Library/Application Support/Cursor/User/globalStorage/mcp.json`
2. Paste the configuration from `cursor-mcp-config.json`
3. Save the file

### Step 3: Restart Cursor
1. Quit Cursor completely (⌘Q)
2. Reopen Cursor
3. The MCP server should now be available

## 🧪 Test in Cursor

Once Cursor restarts, open the AI chat and try:

### Connection Test
```
What MCP tools are available?
```

### Expected Response
Cursor should show these tools:
- `run_fastqc` - Run quality control analysis
- `run_multiqc` - Aggregate multiple reports
- `parse_fastqc_summary` - Extract metrics
- `read_html_file` - Preview HTML reports
- `generate_chart` - Create visualizations
- `extract_and_visualize_qc_data` - Auto-visualization

### Functionality Test
```
Can you list FastQC and MultiQC capabilities?
```

## 🔧 Troubleshooting

### Server Not Showing?
1. Check Cursor logs: `View > Developer > Toggle Developer Tools`
2. Look for MCP-related errors in Console
3. Verify paths in configuration match your system

### Quick Fixes
```bash
# Re-run the test script
./test_mcp_server.sh

# Verify Python environment
source venv/bin/activate
python3 src/server.py
# Should start without errors (Ctrl+C to stop)

# Check configuration syntax
cat cursor-mcp-config.json | python3 -m json.tool
```

## 📚 Full Documentation
- See `CURSOR_SETUP.md` for detailed setup instructions
- See `README.md` for MCP server capabilities and usage examples

## 🎯 Quick Reference

| File | Purpose |
|------|---------|
| `CURSOR_SETUP.md` | Complete Cursor setup guide |
| `cursor-mcp-config.json` | Ready-to-use Cursor configuration |
| `test_mcp_server.sh` | Pre-flight verification script |
| `README.md` | Main documentation with features |

## ✨ Next Steps
Once working in Cursor, you can:
1. Run quality control on FASTQ files
2. Generate and analyze HTML reports
3. Create custom visualizations
4. Parse quality metrics
5. Aggregate multiple sample analyses

**Happy testing! 🚀**
