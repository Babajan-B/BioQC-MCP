# Quick Quality Check
# Execute with: run_qc_pipeline tool
# Usage: Fast sanity check on FASTQ files

# Configuration  
INPUT_DIR = '/path/to/samples'

# Find files
files = list_fastq_files(INPUT_DIR)
print(f"Found {len(files)} FASTQ files\n")

# Quick summary
total_size = sum(f['size_mb'] for f in files)
print(f"Total data: {total_size:.1f} MB")
print(f"Average size: {total_size/len(files):.1f} MB per file\n")

# List files
print("Files:")
for f in files[:10]:  # Show first 10
    print(f"  - {f['name']} ({f['size_mb']} MB)")

if len(files) > 10:
    print(f"  ... and {len(files) - 10} more files")

result = {
    "num_files": len(files),
    "total_size_mb": round(total_size, 2),
    "avg_size_mb": round(total_size/len(files), 2) if files else 0,
    "files": files
}
