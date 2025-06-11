import customtkinter as ctk
import tkinter as tk
from tkinter import scrolledtext
import os
import threading
import re
from pathlib import Path
import time

class FBIntelScan:
    def __init__(self):
        # Set the appearance mode and color theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        
        # Initialize the main window
        self.root = ctk.CTk()
        self.root.title("FB IntelScan v1.0 - Dark OSINT File Scanner")
        self.root.geometry("1200x800")
        self.root.configure(fg_color="#0a0a0a")
        
        # Directory path (hardcoded as specified)
        self.data_directory = "/home/cts/Desktop/FB-data"
        
        # Search control
        self.is_scanning = False
        self.scan_thread = None
        
        # Create the GUI
        self.create_widgets()
        
    def create_widgets(self):
        # Main container
        main_frame = ctk.CTkFrame(self.root, fg_color="#0a0a0a")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame, 
            text="🕵️ FB IntelScan v1.0 - Dark OSINT Scanner", 
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#00ff41"
        )
        title_label.pack(pady=(0, 20))
        
        # Directory info
        dir_label = ctk.CTkLabel(
            main_frame,
            text=f"📂 Scanning Directory: {self.data_directory}",
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        )
        dir_label.pack(pady=(0, 20))
        
        # Search frame
        search_frame = ctk.CTkFrame(main_frame, fg_color="#1a1a1a")
        search_frame.pack(fill="x", pady=(0, 20))
        
        # Search bar
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="🔍 Enter search query (ID, phone, name, email, location...)",
            font=ctk.CTkFont(size=14),
            height=40,
            fg_color="#2a2a2a",
            border_color="#00ff41",
            text_color="#ffffff"
        )
        self.search_entry.pack(side="left", fill="x", expand=True, padx=10, pady=10)
        
        # Search button
        self.search_button = ctk.CTkButton(
            search_frame,
            text="🔎 SCAN",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            width=100,
            fg_color="#00ff41",
            hover_color="#00cc33",
            text_color="#000000",
            command=self.start_search
        )
        self.search_button.pack(side="right", padx=10, pady=10)
        
        # Stop button
        self.stop_button = ctk.CTkButton(
            search_frame,
            text="🛑 STOP",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            width=100,
            fg_color="#ff4444",
            hover_color="#cc3333",
            text_color="#ffffff",
            command=self.stop_search
        )
        self.stop_button.pack(side="right", padx=(0, 10), pady=10)
        
        # Status label
        self.status_label = ctk.CTkLabel(
            main_frame,
            text="⏳ Ready to scan...",
            font=ctk.CTkFont(size=12),
            text_color="#888888"
        )
        self.status_label.pack(pady=(0, 10))
        
        # Results container (hidden by default)
        self.results_frame = ctk.CTkScrollableFrame(
            main_frame,
            fg_color="#1a1a1a",
            height=500
        )
        # Initially hidden
        
        # Bind Enter key to search
        self.search_entry.bind("<Return>", lambda event: self.start_search())
        
    def start_search(self):
        query = self.search_entry.get().strip()
        if not query:
            self.status_label.configure(text="❌ Please enter a search query")
            return
            
        if self.is_scanning:
            self.status_label.configure(text="⚠️ Scan already in progress...")
            return
            
        # Check if directory exists
        if not os.path.exists(self.data_directory):
            self.status_label.configure(text=f"❌ Directory not found: {self.data_directory}")
            return
            
        self.is_scanning = True
        self.search_button.configure(state="disabled")
        self.status_label.configure(text=f"🔍 Scanning for: '{query}'...")
        
        # Clear previous results
        if hasattr(self, 'results_frame') and self.results_frame.winfo_exists():
            self.results_frame.destroy()
            
        # Start search in a separate thread
        self.scan_thread = threading.Thread(target=self.perform_search, args=(query,))
        self.scan_thread.daemon = True
        self.scan_thread.start()
        
    def stop_search(self):
        if self.is_scanning:
            self.is_scanning = False
            self.status_label.configure(text="🛑 Scan stopped by user")
            self.search_button.configure(state="normal")
            
    def perform_search(self, query):
        try:
            results = []
            query_lower = query.lower()
            
            # Get all .txt files in the directory
            txt_files = list(Path(self.data_directory).glob("*.txt"))
            
            if not txt_files:
                self.root.after(0, lambda: self.status_label.configure(text="❌ No .txt files found in directory"))
                self.is_scanning = False
                self.search_button.configure(state="normal")
                return
                
            total_files = len(txt_files)
            files_processed = 0
            
            for file_path in txt_files:
                if not self.is_scanning:
                    break
                    
                files_processed += 1
                self.root.after(0, lambda f=files_processed, t=total_files: 
                    self.status_label.configure(text=f"🔍 Scanning file {f}/{t}: {file_path.name}"))
                
                try:
                    # Stream read the file
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                        for line_num, line in enumerate(file, 1):
                            if not self.is_scanning:
                                break
                                
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
                                    
                                    # Update UI with results in real-time
                                    self.root.after(0, lambda r=results: self.update_results_display(r))
                                    
                except Exception as file_error:
                    print(f"Error reading file {file_path}: {file_error}")
                    continue
                    
            # Final update
            if self.is_scanning:
                final_count = len(results)
                self.root.after(0, lambda: self.status_label.configure(
                    text=f"✅ Scan complete! Found {final_count} matches"))
            
        except Exception as e:
            self.root.after(0, lambda: self.status_label.configure(text=f"❌ Error: {str(e)}"))
        finally:
            self.is_scanning = False
            self.root.after(0, lambda: self.search_button.configure(state="normal"))
            
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
            
    def update_results_display(self, results):
        """Update the results display with target cards"""
        if not results:
            return
            
        # Show results frame if not already shown
        if not hasattr(self, 'results_frame') or not self.results_frame.winfo_exists():
            self.results_frame = ctk.CTkScrollableFrame(
                self.root,
                fg_color="#1a1a1a",
                height=400
            )
            self.results_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
            
        # Clear existing results
        for widget in self.results_frame.winfo_children():
            widget.destroy()
            
        # Add header
        header_label = ctk.CTkLabel(
            self.results_frame,
            text=f"🎯 INTELLIGENCE RESULTS ({len(results)} targets found)",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#00ff41"
        )
        header_label.pack(pady=(10, 20))
        
        # Create target cards
        for i, result in enumerate(results):
            self.create_target_card(result, i)
            
    def create_target_card(self, data, index):
        """Create a target card for each result"""
        # Card container
        card_frame = ctk.CTkFrame(
            self.results_frame,
            fg_color="#2a2a2a",
            border_color="#00ff41",
            border_width=1
        )
        card_frame.pack(fill="x", padx=10, pady=5)
        
        # Header with name and ID
        header_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=15, pady=(15, 5))
        
        name_label = ctk.CTkLabel(
            header_frame,
            text=f"👤 {data['full_name']}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#ffffff"
        )
        name_label.pack(side="left")
        
        id_label = ctk.CTkLabel(
            header_frame,
            text=f"ID: {data['fb_id']}",
            font=ctk.CTkFont(size=12),
            text_color="#00ff41"
        )
        id_label.pack(side="right")
        
        # Details grid
        details_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
        details_frame.pack(fill="x", padx=15, pady=5)
        
        # Phone (highlighted)
        if data['phone'] != 'N/A':
            phone_label = ctk.CTkLabel(
                details_frame,
                text=f"📱 {data['phone']}",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#ff6b6b"
            )
            phone_label.pack(anchor="w")
            
        # Profile URL (highlighted)
        if data['profile_url'] != 'N/A' and data['profile_url'].startswith('http'):
            url_label = ctk.CTkLabel(
                details_frame,
                text=f"🔗 {data['profile_url']}",
                font=ctk.CTkFont(size=12),
                text_color="#4ecdc4"
            )
            url_label.pack(anchor="w")
            
        # Additional info
        info_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
        info_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        # Gender and Email
        if data['gender'] != 'N/A':
            gender_label = ctk.CTkLabel(
                info_frame,
                text=f"⚧ {data['gender'].title()}",
                font=ctk.CTkFont(size=11),
                text_color="#999999"
            )
            gender_label.pack(side="left")
            
        if data['email'] != 'N/A':
            email_label = ctk.CTkLabel(
                info_frame,
                text=f"📧 {data['email']}",
                font=ctk.CTkFont(size=11),
                text_color="#999999"
            )
            email_label.pack(side="right")
            
        # Separator line
        separator = ctk.CTkFrame(self.results_frame, height=1, fg_color="#444444")
        separator.pack(fill="x", padx=20, pady=2)
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = FBIntelScan()
    app.run()
