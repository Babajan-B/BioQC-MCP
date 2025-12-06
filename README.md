# FastQC & MultiQC MCP Server

A professional Model Context Protocol (MCP) server for comprehensive bioinformatics quality control analysis. This server provides an integrated three-pronged approach to genomic data quality assessment: automated QC pipeline execution, interactive HTML report analysis, and dynamic data visualization.

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/MCP-1.0+-green.svg)](https://github.com/modelcontextprotocol)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## Overview

This MCP server combines three essential approaches to quality control analysis:

1. **Automated Quality Control Pipeline** - Execute FastQC and MultiQC analyses programmatically on sequencing data
2. **Intelligent HTML Report Analysis** - Read, parse, and interpret quality control reports directly within your workflow
3. **Dynamic Data Visualization** - Generate publication-quality charts and graphs from quality metrics

## Key Features

### Quality Control Pipeline
- Run FastQC analysis on individual or batch FASTQ files
- Generate MultiQC aggregate reports from multiple samples
- Auto-detect and validate FASTQ files in directories
- Parse and extract quality metrics from analysis results
- Support for all standard sequencing file formats (.fastq, .fq, .fastq.gz, .fq.gz)

### HTML Report Analysis
- Direct preview of FastQC and MultiQC HTML reports
- Extract structured information from quality control reports
- Analyze report structure, headings, tables, and data sections
- Interpret quality metrics without external browser dependencies
- Text-based content extraction and analysis

### Data Visualization
- Generate 20+ chart types for quality metrics visualization
- Automatic extraction and plotting of QC data from reports
- Publication-quality output with customizable styles and themes
- Support for multiple chart formats: line, bar, scatter, heatmap, violin, box, density, and more
- Interactive data visualization from parsed report data

## Prerequisites

**Required Software:**
- Python 3.8 or higher
- FastQC (bioinformatics quality control tool)
- MultiQC (aggregate reporting tool)

**Installation Commands:**
```bash
# Install FastQC (macOS)
brew install fastqc

# Install MultiQC
pip install multiqc
```

## Installation

### Step 1: Clone and Setup Environment

```bash
# Clone the repository
git clone <repository-url>
cd fastqc-multiqc-mcp-server

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Configure Claude Desktop

Add the server configuration to your Claude Desktop config file:

**Location:** `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS)

```json
{
  "mcpServers": {
    "fastqc-multiqc": {
      "command": "/path/to/venv/bin/python3",
      "args": ["/path/to/fastqc-multiqc-mcp-server/src/server.py"]
    }
  }
}
```

**Note:** Replace `/path/to/` with your actual installation path.

### Step 3: Test Before Deploying (Recommended)

Before integrating with Claude Desktop or Cursor, test your server:

```bash
# Run automated verification tests
./tests/test_mcp_server.sh

# Or launch MCP Inspector for interactive testing
./tests/launch_inspector.sh
```

See [docs/TESTING_WITH_INSPECTOR.md](docs/TESTING_WITH_INSPECTOR.md) for detailed testing instructions.

### Step 4: Restart Claude Desktop

Restart Claude Desktop to load the MCP server. The server will be automatically available for use.

## Testing in Other Clients

- **Cursor IDE**: See [QUICKSTART_CURSOR.md](QUICKSTART_CURSOR.md) for 3-step setup
- **Cursor (Detailed)**: See [CURSOR_SETUP.md](CURSOR_SETUP.md) for comprehensive troubleshooting
- **MCP Inspector**: See [docs/TESTING_WITH_INSPECTOR.md](docs/TESTING_WITH_INSPECTOR.md) for debugging
- **Example Config**: See [examples/cursor-mcp-config.json](examples/cursor-mcp-config.json) for Cursor configuration

## Usage

Interact with the server through natural language queries to Claude:

### Quality Control Analysis
```
"Run FastQC analysis on sample1.fastq and sample2.fastq"
"Check the quality of all FASTQ files in ~/sequencing_data/"
"Create a MultiQC report for all samples in the fastqc_output directory"
"What's the overall quality score of my sequencing data?"
```

### Report Analysis
```
"Read the FastQC HTML report at ~/results/sample_fastqc.html"
"What does the MultiQC report say about my samples?"
"Analyze the structure of the quality control report"
"Extract the key quality metrics from the FastQC report"
```

### Data Visualization
```
"Show me the per base quality scores as a line chart"
"Generate a heatmap of the quality metrics"
"Create a bar chart comparing GC content across samples"
"Visualize the adapter contamination data"
```

## Workflow Example

A typical quality control workflow using this server:

1. **Discovery:** Identify FASTQ files in your data directory
2. **Analysis:** Run FastQC on all samples
3. **Aggregation:** Generate MultiQC report for comparison
4. **Interpretation:** Read and analyze HTML reports
5. **Visualization:** Create custom charts for presentations
6. **Decision:** Make informed decisions based on comprehensive quality metrics

All steps can be performed through natural language interactions with Claude.

## Capabilities

### Supported Analysis Types
- Per base sequence quality assessment
- Per sequence quality score distribution
- GC content analysis
- Sequence length distribution
- Adapter contamination detection
- Duplicate sequence identification
- Overrepresented sequences
- Per base N content

### Available Visualization Types
- **Statistical Charts:** box plots, violin plots, histograms, density plots
- **Comparison Charts:** bar charts, scatter plots, line graphs
- **Distribution Charts:** heatmaps, area plots, KDE plots
- **Advanced Visualizations:** regression plots, joint plots, pair plots

### Report Processing
- Full HTML content extraction
- Structured data parsing
- Metadata extraction
- Summary statistics calculation
- Quality metric interpretation

## Architecture

The server implements a modular architecture with three core components:

1. **Pipeline Module:** Interfaces with FastQC/MultiQC command-line tools
2. **Parser Module:** Extracts and structures data from reports
3. **Visualization Module:** Generates charts using matplotlib, seaborn, and plotly

All components communicate through the Model Context Protocol, enabling seamless integration with Claude.

## Technical Specifications

**Programming Language:** Python 3.8+

**Core Dependencies:**
- mcp >= 1.0.0 (Model Context Protocol)
- pydantic >= 2.0.0 (data validation)
- matplotlib >= 3.8.0 (visualization)
- seaborn >= 0.13.0 (statistical graphics)
- plotly >= 5.18.0 (interactive charts)
- pandas >= 2.1.0 (data manipulation)
- numpy >= 1.24.0 (numerical computing)

**External Tools:**
- FastQC (quality control)
- MultiQC (report aggregation)

## Project Structure

```
fastqc-multiqc-mcp-server/
├── src/
│   ├── __init__.py
│   └── server.py              # Main MCP server implementation
├── docs/                       # Additional documentation
│   ├── TESTING_WITH_INSPECTOR.md
│   ├── TESTING_COMPLETE.md
│   ├── DEPLOYMENT_CHECKLIST.md
│   └── COMPARISON_BIOINFOMCP.md
├── examples/                   # Example configurations
│   └── cursor-mcp-config.json
├── tests/                      # Testing utilities
│   ├── test_mcp_server.sh
│   ├── test_server_manually.py
│   ├── test_real_fastqc.sh
│   └── launch_inspector.sh
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore rules
├── LICENSE                     # MIT License
├── README.md                   # Main documentation
├── QUICKSTART_CURSOR.md        # Cursor quick start
├── CURSOR_SETUP.md             # Cursor detailed setup
└── DEPLOYMENT_GUIDE.md         # Deployment instructions
```

## Project Status

**Current Version:** 2.0

**Status:** ✅ **Production Ready & Fully Tested**

**Testing Completed:** December 5, 2025
- ✅ MCP protocol compliance verified
- ✅ All 8 tools tested and functional
- ✅ Inspector integration successful
- ✅ Ready for Claude Desktop and Cursor IDE

**Recent Updates:**
- ✅ Integrated chart generation system with 20+ visualization types
- ✅ HTML report preview and analysis capabilities
- ✅ Automated quality control pipeline
- ✅ Multi-sample batch processing support
- ✅ Publication-quality visualization output
- ✅ Comprehensive testing suite and documentation

**See Testing Results:** [Testing Summary](.gemini/antigravity/brain/.../testing_summary.md)

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes with clear commit messages
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, reach out to: **bioinformatics.bb@gmail.com**

---

**Note:** This server is designed for local execution and does not require external API dependencies or network connectivity for core functionality.
