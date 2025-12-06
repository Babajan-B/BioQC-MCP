# Full QC Pipeline
# Execute with: run_qc_pipeline tool
# Usage: Adapt paths and parameters for your data

# Configuration
INPUT_DIR = '/path/to/fastq/files'
OUTPUT_DIR = './fastqc_results'
MULTIQC_DIR = './multiqc_report'

# Step 1: Discover FASTQ files
files = list_fastq_files(INPUT_DIR)
print(f"Found {len(files)} FASTQ files")

if len(files) == 0:
    print("No FASTQ files found!")
    result = {"success": False, "error": "No files found"}
else:
    # Step 2: Run FastQC on all files
    file_paths = [f['path'] for f in files]
    fastqc_result = run_fastqc(file_paths, output_dir=OUTPUT_DIR)
    
    if fastqc_result['success']:
        print(f"FastQC complete: {fastqc_result['num_files_analyzed']} files analyzed")
        
        # Step 3: Generate MultiQC aggregate report
        multiqc_result = run_multiqc(OUTPUT_DIR, output_dir=MULTIQC_DIR)
        
        if multiqc_result['success']:
            print(f"MultiQC report: {multiqc_result['report']}")
        else:
            print(f"MultiQC failed: {multiqc_result.get('error', 'Unknown error')}")
        
        # Step 4: Parse summary for key metrics
        # (Get first sample's metrics as example)
        if fastqc_result.get('reports'):
            first_report = fastqc_result['reports'][0]
            fastqc_data_dir = first_report.replace('_fastqc.html', '_fastqc')
            summary = parse_fastqc_summary(fastqc_data_dir)
            print(f"Sample metrics: {summary.get('metrics', {})}")
        
        result = {
            "success": True,
            "files_analyzed": len(files),
            "fastqc_reports": fastqc_result.get('reports', []),
            "multiqc_report": multiqc_result.get('report'),
            "output_directory": OUTPUT_DIR
        }
    else:
        print(f"FastQC failed: {fastqc_result.get('error', 'Unknown error')}")
        result = fastqc_result
