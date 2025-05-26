# Odisha RERA Projects Scraper 🏗️

This is a Python-based web scraper that extracts project data from the [Odisha RERA Projects Portal](https://rera.odisha.gov.in/projects) using Selenium. The scraper captures basic project information and detailed promoter details (like GST number and office address) for the **first 6 projects** listed.

---

## 📌 Features

- Scrapes:
  - Project Name
  - Promoter Name
  - RERA Registration Number
  - Project Address
  - Project Type
  - Start and Possession Dates
  - Number of Units
  - GST Number (from promoter details)
  - Registered Office Address (from promoter details)
- Uses Selenium for dynamic content rendering and interaction
- Handles popups and page navigation
- Headless mode available
- Saves data to `orera_projects.json` file

---

## 📦 Requirements

- Python 3.7+
- Google Chrome installed
- ChromeDriver in PATH (matching your Chrome version)

### Python Packages

Install dependencies via pip:
```bash
pip install selenium pandas
```

## 🚀 Getting Started
Clone the repo:
```bash
git clone https://github.com/yourusername/orera-rera-scraper.git
cd orera-rera-scraper
```
Make sure chromedriver is available in your system PATH.

Run the scraper:
```bash
python scraper.py
```

## 🧠 How It Works
- Navigates to the Odisha RERA projects page.
- Waits for project cards to load.
- Iterates over the first 6 project cards:
  - Extracts summary info
  - Clicks “View Details”
  - Switches to Promoter Details tab
  - Extracts GST No. and office address
  - Goes back and continues
- Handles popups after back navigation.
- Saves extracted data to orera_projects.json.

## 📂 Output Format
The data is saved as a list of dictionaries in orera_projects.json. Example:
```bash
[
  {
    "Project Name": "Dream Homes",
    "Promoter Name": "ABC Builders",
    "Rera Regd. No": "ORERA123456",
    "Project Address": "Bhubaneswar, Odisha",
    "Project Type": "Residential",
    "Started From": "01-Jan-2022",
    "Possession by": "31-Dec-2025",
    "Units": "120",
    "GST No.": "21ABCDE1234F1Z5",
    "Address of the Promoter": "Plot No 123, Jaydev Vihar, Bhubaneswar"
  }
]
```

## 🛠️ Troubleshooting

- WebDriverException / Version mismatch:
Ensure your ChromeDriver matches your installed Chrome version. Download here: https://chromedriver.chromium.org/downloads
- Timeouts:
The site may be slow. Increase WebDriverWait time if needed.
- No popup detected errors:
These are safe to ignore — the scraper gracefully handles both cases.

