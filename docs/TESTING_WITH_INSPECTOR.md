# Testing with MCP Inspector

The MCP Inspector is the **recommended first step** for testing your MCP server before integrating with Cursor.

## Why Test with Inspector First?

✅ **Isolated environment** - Test server independently  
✅ **Visual debugging** - See all tools and their schemas  
✅ **Interactive testing** - Execute tools and view responses  
✅ **Fast iteration** - No need to restart Cursor  
✅ **Official tool** - Built by MCP team for server development  

## Installation

### Option 1: NPX (Recommended - No Install)
```bash
npx @modelcontextprotocol/inspector
```

### Option 2: Global Install
```bash
npm install -g @modelcontextprotocol/inspector
mcp-inspector
```

## Testing Your FastQC/MultiQC Server

### Step 1: Start the Inspector

```bash
cd /Users/jaan/Desktop/Ai-text/fastqc-multiqc-mcp-server
npx @modelcontextprotocol/inspector
```

This will:
- Start a local web server (usually http://localhost:5173)
- Open your browser automatically
- Show the Inspector interface

### Step 2: Configure Your Server in Inspector

In the Inspector web interface:

1. **Add New Server** button
2. Enter server details:
   ```
   Server Name: fastqc-multiqc
   Command: /Users/jaan/Desktop/Ai-text/fastqc-multiqc-mcp-server/venv/bin/python3
   Arguments: /Users/jaan/Desktop/Ai-text/fastqc-multiqc-mcp-server/src/server.py
   ```

### Step 3: Connect and Explore

Once connected, you should see:

**Tools Available (6 total):**
- ✅ `run_fastqc` - Run FastQC analysis
- ✅ `run_multiqc` - Generate MultiQC reports
- ✅ `parse_fastqc_summary` - Parse quality metrics
- ✅ `read_html_file` - Read HTML reports
- ✅ `generate_chart` - Create visualizations
- ✅ `extract_and_visualize_qc_data` - Auto-visualization

### Step 4: Test Individual Tools

#### Test 1: Read HTML File (Simple Test)
```json
{
  "file_path": "/path/to/sample_fastqc.html"
}
```

#### Test 2: Generate Chart (Visualization Test)
```json
{
  "chart_type": "line",
  "data": {
    "x": [1, 2, 3, 4, 5],
    "y": [20, 25, 30, 28, 35]
  },
  "title": "Test Quality Scores",
  "x_label": "Position",
  "y_label": "Quality"
}
```

## What to Check

### ✅ Server Starts Successfully
- No errors in console
- Tools list appears

### ✅ Tool Schemas Are Correct
- All 6 tools listed
- Parameters match expected inputs
- Descriptions are clear

### ✅ Tools Execute Properly
- Test each tool with sample data
- Check responses are formatted correctly
- Verify error handling

### ✅ Environment Configuration
- FastQC/MultiQC accessible
- Python dependencies loaded
- File paths resolve correctly

## Common Issues & Solutions

### Issue: Server Won't Start
**Solution:**
```bash
# Verify server runs standalone
source venv/bin/activate
python3 src/server.py
# Should show MCP protocol output
```

### Issue: Python Not Found
**Solution:**
```bash
# Verify path
ls -la /Users/jaan/Desktop/Ai-text/fastqc-multiqc-mcp-server/venv/bin/python3

# Use absolute path in Inspector config
which python3  # After activating venv
```

### Issue: Missing Dependencies
**Solution:**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: FastQC/MultiQC Not Found
**Solution:**
Add environment variable in Inspector:
```
Key: PATH
Value: /usr/local/bin:/opt/homebrew/bin:{existing PATH}
```

## Recommended Testing Workflow

```
1. Test with Inspector ← START HERE
   ↓
2. Fix any issues found
   ↓
3. Re-test in Inspector
   ↓
4. Once working perfectly → Test in Cursor
   ↓
5. Final validation in production
```

## Benefits Over Direct Cursor Testing

| Aspect | MCP Inspector | Direct Cursor |
|--------|---------------|---------------|
| Setup Speed | Instant | Requires restart |
| Debugging | Visual, detailed | Console logs only |
| Iteration | Fast (refresh browser) | Slow (restart app) |
| Isolation | Server only | Full app stack |
| Learning | See MCP protocol | Hidden complexity |

## Sample Test Session

### Test Sequence:

1. **Connection Test**
   - Start Inspector
   - Connect to server
   - Verify 6 tools appear

2. **Simple Tool Test**
   - Call `read_html_file` with a sample HTML
   - Verify HTML content returned

3. **Complex Tool Test**
   - Call `generate_chart` with sample data
   - Verify image generated and returned

4. **Pipeline Test**
   - Call `run_fastqc` on sample FASTQ
   - Verify analysis runs
   - Check output paths

5. **Error Handling Test**
   - Call tool with invalid input
   - Verify proper error messages

## Next Steps After Inspector Testing

Once your server works perfectly in Inspector:

✅ **Copy exact configuration** to Cursor  
✅ **Document any environment variables** needed  
✅ **Note any path requirements**  
✅ **Validate same behavior in Cursor**  

## Pro Tips

💡 **Keep Inspector running** - Use it for quick testing during development  
💡 **Test edge cases** - Try invalid inputs to verify error handling  
💡 **Check performance** - Time tool execution for large files  
💡 **Verify all tools** - Don't assume if one works, all work  
💡 **Document findings** - Note any quirks for Cursor setup  

## Resources

- **MCP Inspector Docs**: https://modelcontextprotocol.io/docs/tools/inspector
- **MCP Protocol Spec**: https://spec.modelcontextprotocol.io/
- **MCP GitHub**: https://github.com/modelcontextprotocol

---

**TL;DR**: Yes, absolutely use MCP Inspector first! It's faster, easier to debug, and the recommended way to test MCP servers before production use.
