#!/bin/bash

# Test FastQC with real FASTQ files
# This demonstrates the MCP server's run_fastqc tool functionality

echo "=========================================="
echo "FastQC Real Data Test"
echo "=========================================="
echo ""

# Input files
FASTQ_FILE="/Users/jaan/Desktop/Alaa/Alaa_R1.fastq.gz"
OUTPUT_DIR="/Users/jaan/Desktop/Alaa/fastqc_results"

echo "Input file: $FASTQ_FILE"
echo "Output directory: $OUTPUT_DIR"
echo ""

# Create output directory
echo "Creating output directory..."
mkdir -p "$OUTPUT_DIR"

# Check if file exists
if [ ! -f "$FASTQ_FILE" ]; then
    echo "❌ Error: FASTQ file not found!"
    exit 1
fi

echo "✓ FASTQ file found ($(ls -lh "$FASTQ_FILE" | awk '{print $5}'))"
echo ""

# Run FastQC
echo "Running FastQC analysis..."
echo "Command: fastqc -o $OUTPUT_DIR -t 2 $FASTQ_FILE"
echo ""

fastqc -o "$OUTPUT_DIR" -t 2 "$FASTQ_FILE"

EXIT_CODE=$?

echo ""
echo "=========================================="
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ FastQC analysis completed successfully!"
    echo ""
    echo "Output files created:"
    ls -lh "$OUTPUT_DIR"
    echo ""
    echo "HTML Report: $OUTPUT_DIR/Alaa_R1_fastqc.html"
    echo "ZIP Archive: $OUTPUT_DIR/Alaa_R1_fastqc.zip"
    echo ""
    echo "You can open the HTML report in your browser to view results"
else
    echo "❌ FastQC analysis failed with exit code: $EXIT_CODE"
fi
echo "=========================================="
