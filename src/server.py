#!/usr/bin/env python3
"""
FastQC & MultiQC MCP Server
Provides quality control analysis tools for sequencing data
"""

import asyncio
import base64
import json
import logging
import os
import re
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import Any, Sequence
from html.parser import HTMLParser
import io

# Chart generation libraries
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP server
app = Server("fastqc-multiqc-server")

# Tool definitions
TOOLS: list[Tool] = [
    Tool(
        name="run_fastqc",
        description="Run FastQC quality control analysis on FASTQ files. Returns summary of quality metrics and path to HTML report.",
        inputSchema={
            "type": "object",
            "properties": {
                "input_files": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of FASTQ file paths to analyze"
                },
                "output_dir": {
                    "type": "string",
                    "description": "Output directory for FastQC reports (default: fastqc_output)"
                },
                "threads": {
                    "type": "integer",
                    "description": "Number of threads to use (default: 2)",
                    "default": 2
                }
            },
            "required": ["input_files"]
        }
    ),
    Tool(
        name="run_multiqc",
        description="Aggregate multiple FastQC reports into a single MultiQC report. Useful for comparing multiple samples.",
        inputSchema={
            "type": "object",
            "properties": {
                "input_dir": {
                    "type": "string",
                    "description": "Directory containing FastQC reports to aggregate"
                },
                "output_dir": {
                    "type": "string",
                    "description": "Output directory for MultiQC report (default: multiqc_output)"
                }
            },
            "required": ["input_dir"]
        }
    ),
    Tool(
        name="list_fastq_files",
        description="Find all FASTQ files in a directory. Supports .fastq, .fq, .fastq.gz, .fq.gz extensions.",
        inputSchema={
            "type": "object",
            "properties": {
                "directory": {
                    "type": "string",
                    "description": "Directory to search for FASTQ files"
                },
                "recursive": {
                    "type": "boolean",
                    "description": "Search recursively in subdirectories (default: false)",
                    "default": False
                }
            },
            "required": ["directory"]
        }
    ),
    Tool(
        name="parse_fastqc_summary",
        description="Parse FastQC summary data from fastqc_data.txt file. Returns key quality metrics in structured format.",
        inputSchema={
            "type": "object",
            "properties": {
                "fastqc_dir": {
                    "type": "string",
                    "description": "Path to FastQC output directory containing fastqc_data.txt"
                }
            },
            "required": ["fastqc_dir"]
        }
    ),
    Tool(
        name="extract_fastqc_plots",
        description="Extract key quality plots from FastQC reports. Returns images of per base quality, sequence quality, GC content, and adapter content plots.",
        inputSchema={
            "type": "object",
            "properties": {
                "fastqc_dir": {
                    "type": "string",
                    "description": "Path to FastQC output directory"
                },
                "plots": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["per_base_quality", "per_sequence_quality", "gc_content", "adapter_content", "all"]
                    },
                    "description": "Which plots to extract (default: all key plots)",
                    "default": ["all"]
                }
            },
            "required": ["fastqc_dir"]
        }
    ),
    Tool(
        name="read_html_file",
        description="Read and preview HTML files (FastQC/MultiQC reports). Returns the full HTML content that Claude can analyze and interpret.",
        inputSchema={
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the HTML file to read"
                },
                "extract_text": {
                    "type": "boolean",
                    "description": "Extract and return text content only (default: false)",
                    "default": False
                }
            },
            "required": ["file_path"]
        }
    ),
    Tool(
        name="analyze_html_content",
        description="Analyze HTML file structure and extract key information like headings, tables, and data sections. Useful for understanding report structure.",
        inputSchema={
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the HTML file to analyze"
                }
            },
            "required": ["file_path"]
        }
    ),
    Tool(
        name="generate_chart",
        description="Generate charts from data extracted from FastQC/MultiQC reports or custom data. Supports 20+ chart types including line, bar, scatter, heatmap, box plot, and more.",
        inputSchema={
            "type": "object",
            "properties": {
                "chart_type": {
                    "type": "string",
                    "enum": [
                        "line", "bar", "scatter", "histogram", "box", "violin",
                        "heatmap", "pie", "area", "density", "strip", "swarm",
                        "count", "point", "regression", "residual", "distribution",
                        "joint", "pair", "kde"
                    ],
                    "description": "Type of chart to generate"
                },
                "data": {
                    "type": "object",
                    "description": "Chart data in JSON format. Can be array of objects or nested structure.",
                    "additionalProperties": True
                },
                "title": {
                    "type": "string",
                    "description": "Chart title (optional)"
                },
                "x_label": {
                    "type": "string",
                    "description": "X-axis label (optional)"
                },
                "y_label": {
                    "type": "string",
                    "description": "Y-axis label (optional)"
                },
                "style": {
                    "type": "string",
                    "enum": ["default", "seaborn", "ggplot", "dark", "minimal"],
                    "description": "Chart style theme (default: seaborn)",
                    "default": "seaborn"
                },
                "width": {
                    "type": "integer",
                    "description": "Chart width in pixels (default: 800)",
                    "default": 800
                },
                "height": {
                    "type": "integer",
                    "description": "Chart height in pixels (default: 600)",
                    "default": 600
                }
            },
            "required": ["chart_type", "data"]
        }
    ),
    Tool(
        name="extract_and_visualize_qc_data",
        description="Extract quality control data from FastQC reports and automatically generate appropriate visualizations. Perfect for QC analysis.",
        inputSchema={
            "type": "object",
            "properties": {
                "fastqc_dir": {
                    "type": "string",
                    "description": "Path to FastQC output directory"
                },
                "metrics": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["quality_scores", "gc_content", "sequence_length", "duplication", "adapter", "all"]
                    },
                    "description": "Which metrics to visualize (default: all)",
                    "default": ["all"]
                }
            },
            "required": ["fastqc_dir"]
        }
    )
]


class HTMLAnalyzer(HTMLParser):
    """Custom HTML parser to extract structure and content"""

    def __init__(self):
        super().__init__()
        self.headings = []
        self.paragraphs = []
        self.links = []
        self.images = []
        self.tables = []
        self.current_tag = None
        self.current_data = []

    def handle_starttag(self, tag, attrs):
        self.current_tag = tag

        if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            self.current_data = []
        elif tag == 'p':
            self.current_data = []
        elif tag == 'a':
            href = dict(attrs).get('href', '')
            self.links.append(href)
        elif tag == 'img':
            src = dict(attrs).get('src', '')
            alt = dict(attrs).get('alt', '')
            self.images.append({'src': src, 'alt': alt})
        elif tag == 'table':
            self.tables.append('table_found')

    def handle_data(self, data):
        if self.current_tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p']:
            self.current_data.append(data.strip())

    def handle_endtag(self, tag):
        if tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            text = ' '.join(self.current_data)
            if text:
                self.headings.append({'level': tag, 'text': text})
        elif tag == 'p':
            text = ' '.join(self.current_data)
            if text:
                self.paragraphs.append(text)

        if tag == self.current_tag:
            self.current_tag = None
            self.current_data = []


def read_html_file(file_path: str, extract_text: bool = False) -> dict[str, Any]:
    """Read HTML file and optionally extract text content"""
    html_path = Path(file_path).expanduser()

    if not html_path.exists():
        return {"success": False, "error": f"File not found: {file_path}"}

    if not html_path.suffix.lower() in ['.html', '.htm']:
        return {"success": False, "error": f"Not an HTML file: {file_path}"}

    try:
        with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
            html_content = f.read()

        result = {
            "success": True,
            "file_path": str(html_path),
            "file_size_kb": round(html_path.stat().st_size / 1024, 2)
        }

        if extract_text:
            # Remove HTML tags and extract text
            text_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL)
            text_content = re.sub(r'<style[^>]*>.*?</style>', '', text_content, flags=re.DOTALL)
            text_content = re.sub(r'<[^>]+>', '', text_content)
            text_content = re.sub(r'\s+', ' ', text_content).strip()
            result["text_content"] = text_content
        else:
            result["html_content"] = html_content

        return result

    except Exception as e:
        return {"success": False, "error": f"Error reading file: {str(e)}"}


def analyze_html_structure(file_path: str) -> dict[str, Any]:
    """Analyze HTML file structure and extract key elements"""
    html_path = Path(file_path).expanduser()

    if not html_path.exists():
        return {"success": False, "error": f"File not found: {file_path}"}

    if not html_path.suffix.lower() in ['.html', '.htm']:
        return {"success": False, "error": f"Not an HTML file: {file_path}"}

    try:
        with open(html_path, 'r', encoding='utf-8', errors='ignore') as f:
            html_content = f.read()

        # Parse HTML
        parser = HTMLAnalyzer()
        parser.feed(html_content)

        # Extract title
        title_match = re.search(r'<title[^>]*>(.*?)</title>', html_content, re.IGNORECASE)
        title = title_match.group(1) if title_match else "No title"

        result = {
            "success": True,
            "file_path": str(html_path),
            "title": title,
            "structure": {
                "headings": parser.headings[:20],  # Limit to first 20
                "num_paragraphs": len(parser.paragraphs),
                "num_links": len(parser.links),
                "num_images": len(parser.images),
                "num_tables": len(parser.tables),
                "sample_paragraphs": parser.paragraphs[:5]  # First 5 paragraphs
            }
        }

        return result

    except Exception as e:
        return {"success": False, "error": f"Error analyzing file: {str(e)}"}


def generate_chart_from_data(
    chart_type: str,
    data: dict,
    title: str = "",
    x_label: str = "",
    y_label: str = "",
    style: str = "seaborn",
    width: int = 800,
    height: int = 600
) -> dict[str, Any]:
    """Generate chart from provided data"""

    try:
        # Set style
        style_map = {
            "seaborn": "seaborn-v0_8",
            "ggplot": "ggplot",
            "dark": "dark_background",
            "minimal": "bmh",
            "default": "default"
        }
        plt.style.use(style_map.get(style, "seaborn-v0_8"))

        # Convert data to DataFrame if it's a list of dicts
        if isinstance(data, list):
            df = pd.DataFrame(data)
        elif isinstance(data, dict):
            # Check if it's a dict of lists (column-oriented)
            if all(isinstance(v, list) for v in data.values()):
                df = pd.DataFrame(data)
            else:
                # Assume it's a single record
                df = pd.DataFrame([data])
        else:
            return {"success": False, "error": "Data must be a list or dict"}

        # Create figure
        fig, ax = plt.subplots(figsize=(width/100, height/100), dpi=100)

        # Generate chart based on type
        if chart_type == "line":
            if len(df.columns) >= 2:
                ax.plot(df.iloc[:, 0], df.iloc[:, 1], marker='o', linewidth=2)
            else:
                ax.plot(df.iloc[:, 0], marker='o', linewidth=2)

        elif chart_type == "bar":
            if len(df.columns) >= 2:
                ax.bar(df.iloc[:, 0], df.iloc[:, 1])
            else:
                ax.bar(range(len(df)), df.iloc[:, 0])

        elif chart_type == "scatter":
            if len(df.columns) >= 2:
                ax.scatter(df.iloc[:, 0], df.iloc[:, 1], s=100, alpha=0.6)

        elif chart_type == "histogram":
            ax.hist(df.iloc[:, 0], bins=30, edgecolor='black', alpha=0.7)

        elif chart_type == "box":
            ax.boxplot([df[col].dropna() for col in df.columns])
            ax.set_xticklabels(df.columns)

        elif chart_type == "violin":
            sns.violinplot(data=df, ax=ax)

        elif chart_type == "heatmap":
            sns.heatmap(df, annot=True, fmt='.2f', cmap='coolwarm', ax=ax)

        elif chart_type == "pie":
            if len(df.columns) >= 2:
                ax.pie(df.iloc[:, 1], labels=df.iloc[:, 0], autopct='%1.1f%%')
            else:
                ax.pie(df.iloc[:, 0], autopct='%1.1f%%')

        elif chart_type == "area":
            if len(df.columns) >= 2:
                ax.fill_between(range(len(df)), df.iloc[:, 1], alpha=0.6)
                ax.plot(df.iloc[:, 1], linewidth=2)

        elif chart_type in ["density", "kde"]:
            for col in df.select_dtypes(include=[np.number]).columns:
                df[col].plot(kind='density', ax=ax)

        elif chart_type in ["strip", "swarm"]:
            sns.stripplot(data=df, ax=ax) if chart_type == "strip" else sns.swarmplot(data=df, ax=ax)

        else:
            # Default to line chart for unknown types
            ax.plot(df.iloc[:, 0] if len(df.columns) == 1 else df.iloc[:, 1], marker='o')

        # Set labels and title
        if title:
            ax.set_title(title, fontsize=14, fontweight='bold')
        if x_label:
            ax.set_xlabel(x_label, fontsize=11)
        if y_label:
            ax.set_ylabel(y_label, fontsize=11)

        plt.tight_layout()

        # Save to bytes
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()

        return {
            "success": True,
            "chart_type": chart_type,
            "image_data": img_base64,
            "mime_type": "image/png",
            "width": width,
            "height": height
        }

    except Exception as e:
        plt.close('all')  # Clean up any open figures
        logger.error(f"Error generating chart: {e}")
        return {"success": False, "error": f"Error generating chart: {str(e)}"}


def extract_and_visualize_qc(fastqc_dir: str, metrics: list[str] = ["all"]) -> dict[str, Any]:
    """Extract QC data and generate visualizations"""
    fastqc_path = Path(fastqc_dir).expanduser()

    if not fastqc_path.exists():
        return {"success": False, "error": f"Directory not found: {fastqc_dir}"}

    data_file = fastqc_path / "fastqc_data.txt"
    if not data_file.exists():
        return {"success": False, "error": f"fastqc_data.txt not found in {fastqc_dir}"}

    try:
        with open(data_file, 'r') as f:
            content = f.read()

        charts = {}

        # Extract per base quality scores
        if "all" in metrics or "quality_scores" in metrics:
            if ">>Per base sequence quality" in content:
                section = content.split(">>Per base sequence quality")[1].split(">>END_MODULE")[0]
                lines = [l.strip() for l in section.split('\n') if l.strip() and not l.startswith('#')]

                if len(lines) > 0:
                    data = []
                    for line in lines[1:]:  # Skip header
                        parts = line.split('\t')
                        if len(parts) >= 2:
                            try:
                                data.append({"position": parts[0], "quality": float(parts[1])})
                            except ValueError:
                                continue

                    if data:
                        chart_result = generate_chart_from_data(
                            "line",
                            data,
                            title="Per Base Sequence Quality",
                            x_label="Position",
                            y_label="Quality Score"
                        )
                        if chart_result["success"]:
                            charts["quality_scores"] = chart_result["image_data"]

        # Extract GC content
        if "all" in metrics or "gc_content" in metrics:
            if ">>Per sequence GC content" in content:
                section = content.split(">>Per sequence GC content")[1].split(">>END_MODULE")[0]
                lines = [l.strip() for l in section.split('\n') if l.strip() and not l.startswith('#')]

                if len(lines) > 0:
                    data = []
                    for line in lines[1:]:
                        parts = line.split('\t')
                        if len(parts) >= 2:
                            try:
                                data.append({"gc_content": float(parts[0]), "count": float(parts[1])})
                            except ValueError:
                                continue

                    if data:
                        chart_result = generate_chart_from_data(
                            "line",
                            data,
                            title="GC Content Distribution",
                            x_label="GC Content (%)",
                            y_label="Count"
                        )
                        if chart_result["success"]:
                            charts["gc_content"] = chart_result["image_data"]

        return {
            "success": True,
            "num_charts": len(charts),
            "charts": charts,
            "fastqc_dir": str(fastqc_path)
        }

    except Exception as e:
        logger.error(f"Error extracting and visualizing QC data: {e}")
        return {"success": False, "error": str(e)}


def find_fastq_files(directory: str, recursive: bool = False) -> list[dict[str, Any]]:
    """Find FASTQ files in a directory"""
    fastq_extensions = [".fastq", ".fq", ".fastq.gz", ".fq.gz"]
    fastq_files = []

    dir_path = Path(directory).expanduser()
    if not dir_path.exists():
        raise FileNotFoundError(f"Directory not found: {directory}")

    pattern = "**/*" if recursive else "*"

    for ext in fastq_extensions:
        for file_path in dir_path.glob(f"{pattern}{ext}"):
            if file_path.is_file():
                file_info = {
                    "path": str(file_path),
                    "name": file_path.name,
                    "size_mb": round(file_path.stat().st_size / (1024 * 1024), 2)
                }
                fastq_files.append(file_info)

    return sorted(fastq_files, key=lambda x: x["name"])


def run_fastqc_analysis(input_files: list[str], output_dir: str = "fastqc_output", threads: int = 2) -> dict[str, Any]:
    """Run FastQC on input files"""
    output_path = Path(output_dir).expanduser()
    output_path.mkdir(parents=True, exist_ok=True)

    # Expand paths
    expanded_files = [str(Path(f).expanduser()) for f in input_files]

    # Build FastQC command
    cmd = ["fastqc", "-o", str(output_path), "-t", str(threads)] + expanded_files

    logger.info(f"Running FastQC: {' '.join(cmd)}")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout
        )

        if result.returncode != 0:
            return {
                "success": False,
                "error": result.stderr,
                "command": " ".join(cmd)
            }

        # Find generated reports
        reports = list(output_path.glob("*.html"))

        return {
            "success": True,
            "output_dir": str(output_path),
            "num_files_analyzed": len(input_files),
            "reports": [str(r) for r in reports],
            "message": f"FastQC analysis complete. Analyzed {len(input_files)} file(s). Reports saved to {output_path}"
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "FastQC analysis timed out (>10 minutes)"
        }
    except FileNotFoundError:
        return {
            "success": False,
            "error": "FastQC not found. Please ensure it is installed and in PATH."
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def run_multiqc_analysis(input_dir: str, output_dir: str = "multiqc_output") -> dict[str, Any]:
    """Run MultiQC to aggregate FastQC reports"""
    input_path = Path(input_dir).expanduser()
    output_path = Path(output_dir).expanduser()

    if not input_path.exists():
        return {
            "success": False,
            "error": f"Input directory not found: {input_dir}"
        }

    output_path.mkdir(parents=True, exist_ok=True)

    cmd = ["multiqc", str(input_path), "-o", str(output_path), "--force"]

    logger.info(f"Running MultiQC: {' '.join(cmd)}")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )

        if result.returncode != 0:
            return {
                "success": False,
                "error": result.stderr,
                "command": " ".join(cmd)
            }

        report_path = output_path / "multiqc_report.html"

        return {
            "success": True,
            "output_dir": str(output_path),
            "report": str(report_path) if report_path.exists() else None,
            "message": f"MultiQC analysis complete. Report saved to {report_path}"
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "MultiQC analysis timed out (>5 minutes)"
        }
    except FileNotFoundError:
        return {
            "success": False,
            "error": "MultiQC not found. Please ensure it is installed (pip install multiqc)."
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def parse_fastqc_data(fastqc_dir: str) -> dict[str, Any]:
    """Parse FastQC summary data"""
    fastqc_path = Path(fastqc_dir).expanduser()

    # Look for fastqc_data.txt
    data_file = fastqc_path / "fastqc_data.txt"
    summary_file = fastqc_path / "summary.txt"

    if not fastqc_path.exists():
        return {"success": False, "error": f"Directory not found: {fastqc_dir}"}

    result = {"success": True, "metrics": {}, "summary": {}}

    # Parse summary.txt (pass/warn/fail status)
    if summary_file.exists():
        with open(summary_file, 'r') as f:
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) >= 2:
                    status, module = parts[0], parts[1]
                    result["summary"][module] = status

    # Parse fastqc_data.txt (detailed metrics)
    if data_file.exists():
        with open(data_file, 'r') as f:
            content = f.read()

            # Extract basic statistics
            if ">>Basic Statistics" in content:
                stats_section = content.split(">>Basic Statistics")[1].split(">>END_MODULE")[0]
                for line in stats_section.strip().split('\n'):
                    if '\t' in line and not line.startswith('#'):
                        parts = line.split('\t')
                        if len(parts) >= 2:
                            key, value = parts[0], parts[1]
                            result["metrics"][key] = value

    return result


def extract_plots_from_fastqc(fastqc_dir: str, plot_types: list[str] = ["all"]) -> dict[str, Any]:
    """Extract image plots from FastQC output directory"""
    fastqc_path = Path(fastqc_dir).expanduser()

    if not fastqc_path.exists():
        return {"success": False, "error": f"Directory not found: {fastqc_dir}"}

    # Map of plot types to their filenames in FastQC output
    plot_mapping = {
        "per_base_quality": "per_base_quality.png",
        "per_sequence_quality": "per_sequence_quality_scores.png",
        "gc_content": "per_sequence_gc_content.png",
        "adapter_content": "adapter_content.png",
        "sequence_length": "sequence_length_distribution.png",
        "duplication": "duplication_levels.png",
        "per_base_n_content": "per_base_n_content.png",
        "per_base_sequence_content": "per_base_sequence_content.png"
    }

    # If "all" is specified, extract all available plots
    if "all" in plot_types:
        plot_types = list(plot_mapping.keys())

    result = {
        "success": True,
        "plots": {},
        "fastqc_dir": str(fastqc_path)
    }

    # Look for Images directory (extracted FastQC output)
    images_dir = fastqc_path / "Images"

    # If Images directory doesn't exist, try to extract from .zip file
    if not images_dir.exists():
        zip_files = list(fastqc_path.parent.glob(f"{fastqc_path.stem}.zip"))
        if not zip_files:
            # Try to find zip with _fastqc suffix
            zip_files = list(fastqc_path.parent.glob(f"{fastqc_path.stem}_fastqc.zip"))

        if zip_files:
            try:
                with zipfile.ZipFile(zip_files[0], 'r') as zip_ref:
                    # Extract only Images directory
                    for file in zip_ref.namelist():
                        if '/Images/' in file and file.endswith('.png'):
                            zip_ref.extract(file, fastqc_path.parent)
                images_dir = fastqc_path / "Images"
            except Exception as e:
                logger.warning(f"Could not extract zip file: {e}")

    if not images_dir or not images_dir.exists():
        # Check if images are directly in the fastqc_dir
        images_dir = fastqc_path

    # Extract requested plots
    for plot_type in plot_types:
        if plot_type in plot_mapping:
            plot_file = images_dir / plot_mapping[plot_type]

            if plot_file.exists():
                try:
                    with open(plot_file, 'rb') as img_file:
                        img_data = img_file.read()
                        img_base64 = base64.b64encode(img_data).decode('utf-8')

                        result["plots"][plot_type] = {
                            "filename": plot_mapping[plot_type],
                            "data": img_base64,
                            "mime_type": "image/png"
                        }
                except Exception as e:
                    logger.error(f"Error reading plot {plot_type}: {e}")
            else:
                logger.warning(f"Plot file not found: {plot_file}")

    result["num_plots_extracted"] = len(result["plots"])

    return result


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools"""
    return TOOLS


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
    """Handle tool calls"""

    try:
        if name == "list_fastq_files":
            directory = arguments.get("directory")
            recursive = arguments.get("recursive", False)

            files = find_fastq_files(directory, recursive)

            return [TextContent(
                type="text",
                text=json.dumps({
                    "num_files": len(files),
                    "files": files
                }, indent=2)
            )]

        elif name == "run_fastqc":
            input_files = arguments.get("input_files", [])
            output_dir = arguments.get("output_dir", "fastqc_output")
            threads = arguments.get("threads", 2)

            result = run_fastqc_analysis(input_files, output_dir, threads)

            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]

        elif name == "run_multiqc":
            input_dir = arguments.get("input_dir")
            output_dir = arguments.get("output_dir", "multiqc_output")

            result = run_multiqc_analysis(input_dir, output_dir)

            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]

        elif name == "parse_fastqc_summary":
            fastqc_dir = arguments.get("fastqc_dir")

            result = parse_fastqc_data(fastqc_dir)

            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]

        elif name == "extract_fastqc_plots":
            fastqc_dir = arguments.get("fastqc_dir")
            plot_types = arguments.get("plots", ["all"])

            result = extract_plots_from_fastqc(fastqc_dir, plot_types)

            if not result.get("success"):
                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]

            # Return both text summary and images
            content_list = []

            # Add text summary
            summary = {
                "success": result["success"],
                "num_plots_extracted": result["num_plots_extracted"],
                "fastqc_dir": result["fastqc_dir"],
                "plot_names": list(result["plots"].keys())
            }
            content_list.append(TextContent(
                type="text",
                text=json.dumps(summary, indent=2)
            ))

            # Add image content for each plot
            for plot_name, plot_data in result["plots"].items():
                content_list.append(ImageContent(
                    type="image",
                    data=plot_data["data"],
                    mimeType=plot_data["mime_type"]
                ))

            return content_list

        elif name == "read_html_file":
            file_path = arguments.get("file_path")
            extract_text = arguments.get("extract_text", False)

            result = read_html_file(file_path, extract_text)

            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]

        elif name == "analyze_html_content":
            file_path = arguments.get("file_path")

            result = analyze_html_structure(file_path)

            return [TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]

        elif name == "generate_chart":
            chart_type = arguments.get("chart_type")
            data = arguments.get("data")
            title = arguments.get("title", "")
            x_label = arguments.get("x_label", "")
            y_label = arguments.get("y_label", "")
            style = arguments.get("style", "seaborn")
            width = arguments.get("width", 800)
            height = arguments.get("height", 600)

            result = generate_chart_from_data(
                chart_type, data, title, x_label, y_label, style, width, height
            )

            if not result.get("success"):
                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]

            # Return both text summary and image
            return [
                TextContent(
                    type="text",
                    text=json.dumps({
                        "success": True,
                        "chart_type": result["chart_type"],
                        "width": result["width"],
                        "height": result["height"]
                    }, indent=2)
                ),
                ImageContent(
                    type="image",
                    data=result["image_data"],
                    mimeType=result["mime_type"]
                )
            ]

        elif name == "extract_and_visualize_qc_data":
            fastqc_dir = arguments.get("fastqc_dir")
            metrics = arguments.get("metrics", ["all"])

            result = extract_and_visualize_qc(fastqc_dir, metrics)

            if not result.get("success"):
                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]

            # Return text summary and chart images
            content_list = [
                TextContent(
                    type="text",
                    text=json.dumps({
                        "success": True,
                        "num_charts": result["num_charts"],
                        "fastqc_dir": result["fastqc_dir"],
                        "chart_names": list(result["charts"].keys())
                    }, indent=2)
                )
            ]

            # Add each chart image
            for chart_name, chart_data in result["charts"].items():
                content_list.append(ImageContent(
                    type="image",
                    data=chart_data,
                    mimeType="image/png"
                ))

            return content_list

        else:
            return [TextContent(
                type="text",
                text=json.dumps({"error": f"Unknown tool: {name}"})
            )]

    except Exception as e:
        logger.error(f"Error executing tool {name}: {e}")
        return [TextContent(
            type="text",
            text=json.dumps({"error": str(e)})
        )]


async def main():
    """Run the MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
