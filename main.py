#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import customtkinter as ctk
import threading
import time
import os
import pyperclip
import webbrowser
import sqlite3
import re
from functools import lru_cache
import queue
from concurrent.futures import ThreadPoolExecutor
import json

DATA_PATH = "/var/www/html/king/iraq-cts/FB-data.json"
DB_PATH = "fb_search.db"
RESULTS_PER_PAGE = 25
MAX_WORKERS = 4

FIELDS_TO_DISPLAY = ["phone", "name", "profile", "job", "study", "username", "gender", "location"]

class ModernCard(ctk.CTkFrame):
    def __init__(self, parent, data, **kwargs):
        super().__init__(parent, corner_radius=15, fg_color=("gray90", "gray15"), 
                        border_width=1, border_color=("gray70", "gray30"), **kwargs)
        self.data = data
        self.setup_card()
        
    def setup_card(self):
        # Header with name and status indicator
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        name = self.data.get("name", "Unknown")
        username = self.data.get("username", "")
        
        # Status indicator
        status_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        status_frame.pack(anchor="w", fill="x")
        
        # Online status indicator (green dot)
        status_dot = ctk.CTkFrame(status_frame, width=12, height=12, corner_radius=6,
                                 fg_color=("#2d7016", "#4da82b"))
        status_dot.pack(side="left", padx=(0, 8), pady=8)
        
        name_frame = ctk.CTkFrame(status_frame, fg_color="transparent")
        name_frame.pack(side="left", fill="x", expand=True)
        
        ctk.CTkLabel(
            name_frame, 
            text=f"👤 {name}", 
            font=ctk.CTkFont("Segoe UI", 18, weight="bold"),
            text_color=("gray10", "white"),
            anchor="w"
        ).pack(anchor="w")
        
        if username:
            ctk.CTkLabel(
                name_frame, 
                text=f"@{username}", 
                font=ctk.CTkFont("Segoe UI", 12),
                text_color=("gray40", "gray60"),
                anchor="w"
            ).pack(anchor="w")
        
        # Main content in grid layout
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Configure grid
        content_frame.grid_columnconfigure((0, 1), weight=1)
        
        row = 0
        
        # Phone (priority info)
        phone = self.data.get("phone", "")
        if phone:
            self.add_info_field(content_frame, "📱 Phone", phone, row, 0, 
                              fg_color=("#e8f4fd", "#1a365d"), is_copyable=True)
            row += 1
        
        # Gender and Location in same row
        gender = self.data.get("gender", "")
        location = self.data.get("location", "")
        
        if gender:
            self.add_info_field(content_frame, "⚧ Gender", gender, row, 0)
        if location:
            self.add_info_field(content_frame, "📍 Location", location, row, 1)
        if gender or location:
            row += 1
        
        # Job and Study
        job = self.data.get("job", "")
        study = self.data.get("study", "")
        
        if job:
            self.add_info_field(content_frame, "💼 Job", job, row, 0)
        if study:
            self.add_info_field(content_frame, "🎓 Education", study, row, 1)
        if job or study:
            row += 1
        
        # Action buttons
        self.setup_action_buttons()
        
    def add_info_field(self, parent, label, value, row, col, fg_color=None, is_copyable=False):
        if not value or str(value).strip() == "":
            return
            
        field_frame = ctk.CTkFrame(parent, fg_color=fg_color or ("gray85", "gray25"), 
                                  corner_radius=10)
        field_frame.grid(row=row, column=col, sticky="ew", padx=5, pady=3)
        
        ctk.CTkLabel(
            field_frame, 
            text=label, 
            font=ctk.CTkFont("Segoe UI", 11, weight="bold"),
            text_color=("gray20", "gray80")
        ).pack(anchor="w", padx=12, pady=(8, 2))
        
        value_text = str(value)[:45] + "..." if len(str(value)) > 45 else str(value)
        value_label = ctk.CTkLabel(
            field_frame, 
            text=value_text,
            font=ctk.CTkFont("Segoe UI", 12),
            text_color=("gray10", "white"),
            anchor="w"
        )
        value_label.pack(anchor="w", padx=12, pady=(0, 8))
        
        if is_copyable:
            value_label.bind("<Button-1>", lambda e: self.copy_to_clipboard(value))
            value_label.configure(cursor="hand2")
        
    def setup_action_buttons(self):
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(10, 20))
        
        # Profile button
        profile_url = self.data.get("profile", "")
        if profile_url and "http" in profile_url:
            profile_btn = ctk.CTkButton(
                button_frame,
                text="🔗 Open Profile",
                command=lambda: webbrowser.open(profile_url),
                width=130,
                height=35,
                font=ctk.CTkFont("Segoe UI", 11, weight="bold"),
                fg_color=("#1565c0", "#0d47a1"),
                hover_color=("#1976d2", "#1565c0"),
                corner_radius=8
            )
            profile_btn.pack(side="left", padx=(0, 8))
        
        # Copy phone button
        phone = self.data.get("phone", "")
        if phone:
            phone_btn = ctk.CTkButton(
                button_frame,
                text="📋 Copy Phone",
                command=lambda: self.copy_to_clipboard(phone),
                width=120,
                height=35,
                font=ctk.CTkFont("Segoe UI", 11, weight="bold"),
                fg_color=("#2e7d32", "#1b5e20"),
                hover_color=("#388e3c", "#2e7d32"),
                corner_radius=8
            )
            phone_btn.pack(side="left", padx=8)
        
        # Copy all data button
        copy_all_btn = ctk.CTkButton(
            button_frame,
            text="📄 Copy All",
            command=self.copy_all_data,
            width=110,
            height=35,
            font=ctk.CTkFont("Segoe UI", 11, weight="bold"),
            fg_color=("#f57c00", "#e65100"),
            hover_color=("#ff9800", "#f57c00"),
            corner_radius=8
        )
        copy_all_btn.pack(side="left", padx=8)
    
    def copy_to_clipboard(self, text):
        try:
            pyperclip.copy(str(text))
            self.show_notification("Copied! ✓")
        except Exception:
            pass
    
    def copy_all_data(self):
        try:
            data_text = "\n".join([f"{k}: {v}" for k, v in self.data.items() if v])
            pyperclip.copy(data_text)
            self.show_notification("All data copied! ✓")
        except Exception:
            pass
    
    def show_notification(self, message):
        notification = ctk.CTkLabel(
            self, 
            text=message, 
            fg_color=("#4caf50", "#2e7d32"),
            corner_radius=8,
            text_color="white",
            font=ctk.CTkFont("Segoe UI", 11, weight="bold")
        )
        notification.place(relx=0.5, rely=0.1, anchor="center")
        self.after(2000, notification.destroy)

class DatabaseManager:
    """Manages database operations with efficient memory usage"""
    
    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = None
        self.create_database()
        
    def create_database(self):
        """Create database with proper indexing"""
        self.conn = sqlite3.connect(self.db_path)
        cur = self.conn.cursor()
        
        # Create main table with appropriate data types
        cur.execute('''
            CREATE TABLE IF NOT EXISTS fb_records (
                id INTEGER PRIMARY KEY,
                phone TEXT,
                name TEXT,
                profile TEXT,
                job TEXT,
                study TEXT,
                username TEXT,
                gender TEXT,
                location TEXT
            )
        ''')
        
        # Create indexes for faster searching
        cur.execute('CREATE INDEX IF NOT EXISTS idx_phone ON fb_records(phone)')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_location ON fb_records(location)')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_job ON fb_records(job)')
        cur.execute('CREATE INDEX IF NOT EXISTS idx_study ON fb_records(study)')
        
        # Create FTS virtual table for full-text search
        cur.execute('''
            CREATE VIRTUAL TABLE IF NOT EXISTS fts_fb_records 
            USING fts5(phone, name, location, job, study, username, gender)
        ''')
        
        self.conn.commit()
    
    def insert_records(self, records):
        """Insert records in batches to minimize memory usage"""
        try:
            cur = self.conn.cursor()
            
            # Insert in batches
            batch_size = 10000
            for i in range(0, len(records), batch_size):
                batch = records[i:i+batch_size]
                
                # Insert into main table
                cur.executemany('''
                    INSERT INTO fb_records 
                    (phone, name, profile, job, study, username, gender, location)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', [(
                    r.get("phone", ""),
                    r.get("name", ""),
                    r.get("profile", ""),
                    r.get("job", ""),
                    r.get("study", ""),
                    r.get("username", ""),
                    r.get("gender", ""),
                    r.get("location", "")
                ) for r in batch])
                
                # Insert into FTS table
                cur.executemany('''
                    INSERT INTO fts_fb_records 
                    (phone, name, location, job, study, username, gender)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', [(
                    r.get("phone", ""),
                    r.get("name", ""),
                    r.get("location", ""),
                    r.get("job", ""),
                    r.get("study", ""),
                    r.get("username", ""),
                    r.get("gender", "")
                ) for r in batch])
                
                self.conn.commit()
                
            return True
        except Exception as e:
            print(f"Database insert error: {e}")
            return False
    
    def count_records(self):
        """Count total records in database"""
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM fb_records")
        return cur.fetchone()[0]
    
    def search(self, query, offset=0, limit=RESULTS_PER_PAGE):
        """Perform efficient search using database indexes"""
        cur = self.conn.cursor()
        
        if not query.strip():
            # Return all results with pagination
            cur.execute("""
                SELECT phone, name, profile, job, study, username, gender, location
                FROM fb_records
                ORDER BY id
                LIMIT ? OFFSET ?
            """, (limit, offset))
            return cur.fetchall()
        
        # Use FTS for text search
        query_terms = query.split()
        fts_query = " AND ".join([f'"{term}"' for term in query_terms])
        
        cur.execute(f"""
            SELECT phone, name, profile, job, study, username, gender, location
            FROM fts_fb_records
            WHERE fts_fb_records MATCH ?
            ORDER BY rank
            LIMIT ? OFFSET ?
        """, (fts_query, limit, offset))
        
        return cur.fetchall()
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

class EfficientDataLoader:
    """Loads data efficiently with minimal memory footprint"""
    
    @staticmethod
    def parse_line(line):
        """Parse a single line of CSV data with error handling"""
        try:
            if not line.strip():
                return None
            
            # Split the line by commas, considering potential quoted fields
            parts = [part.strip() for part in line.split(',')]
            
            # Ensure the line has enough parts to extract required fields
            if len(parts) < 13:
                print(f"Skipping malformed line: {line.strip()}")  # Debugging log
                return None
            
            # Map the parts to the expected fields
            return {
                "phone": parts[1],
                "name": parts[2],
                "profile": parts[5],
                "job": parts[7],
                "study": parts[11],
                "username": parts[0],
                "gender": parts[4],
                "location": parts[9]
            }
        except Exception as e:
            print(f"Error parsing line: {line.strip()} - {e}")  # Debugging log
            return None

    @staticmethod
    def load_to_database(file_path, db_manager, progress_callback=None):
        """Load data directly to database with streaming"""
        total_lines = 0
        processed = 0
        records_batch = []
        batch_size = 1000
        
        # Count total lines first
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for _ in f:
                total_lines += 1
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                record = EfficientDataLoader.parse_line(line)
                if record:
                    records_batch.append(record)
                    
                    # Process in batches
                    if len(records_batch) >= batch_size:
                        db_manager.insert_records(records_batch)
                        processed += len(records_batch)
                        records_batch = []
                        
                        if progress_callback:
                            progress = processed / total_lines
                            progress_callback(progress, processed)
            
            # Process remaining records
            if records_batch:
                db_manager.insert_records(records_batch)
                processed += len(records_batch)
                
                if progress_callback:
                    progress = processed / total_lines
                    progress_callback(progress, processed)
        
        return processed

class FBSearchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🚀 FB Intelligence Search - Memory Efficient")
        self.root.geometry("1400x900")
        self.root.minsize(1200, 700)
        
        # Set modern theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.db_manager = DatabaseManager(DB_PATH)
        self.filtered_data = []
        self.current_page = 0
        self.search_active = False
        self.last_search_term = ""
        self.search_queue = queue.Queue()
        self.total_records = 0

        self.setup_ui()
        self.start_background_workers()
        self.check_data_availability()

    def setup_ui(self):
        # Main container
        main_container = ctk.CTkFrame(self.root, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=25, pady=25)
        
        # Modern header with gradient effect
        header_frame = ctk.CTkFrame(main_container, height=100, 
                                   fg_color=("gray88", "gray18"),
                                   corner_radius=20)
        header_frame.pack(fill="x", pady=(0, 25))
        header_frame.pack_propagate(False)
        
        header_content = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_content.pack(expand=True, fill="both")
        
        title_frame = ctk.CTkFrame(header_content, fg_color="transparent")
        title_frame.pack(expand=True)
        
        ctk.CTkLabel(
            title_frame, 
            text="🚀 Facebook Intelligence Search",
            font=ctk.CTkFont("Segoe UI", 28, weight="bold")
        ).pack(pady=15)
        
        ctk.CTkLabel(
            title_frame, 
            text="Memory-Efficient Search Engine",
            font=ctk.CTkFont("Segoe UI", 14),
            text_color=("gray40", "gray70")
        ).pack()
        
        # Advanced search section
        search_frame = ctk.CTkFrame(main_container, fg_color=("gray85", "gray20"),
                                   corner_radius=20)
        search_frame.pack(fill="x", pady=(0, 25))
        
        search_container = ctk.CTkFrame(search_frame, fg_color="transparent")
        search_container.pack(pady=25, padx=30, fill="x")
        
        # Search input with modern styling
        search_label_frame = ctk.CTkFrame(search_container, fg_color="transparent")
        search_label_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(
            search_label_frame, 
            text="🔍 Smart Search", 
            font=ctk.CTkFont("Segoe UI", 18, weight="bold")
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            search_label_frame, 
            text="Search by name, phone, location, job, or any keyword (Arabic/English supported)", 
            font=ctk.CTkFont("Segoe UI", 12),
            text_color=("gray40", "gray70")
        ).pack(anchor="w")
        
        # Search controls
        search_controls = ctk.CTkFrame(search_container, fg_color="transparent")
        search_controls.pack(fill="x")
        
        self.search_var = ctk.StringVar()
        self.search_var.trace("w", self.on_search_change)
        
        self.search_entry = ctk.CTkEntry(
            search_controls, 
            textvariable=self.search_var, 
            width=600, 
            height=50,
            font=ctk.CTkFont("Segoe UI", 16),
            placeholder_text="Type to search... (ابحث هنا)",
            corner_radius=15,
            border_width=2
        )
        self.search_entry.pack(side="left", padx=(0, 15))
        
        self.search_btn = ctk.CTkButton(
            search_controls, 
            text="🚀 Search",
            command=self.instant_search,
            width=120,
            height=50,
            font=ctk.CTkFont("Segoe UI", 14, weight="bold"),
            corner_radius=15
        )
        self.search_btn.pack(side="left", padx=8)
        
        self.clear_btn = ctk.CTkButton(
            search_controls, 
            text="🗑 Clear",
            command=self.clear_search,
            width=100,
            height=50,
            font=ctk.CTkFont("Segoe UI", 14),
            fg_color=("gray55", "gray35"),
            hover_color=("gray45", "gray25"),
            corner_radius=15
        )
        self.clear_btn.pack(side="left", padx=8)
        
        # Status section
        status_section = ctk.CTkFrame(search_frame, fg_color="transparent")
        status_section.pack(fill="x", padx=30, pady=(0, 25))
        
        self.progress = ctk.CTkProgressBar(status_section, width=500, height=12,
                                          corner_radius=6)
        self.progress.set(0)
        self.progress.pack(pady=8)
        
        self.progress_label = ctk.CTkLabel(
            status_section, 
            text="Initializing memory-efficient search engine...", 
            font=ctk.CTkFont("Segoe UI", 13, weight="bold")
        )
        self.progress_label.pack()
        
        # Results section with modern styling
        results_frame = ctk.CTkFrame(main_container, fg_color=("gray82", "gray22"),
                                    corner_radius=20)
        results_frame.pack(fill="both", expand=True, pady=(0, 25))
        
        # Results header
        results_header = ctk.CTkFrame(results_frame, height=60, fg_color="transparent")
        results_header.pack(fill="x", padx=30, pady=(25, 15))
        results_header.pack_propagate(False)
        
        self.status_label = ctk.CTkLabel(
            results_header, 
            text="Ready for efficient search...",
            font=ctk.CTkFont("Segoe UI", 18, weight="bold")
        )
        self.status_label.pack(anchor="w")
        
        # Results container with smooth scrolling
        self.results_container = ctk.CTkScrollableFrame(
            results_frame, 
            fg_color="transparent"
        )
        self.results_container.pack(fill="both", expand=True, padx=30, pady=(0, 25))
        
        # Modern navigation
        nav_frame = ctk.CTkFrame(main_container, height=70, 
                                fg_color=("gray85", "gray20"),
                                corner_radius=20)
        nav_frame.pack(fill="x")
        nav_frame.pack_propagate(False)
        
        nav_container = ctk.CTkFrame(nav_frame, fg_color="transparent")
        nav_container.pack(expand=True)
        
        self.prev_button = ctk.CTkButton(
            nav_container, 
            text="⬅ Previous", 
            command=self.prev_page,
            width=140,
            height=45,
            font=ctk.CTkFont("Segoe UI", 13, weight="bold"),
            state="disabled",
            corner_radius=12
        )
        self.prev_button.pack(side='left', padx=15, pady=12)
        
        self.page_label = ctk.CTkLabel(
            nav_container, 
            text="Page 1", 
            font=ctk.CTkFont("Segoe UI", 16, weight="bold")
        )
        self.page_label.pack(side='left', padx=30, pady=12)
        
        self.next_button = ctk.CTkButton(
            nav_container, 
            text="Next ➡", 
            command=self.next_page,
            width=140,
            height=45,
            font=ctk.CTkFont("Segoe UI", 13, weight="bold"),
            state="disabled",
            corner_radius=12
        )
        self.next_button.pack(side='left', padx=15, pady=12)

    def start_background_workers(self):
        """Start background worker threads for processing"""
        self.executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)

    def check_data_availability(self):
        """Check if data is already loaded in database"""
        self.total_records = self.db_manager.count_records()
        
        if self.total_records > 0:
            self.progress.set(1.0)
            self.progress_label.configure(
                text=f"⚡ Found {self.total_records:,} records in database"
            )
            return
        
        # If no data, start loading
        threading.Thread(target=self.load_data_to_database, daemon=True).start()

    def load_data_to_database(self):
        """Load data directly to database with minimal memory usage"""
        if not os.path.exists(DATA_PATH):
            self.progress_label.configure(text="❌ Data file not found")
            return

        # Efficient loading with minimal memory footprint
        start_time = time.time()
        
        def progress_callback(progress, count):
            self.progress.set(progress)
            self.progress_label.configure(
                text=f"🚀 Loading to database... {count:,} records ({progress*100:.1f}%)"
            )
        
        processed_count = EfficientDataLoader.load_to_database(
            DATA_PATH, 
            self.db_manager, 
            progress_callback
        )
        
        self.total_records = processed_count
        
        load_time = time.time() - start_time
        self.progress.set(1.0)
        self.progress_label.configure(
            text=f"🚀 Database ready! {self.total_records:,} records in {load_time:.2f}s"
        )

    def on_search_change(self, *args):
        """Instant search with debouncing"""
        if hasattr(self, '_search_timer'):
            self.root.after_cancel(self._search_timer)
        self._search_timer = self.root.after(300, self.instant_search)

    def instant_search(self):
        """Efficient search using database"""
        if self.search_active:
            print("Search is already active. Skipping...")
            return
            
        search_term = self.search_var.get().strip()
        print(f"Search term: {search_term}")  # Debugging log
        if search_term == self.last_search_term:
            print("Search term is the same as the last one. Skipping...")
            return  # Remove this return to allow repeated searches with the same term
            
        self.search_active = True
        self.last_search_term = search_term
        
        # Execute search in background
        future = self.executor.submit(self.perform_database_search, search_term)
        threading.Thread(target=self.handle_search_result, args=(future,), daemon=True).start()

    def perform_database_search(self, search_term):
        """Perform search using database with pagination"""
        start_time = time.time()
        
        # Get just the current page from database
        offset = self.current_page * RESULTS_PER_PAGE
        print(f"Performing database search with term: {search_term}, offset: {offset}")  # Debugging log
        results = self.db_manager.search(search_term, offset, RESULTS_PER_PAGE)
        
        # Convert to dict format for consistency
        dict_results = []
        for row in results:
            dict_results.append({
                "phone": row[0],
                "name": row[1],
                "profile": row[2],
                "job": row[3],
                "study": row[4],
                "username": row[5],
                "gender": row[6],
                "location": row[7]
            })
        
        search_time = time.time() - start_time
        print(f"Search completed in {search_time:.2f}s with {len(dict_results)} results.")  # Debugging log
        return dict_results, search_time, len(dict_results)

    def handle_search_result(self, future):
        """Handle search results and update UI"""
        try:
            results, search_time, result_count = future.result()
            print(f"Handling search results: {result_count} results found.")  # Debugging log
            self.filtered_data = results
            
            # Update UI in main thread
            self.root.after(0, lambda: self.display_results(search_time, result_count))
            
        except Exception as ex:  # Fix NameError by using 'ex' instead of 'e'
            print(f"Error handling search results: {ex}")  # Debugging log
            self.root.after(0, lambda ex=ex: self.progress_label.configure(text=f"Search error: {ex}"))
        finally:
            self.search_active = False

    def display_results(self, search_time=0, result_count=0):
        """Display results with efficient rendering"""
        # Clear previous results
        for widget in self.results_container.winfo_children():
            widget.destroy()
        
        if not self.filtered_data or result_count == 0:
            no_results = ctk.CTkFrame(self.results_container, fg_color=("gray80", "gray30"),
                                     corner_radius=15)
            no_results.pack(fill="x", pady=30, padx=20)
            
            ctk.CTkLabel(
                no_results,
                text="🔍 No Results Found",
                font=ctk.CTkFont("Segoe UI", 20, weight="bold"),
                text_color=("gray40", "gray60")
            ).pack(pady=30)
            
            self.update_navigation()
            return
        
        # Display cards
        for record in self.filtered_data:
            card = ModernCard(self.results_container, record)
            card.pack(fill="x", pady=12, padx=15)
        
        # Update status with performance info
        total_pages = (self.total_records + RESULTS_PER_PAGE - 1) // RESULTS_PER_PAGE
        
        search_info = f"⚡ Showing {len(self.filtered_data)} results"
        if search_time > 0:
            search_info += f" in {search_time*1000:.1f}ms"
        search_info += f" - Page {self.current_page + 1} of {total_pages}"
        
        self.status_label.configure(text=search_info)
        self.update_navigation()

    def update_navigation(self):
        """Update navigation buttons"""
        total_pages = (self.total_records + RESULTS_PER_PAGE - 1) // RESULTS_PER_PAGE
        
        self.prev_button.configure(state="normal" if self.current_page > 0 else "disabled")
        self.next_button.configure(state="normal" if self.current_page < total_pages - 1 else "disabled")
        
        if total_pages > 0:
            self.page_label.configure(text=f"Page {self.current_page + 1} of {total_pages}")
        else:
            self.page_label.configure(text="No Pages")

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.instant_search()

    def next_page(self):
        total_pages = (self.total_records + RESULTS_PER_PAGE - 1) // RESULTS_PER_PAGE
        if self.current_page < total_pages - 1:
            self.current_page += 1
            self.instant_search()
            
    def clear_search(self):
        """Clear search results and reset UI"""
        self.search_var.set("")
        self.filtered_data = []
        self.current_page = 0
        self.last_search_term = ""
        
        # Clear results display
        for widget in self.results_container.winfo_children():
            widget.destroy()
            
        # Reset status
        self.status_label.configure(text="Ready for efficient search...")
        self.page_label.configure(text="Page 1")
        self.prev_button.configure(state="disabled")
        self.next_button.configure(state="disabled")
        
        # Show initial status
        self.progress_label.configure(text=f"⚡ Database ready with {self.total_records:,} records")

# Main application entry point
if __name__ == "__main__":
    # Check for display environment (for headless environments)
    headless = os.environ.get("HEADLESS") == "1"
    if not headless and os.name != "nt" and not os.environ.get("DISPLAY"):
        print("Error: No display found. Please run this application in an environment with a graphical display (X11).")
        exit(1)
    if not headless:
        root = ctk.CTk()
        app = FBSearchApp(root)
        root.mainloop()
    else:
        print("Running in headless mode. GUI will not be started.")