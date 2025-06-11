# FB IntelScan v1.0 - Dark OSINT File Scanner

A powerful Python intelligence tool that searches through folders of large text files containing leaked or compiled Facebook user data, displaying results in a professional target card style GUI.

## 🎯 Features

- **🔎 Search Bar**: Input any query (ID, phone, name, email, location, etc.)
- **🎛️ Search Button**: Starts the scanning process through all .txt files in the directory
- **🛑 Stop Button**: Immediately halts the ongoing scan
- **📦 Results Container**: Hidden by default, becomes visible when results are found
- **📂 Directory Path**: Hardcoded to `/home/cts/Desktop/FB-data`
- **⚡ Streaming File Reading**: Handles extremely large files efficiently without freezing the GUI
- **🖤 Dark Intelligence UI**: Modern cyber-intel design with neon green highlights

## 📋 Data Format

The application expects Facebook data in CSV format with the following structure:
```
ID,phone,first_name,last_name,gender,profile_url,full_name,,,email,,,
```

Example:
```
100024297620720,+9647807440886,Ahmed,Daam,male,https://www.facebook.com/100024297620720,Ahmed Daam,,,100024297620720@facebook.com,,,
```

## 🧠 Data Extracted per Match

- Facebook ID
- Phone Number
- Full Name
- Facebook Profile URL
- Gender
- Email Address
- Location (if available)

## 🖥️ Interface Design

- **🖤 Dark intelligence-style UI** using CustomTkinter
- **🎯 Target Card** for each result with:
  - Bold header with name and Facebook ID
  - Highlighted phone and profile link
  - Clean layout for gender, email, and location
- **🔒 Stealth Mode**: Result box is hidden until at least one match is found
- **📊 Progress Indicator**: Shows scanning status during search

## 🚀 Installation

1. **Install Python 3.7+**

2. **Install required dependencies:**
   ```bash
   pip install customtkinter
   ```

3. **Create the data directory:**
   ```bash
   mkdir -p /home/cts/Desktop/FB-data
   ```

4. **Place your .txt data files** in the `/home/cts/Desktop/FB-data` directory

## 📖 Usage

### GUI Version (Full Application)
```bash
python fb_intelscan.py
```

**Note**: Requires a display environment (X11). In headless environments (like Docker containers), use the test version below.

### Command Line Test Version
```bash
python test_fb_intelscan.py
```

This version provides the same search functionality without the GUI, perfect for testing or headless environments.

## 🔍 Search Examples

The application supports various search queries:

- **Name search**: `Ahmed`, `John Smith`
- **Phone search**: `+964`, `+44`, `+1234567890`
- **Country code search**: `+44` (finds all UK numbers)
- **Email search**: `@facebook.com`, `john.smith@`
- **Gender search**: `female`, `male`
- **ID search**: `100024297620720`
- **Profile URL search**: `facebook.com`

## 🎯 Sample Output

```
🎯 INTELLIGENCE RESULTS (1 targets found)

📊 TARGET #1
----------------------------------------
👤 Name: Ahmed Daam
🆔 Facebook ID: 100024297620720
📱 Phone: +9647807440886
🔗 Profile: https://www.facebook.com/100024297620720
⚧ Gender: Male
📧 Email: 100024297620720@facebook.com
📂 Source: sample_fb_data.txt (line 1)
----------------------------------------
```

## 🛡️ Features

- **High Performance**: No lag when loading thousands of lines
- **Real-time Results**: Updates display as matches are found
- **Multi-file Support**: Scans all .txt files in the directory
- **Streaming Processing**: Handles extremely large files without memory issues
- **Instant Stop**: Can halt scanning immediately
- **Case Insensitive**: Searches work regardless of case
- **Error Handling**: Gracefully handles corrupted or malformed data

## 📁 File Structure

```
/app/
├── fb_intelscan.py          # Main GUI application
├── test_fb_intelscan.py     # Command-line test version
└── README.md                # This file

/home/cts/Desktop/FB-data/   # Data directory (create this)
├── sample_fb_data.txt       # Your data files go here
├── additional_fb_data.txt   # Multiple files supported
└── ...                      # Add more .txt files as needed
```

## 🔒 Security Notes

- This tool is designed for legitimate intelligence and research purposes
- Ensure you have proper authorization to analyze any data
- The application processes data locally - no external connections
- All searches are performed offline

## 🚨 System Requirements

- Python 3.7+
- CustomTkinter library
- Sufficient RAM for large file processing
- Display environment (for GUI version)

## 🔧 Troubleshooting

**GUI won't start in headless environment:**
- Use the command-line test version: `python test_fb_intelscan.py`

**No files found:**
- Ensure .txt files are in `/home/cts/Desktop/FB-data`
- Check file permissions

**Memory issues with large files:**
- The application uses streaming processing to handle large files efficiently
- If issues persist, consider splitting very large files

## 🏆 Performance

- Handles files with millions of lines
- Real-time search results
- Instant stop functionality
- Memory-efficient streaming processing
- Sub-second search times on typical datasets

---

**FB IntelScan v1.0** - Professional OSINT tool for Facebook data analysis.