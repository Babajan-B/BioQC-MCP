#!/usr/bin/env python3
"""
Simple test script to verify the MCP server works correctly
"""

import json
import subprocess
import sys

def test_server():
    """Test the MCP server by sending it a basic request"""
    
    print("🔍 Testing FastQC & MultiQC MCP Server...")
    print("=" * 60)
    
    # Start the server
    server_path = "/Users/jaan/Desktop/Ai-text/fastqc-multiqc-mcp-server/src/server.py"
    python_path = "/Users/jaan/Desktop/Ai-text/fastqc-multiqc-mcp-server/venv/bin/python3"
    
    print(f"\n1. Starting server: {server_path}")
    
    try:
        # Test server initialization request
        initialize_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        print("\n2. Sending initialize request...")
        print(f"   Request: {json.dumps(initialize_request, indent=2)}")
        
        # Run server and send request
        process = subprocess.Popen(
            [python_path, server_path],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Send request
        request_str = json.dumps(initialize_request) + "\n"
        stdout, stderr = process.communicate(input=request_str, timeout=10)
        
        print("\n3. Server Response:")
        print(f"   STDOUT: {stdout[:500]}...")  # First 500 chars
        
        if stderr:
            print(f"   STDERR: {stderr[:500]}...")
        
        # Try to parse response
        try:
            for line in stdout.strip().split('\n'):
                if line.strip():
                    response = json.loads(line)
                    print("\n4. ✅ Server Response (JSON):")
                    print(json.dumps(response, indent=2))
                    
                    if "result" in response:
                        capabilities = response.get("result", {}).get("capabilities", {})
                        print("\n5. ✅ Server Capabilities:")
                        print(json.dumps(capabilities, indent=2))
                        
                        tools = capabilities.get("tools", {})
                        if tools:
                            print("\n6. ✅ Tools Available!")
                            return True
                    break
        except json.JSONDecodeError as e:
            print(f"\n❌ Failed to parse JSON response: {e}")
            print(f"   Raw output: {stdout}")
            return False
        
        print("\n✅ Server test completed!")
        return True
        
    except subprocess.TimeoutExpired:
        print("\n❌ Server request timed out")
        process.kill()
        return False
    except Exception as e:
        print(f"\n❌ Error testing server: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_server()
    sys.exit(0 if success else 1)
