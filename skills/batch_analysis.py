# Batch Analysis Pipeline
# Execute with: run_qc_pipeline tool
# Usage: Process multiple samples with progress tracking

# Configuration
INPUT_DIR = '/path/to/samples'
OUTPUT_BASE = './batch_results'

# Discover files
files = list_fastq_files(INPUT_DIR)
total = len(files)
print(f"Batch processing {total} files...")

results = {
    "total_files": total,
    "processed": 0,
    "failed": 0,
    "samples": []
}

# Process each file
for i, f in enumerate(files):
    print(f"[{i+1}/{total}] Processing: {f['name']} ({f['size_mb']} MB)")
    
    sample_name = f['name'].replace('.fastq.gz', '').replace('.fastq', '')
    output_dir = f"{OUTPUT_BASE}/{sample_name}"
    
    qc_result = run_fastqc([f['path']], output_dir=output_dir)
    
    if qc_result['success']:
        results["processed"] += 1
        results["samples"].append({
            "name": sample_name,
            "status": "success",
            "report": qc_result.get('reports', [None])[0]
        })
    else:
        results["failed"] += 1
        results["samples"].append({
            "name": sample_name,
            "status": "failed",
            "error": qc_result.get('error', 'Unknown')
        })

# Summary
print(f"\n=== Batch Complete ===")
print(f"Processed: {results['processed']}/{total}")
print(f"Failed: {results['failed']}")

# Generate combined MultiQC if any succeeded
if results["processed"] > 0:
    multiqc = run_multiqc(OUTPUT_BASE, output_dir=f"{OUTPUT_BASE}/combined_report")
    if multiqc['success']:
        results["combined_report"] = multiqc['report']
        print(f"Combined report: {multiqc['report']}")

result = results
