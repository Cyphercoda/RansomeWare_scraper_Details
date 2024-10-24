# RansomeWare_scraper_Details
Automated Ransomware Data Collection Tool
 Purpose & Functionality
- Automates data collection from ransomlook.io and ZoomInfo
- Collects company details, websites, and additional information
- Date-based filtering for targeted data collection
- Handles captchas automatically
 
        2. Key Features
- Clean data extraction with automated name cleaning
- Multi-source validation (ransomlook.io + ZoomInfo)
- Detailed CSV output with multiple data points:
  * Original company names
  * Cleaned company names
  * Official company names (from ZoomInfo)
  * Company websites
  * Company details/descriptions
  * Incident dates
  * Associated groups
 
        3. Technical Implementation
 
- Built with Python using Selenium and undetected-chromedriver
- Human-like behavior simulation to avoid detection
- Robust error handling and retry mechanisms
- Real-time progress monitoring with colored terminal output
 
         4. Future Improvements
 
 - Implement multi-threading for faster processing
- Add additional data sources
- Create a simple web interface
 
Usage: python ransomeware_collector.py --start-date 2024-10-19 --end-date 2024-10-23 --output-csv results.csv
