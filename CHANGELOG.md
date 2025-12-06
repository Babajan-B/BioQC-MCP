# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-12-06

### Added
- Comprehensive MCP server for FastQC and MultiQC quality control
- 8 specialized tools for bioinformatics QC workflows:
  - `run_fastqc` - Execute FastQC analysis
  - `run_multiqc` - Generate MultiQC aggregate reports
  - `list_fastq_files` - FASTQ file discovery
  - `parse_fastqc_summary` - Quality metrics extraction
  - `extract_fastqc_plots` - Plot data retrieval
  - `read_html_file` - HTML report reading
  - `analyze_html_content` - HTML structure analysis
  - `generate_chart` - Advanced visualization (20+ chart types)
- Support for all standard sequencing file formats (.fastq, .fq, .fastq.gz, .fq.gz)
- Advanced data visualization with 20+ chart types
- HTML report parsing and interpretation
- Automated testing suite
- MCP Inspector integration
- Comprehensive documentation:
  - README.md - Main documentation
  - QUICKSTART_CURSOR.md - Quick start for Cursor IDE
  - CURSOR_SETUP.md - Detailed Cursor troubleshooting
  - DEPLOYMENT_GUIDE.md - Distribution strategies
  - docs/TESTING_WITH_INSPECTOR.md - Inspector testing guide
  - docs/COMPARISON_BIOINFOMCP.md - Comparison with BioinfoMCP platform

### Tested
- ✅ MCP protocol compliance (2024-11-05)
- ✅ Real FASTQ file analysis (2.5GB test file)
- ✅ Claude Desktop integration
- ✅ MCP Inspector integration
- ✅ All 8 tools verified functional

### Documentation
- Complete setup guides for Claude Desktop and Cursor IDE
- Example configuration files
- Testing utilities and scripts
- Deployment strategies

## Project Status

**Version:** 2.0.0  
**Status:** Production Ready  
**Tested:** December 5-6, 2025  
**License:** MIT
