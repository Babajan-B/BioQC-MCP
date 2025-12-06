#!/usr/bin/env python3
"""Test the run_qc_pipeline functionality"""
import sys
sys.path.insert(0, 'src')
from server import execute_qc_pipeline

# Test 1: Basic execution
print("Test 1: Basic execution")
result = execute_qc_pipeline('print("Hello from pipeline!"); x = 2 + 2; print(f"2+2 = {x}")')
print(f"Success: {result['success']}")
print(f"Output: {result['stdout']}")
print()

# Test 2: Using built-in functions
print("Test 2: Using built-ins")
result = execute_qc_pipeline('data = [1, 2, 3, 4, 5]; print(f"Sum: {sum(data)}, Max: {max(data)}")')
print(f"Success: {result['success']}")
print(f"Output: {result['stdout']}")
print()

# Test 3: Access list_fastq_files function
print("Test 3: Testing list_fastq_files")
result = execute_qc_pipeline('files = list_fastq_files("/Users/jaan/Desktop/Alaa"); print(f"Found {len(files)} files")')
print(f"Success: {result['success']}")
print(f"Output: {result['stdout']}")
if not result['success']:
    print(f"Error: {result.get('error', 'Unknown')}")
print()

# Test 4: Variables captured
print("Test 4: Variable capture")
result = execute_qc_pipeline('x = 42; y = "hello"; result = {"answer": x, "message": y}')
print(f"Success: {result['success']}")
print(f"Variables: {result['variables']}")
print(f"Result: {result['result']}")
print()

print("All tests complete!")
