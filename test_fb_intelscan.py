#!/usr/bin/env python3
"""
FB IntelScan Test Harness - Command Line Version
This tests the core functionality without the GUI
"""

import os
import re
from pathlib import Path
import time

class FBIntelScanTester:
    def __init__(self):
        # Directory path (hardcoded as specified)
        self.data_directory = "/home/cts/Desktop/FB-data"
        
    def parse_fb_data(self, line):
        """Parse a line of Facebook data in the expected format"""
        try:
            # Expected format: ID,phone,first_name,last_name,gender,profile_url,full_name,,,email,,,
            parts = line.split(',')
            
            if len(parts) < 7:
                return None
                
            return {
                'fb_id': parts[0] if parts[0] else 'N/A',
                'phone': parts[1] if parts[1] else 'N/A',
                'first_name': parts[2] if parts[2] else 'N/A',
                'last_name': parts[3] if parts[3] else 'N/A',
                'gender': parts[4] if parts[4] else 'N/A',
                'profile_url': parts[5] if parts[5] else 'N/A',
                'full_name': parts[6] if parts[6] else f"{parts[2]} {parts[3]}".strip(),
                'email': parts[10] if len(parts) > 10 and parts[10] else 'N/A',
                'raw_line': line
            }
        except Exception:
            return None
            
    def perform_search(self, query):
        """Perform search through files"""
        results = []
        query_lower = query.lower()
        
        # Check if directory exists
        if not os.path.exists(self.data_directory):
            print(f"❌ Directory not found: {self.data_directory}")
            return results
        
        # Get all .txt files in the directory
        txt_files = list(Path(self.data_directory).glob("*.txt"))
        
        if not txt_files:
            print("❌ No .txt files found in directory")
            return results
            
        total_files = len(txt_files)
        files_processed = 0
        
        print(f"🔍 Found {total_files} .txt files to scan")
        print(f"🔍 Searching for: '{query}'")
        print("-" * 60)
        
        for file_path in txt_files:
            files_processed += 1
            print(f"🔍 Scanning file {files_processed}/{total_files}: {file_path.name}")
            
            try:
                # Stream read the file
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                    for line_num, line in enumerate(file, 1):
                        line = line.strip()
                        if not line:
                            continue
                            
                        # Check if query matches any part of the line
                        if query_lower in line.lower():
                            # Parse the Facebook data format
                            parsed_data = self.parse_fb_data(line)
                            if parsed_data:
                                parsed_data['file'] = file_path.name
                                parsed_data['line'] = line_num
                                results.append(parsed_data)
                                print(f"✅ Found match in {file_path.name} at line {line_num}")
                                
            except Exception as e:
                print(f"Error reading file {file_path}: {e}")
                continue
                
        print("-" * 60)
        print(f"✅ Scan complete! Found {len(results)} matches")
        return results
        
    def display_results(self, results):
        """Display results in target card format"""
        if not results:
            print("❌ No results found")
            return
            
        print("\n" + "="*80)
        print(f"🎯 INTELLIGENCE RESULTS ({len(results)} targets found)")
        print("="*80)
        
        for i, result in enumerate(results, 1):
            print(f"\n📊 TARGET #{i}")
            print("-" * 40)
            print(f"👤 Name: {result['full_name']}")
            print(f"🆔 Facebook ID: {result['fb_id']}")
            if result['phone'] != 'N/A':
                print(f"📱 Phone: {result['phone']}")
            if result['profile_url'] != 'N/A' and result['profile_url'].startswith('http'):
                print(f"🔗 Profile: {result['profile_url']}")
            if result['gender'] != 'N/A':
                print(f"⚧ Gender: {result['gender'].title()}")
            if result['email'] != 'N/A':
                print(f"📧 Email: {result['email']}")
            print(f"📂 Source: {result['file']} (line {result['line']})")
            print("-" * 40)
            
    def run_test(self, query):
        """Run a test search"""
        print("🕵️ FB IntelScan v1.0 - Dark OSINT Scanner (Test Mode)")
        print("="*60)
        print(f"📂 Scanning Directory: {self.data_directory}")
        print()
        
        start_time = time.time()
        results = self.perform_search(query)
        end_time = time.time()
        
        self.display_results(results)
        
        print(f"\n⏱️ Search completed in {end_time - start_time:.2f} seconds")
        return results

def main():
    tester = FBIntelScanTester()
    
    # Test cases
    test_queries = [
        "Ahmed",
        "Smith", 
        "+964",
        "facebook.com",
        "female",
        "john.smith@facebook.com"
    ]
    
    print("🚀 Starting FB IntelScan Test Suite")
    print("="*80)
    
    for query in test_queries:
        print(f"\n🔍 Testing query: '{query}'")
        results = tester.run_test(query)
        print(f"Results: {len(results)} matches found")
        print("\n" + "="*80)
        
        if len(results) > 0:
            break  # Stop after first successful test to avoid too much output
    
    print("\n✅ Test suite completed!")

if __name__ == "__main__":
    main()