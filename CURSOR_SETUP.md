# Testing FastQC & MultiQC MCP Server in Cursor

This guide explains how to configure and test your MCP server in Cursor IDE.

## Prerequisites

- Cursor IDE installed
- Python 3.8+ with virtual environment set up
- FastQC and MultiQC installed (as per main README.md)
- MCP server dependencies installed via `requirements.txt`

## Configuration Steps

### Step 1: Locate Cursor's MCP Configuration File

Cursor uses a similar configuration approach to Claude Desktop. The configuration file location depends on your OS:

**macOS:**
```bash
~/Library/Application Support/Cursor/User/globalStorage/mcp.json
```

**Alternative macOS location (if using settings.json):**
```bash
~/Library/Application Support/Cursor/User/settings.json
```

### Step 2: Create/Edit MCP Configuration

You have two options for configuring the MCP server in Cursor:

#### Option A: Using mcp.json (Recommended)

Create or edit `~/Library/Application Support/Cursor/User/globalStorage/mcp.json`:

```json
{
  "mcpServers": {
    "fastqc-multiqc": {
      "command": "/Users/jaan/Desktop/Ai-text/fastqc-multiqc-mcp-server/venv/bin/python3",
      "args": [
        "/Users/jaan/Desktop/Ai-text/fastqc-multiqc-mcp-server/src/server.py"
      ],
      "env": {}
    }
  }
}
```

#### Option B: Using settings.json

Add to `~/Library/Application Support/Cursor/User/settings.json`:

```json
{
  "mcp.servers": {
    "fastqc-multiqc": {
      "command": "/Users/jaan/Desktop/Ai-text/fastqc-multiqc-mcp-server/venv/bin/python3",
      "args": [
        "/Users/jaan/Desktop/Ai-text/fastqc-multiqc-mcp-server/src/server.py"
      ]
    }
  }
}
```

### Step 3: Verify Python Path

Make sure your virtual environment is activated and working:

```bash
cd /Users/jaan/Desktop/Ai-text/fastqc-multiqc-mcp-server
source venv/bin/activate
which python3
# Should output: /Users/jaan/Desktop/Ai-text/fastqc-multiqc-mcp-server/venv/bin/python3
```

### Step 4: Test Server Standalone

Before configuring Cursor, test the server works independently:

```bash
cd /Users/jaan/Desktop/Ai-text/fastqc-multiqc-mcp-server
source venv/bin/activate
python3 src/server.py
```

The server should start without errors. Press `Ctrl+C` to stop.

### Step 5: Restart Cursor

After editing the configuration:

1. Save the configuration file
2. Completely quit Cursor (Cmd+Q)
3. Reopen Cursor

### Step 6: Verify MCP Server in Cursor

1. Open Cursor
2. Open the AI chat panel (Cmd+L or Cmd+K)
3. Look for MCP server indicators (may show as tools or capabilities)
4. Try a simple command like: "List the available MCP tools"

## Testing the MCP Server

Once configured, you can test the server with these commands in Cursor's AI chat:

### Basic Connection Test
```
Can you see the FastQC and MultiQC tools available?
```

### Tool Listing Test
```
What MCP tools are available for quality control analysis?
```

### Simple Functionality Test
```
Read the HTML file at [path to a sample HTML report if you have one]
```

## Troubleshooting

### MCP Server Not Showing Up

1. **Check Configuration File Syntax:**
   - Ensure JSON is valid (no trailing commas, proper quotes)
   - Use a JSON validator

2. **Verify Python Path:**
   ```bash
   ls -la /Users/jaan/Desktop/Ai-text/fastqc-multiqc-mcp-server/venv/bin/python3
   ```

3. **Check Server Script:**
   ```bash
   ls -la /Users/jaan/Desktop/Ai-text/fastqc-multiqc-mcp-server/src/server.py
   ```

4. **View Cursor Logs:**
   - Open Cursor Developer Tools: `View > Developer > Toggle Developer Tools`
   - Check Console for MCP-related errors

### Dependencies Issues

If the server fails to start due to missing dependencies:

```bash
cd /Users/jaan/Desktop/Ai-text/fastqc-multiqc-mcp-server
source venv/bin/activate
pip install -r requirements.txt
```

### Permission Issues

Ensure the server script is executable:

```bash
chmod +x /Users/jaan/Desktop/Ai-text/fastqc-multiqc-mcp-server/src/server.py
```

### Environment Variables

If FastQC/MultiQC are not in your PATH, add them to the MCP configuration:

```json
{
  "mcpServers": {
    "fastqc-multiqc": {
      "command": "/Users/jaan/Desktop/Ai-text/fastqc-multiqc-mcp-server/venv/bin/python3",
      "args": [
        "/Users/jaan/Desktop/Ai-text/fastqc-multiqc-mcp-server/src/server.py"
      ],
      "env": {
        "PATH": "/usr/local/bin:/opt/homebrew/bin:${PATH}"
      }
    }
  }
}
```

## Differences Between Claude Desktop and Cursor

| Feature | Claude Desktop | Cursor |
|---------|---------------|--------|
| Config Location | `~/Library/Application Support/Claude/` | `~/Library/Application Support/Cursor/User/` |
| Config File | `claude_desktop_config.json` | `mcp.json` or `settings.json` |
| Auto-discovery | Yes | Depends on version |
| Tool Visibility | Clear in UI | May vary by version |

## Next Steps

Once the server is working in Cursor:

1. **Test All Tools:**
   - `run_fastqc` - Run quality control on FASTQ files
   - `run_multiqc` - Aggregate multiple reports
   - `parse_fastqc_summary` - Extract metrics
   - `read_html_file` - Preview reports
   - `generate_chart` - Create visualizations
   - `extract_and_visualize_qc_data` - Auto-visualization

2. **Create Test Data:**
   - Use sample FASTQ files for testing
   - Generate FastQC reports
   - Test report parsing and visualization

3. **Validate Workflow:**
   - Complete end-to-end QC analysis
   - Generate and analyze reports
   - Create custom visualizations

## Support

If you encounter issues specific to Cursor integration:

1. Check Cursor's MCP documentation (may be updated)
2. Verify MCP protocol version compatibility
3. Test with a simpler MCP server first to isolate configuration issues
4. Check Cursor's GitHub issues for MCP-related problems

## References

- [Model Context Protocol Specification](https://github.com/modelcontextprotocol)
- [Cursor Documentation](https://cursor.sh/docs)
- Main README.md for server capabilities
