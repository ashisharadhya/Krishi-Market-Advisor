# Krishi Market Advisor 🌾

> **"Where and when should I sell my crop to get the best price?"**

A production-ready data collection pipeline for Karnataka farmers, built with Python.  
Fetches daily mandi (market) price data from the official Indian Government data portal (or direct Agmarknet fallback) and saves it as clean, analysis-ready CSV files.

---

## 📋 Project Overview

**Krishi Market Advisor** is a multi-phase AI project that will ultimately help farmers in Karnataka make better crop-selling decisions. It integrates:

- 📊 Government mandi price data (Agmarknet via data.gov.in and direct API fallback)
- 🤖 AI-powered price recommendations *(future phase)*
- 🗣️ Kannada language explanations *(future phase)*
- 📈 Streamlit dashboard *(future phase)*

---

## 🎯 Phase 1 Objective

**Phase 1 is data collection only.**

This phase implements a robust pipeline that:

1. Connects to the **data.gov.in OGD API** (primary) or **Agmarknet 2.0 REST API** (fallback).
2. Downloads **daily Karnataka mandi price data** (all commodities, all markets).
3. Filters only **Karnataka** records.
4. **Validates** the downloaded data structure.
5. Removes **duplicate rows**.
6. Handles **missing values** gracefully.
7. Saves the cleaned data as a **dated CSV file** (e.g., `data/2026-07-16.csv`).
8. **Avoids overwriting:** If today's CSV file already exists, it skips fetching and prints `Today's data already exists.` to prevent redundant resource consumption.
9. Prints a **formatted summary** in the terminal.

> **No AI. No LLM. No Streamlit. No recommendations.**  
> Just clean, reliable, production-grade data collection.

---

## 📁 Folder Structure

```
krishi-market-advisor/
│
├── data/                         ← Daily CSV files saved here (automatically created)
│   └── 2026-07-16.csv           ← Example: one file per day
│
├── src/                          ← All source code modules
│   ├── __init__.py              ← Makes src/ a Python package
│   ├── config.py                ← All settings (API URL, paths, columns)
│   ├── fetch_mandi_prices.py    ← Core pipeline orchestrator
│   ├── agmarknet_scraper.py     ← Fallback scraper (Agmarknet 2.0 API)
│   └── utils.py                 ← Helpers (logging, directories, summary)
│
├── logs/                         ← Application log files (automatically created)
│   ├── krishi_pipeline.log       ← Core pipeline logs
│   └── scheduler.log            ← Windows Task Scheduler execution logs
│
├── .env                          ← Your API key (NOT committed to git)
├── .env.example                  ← Template — copy this to create .env
├── .gitignore                    ← Git exclusion rules
├── main.py                       ← 🚀 Entry point — run this!
├── run_pipeline.bat              ← 🕒 Windows automation batch script
├── requirements.txt              ← Python package dependencies
└── README.md                     ← This file
```

---

## 🔑 Getting Your Free API Key

The pipeline uses the **Open Government Data (OGD) Platform India** API.  
The API is **completely free** but requires registration.

**Step-by-step:**

1. Go to **[https://data.gov.in/user/register](https://data.gov.in/user/register)**
2. Create a free account with your email address
3. Verify your email
4. Log in → click your **Profile** (top-right)
5. Find the **"API Key"** section → copy your key
6. Follow the **Installation** steps below to add it to your `.env` file

---

## ⚙️ Installation

### 1. Navigate to the project folder

```bash
cd krishi-market-advisor
```

### 2. (Recommended) Create a virtual environment

```bash
# Create the virtual environment
python -m venv venv

# Activate it — Windows PowerShell:
venv\Scripts\Activate.ps1

# Activate it — Windows Command Prompt:
venv\Scripts\activate.bat

# Activate it — Mac/Linux:
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up your API key

```bash
# Windows PowerShell:
Copy-Item .env.example .env

# Windows Command Prompt:
copy .env.example .env

# Mac/Linux:
cp .env.example .env
```

Now open `.env` in any text editor and replace `your_api_key_here`:

```env
DATA_GOV_IN_API_KEY=579b464db66ec23bdd000001your_actual_key_here
```

---

## 📦 Required Packages

| Package | Version | Purpose |
|---------|---------|---------|
| `requests` | ≥ 2.31.0 | HTTP calls to the APIs |
| `pandas` | ≥ 2.0.0 | DataFrame operations (filter, clean, save CSV) |
| `python-dotenv` | ≥ 1.0.0 | Loads API key from the `.env` file |
| `urllib3` | ≥ 2.0.0 | Retry logic for network resilience |
| `lxml` | ≥ 4.9.0 | HTML parser used by fallback mechanisms |

All installed automatically via `pip install -r requirements.txt`.

---

## 🚀 How to Run

```bash
python main.py
```

That's it. The pipeline will handle everything automatically. If today's data is already downloaded, it will output:
`Today's data already exists.`

---

## 🕒 Unattended Automation on Windows

To continuously collect historical data, you can set up the pipeline to run automatically every day at **6:00 PM** using **Windows Task Scheduler**.

We have provided a helper file `run_pipeline.bat` that automatically activates your Python virtual environment and schedules the pipeline execution without any terminal windows popping up.

### Step-by-Step Task Scheduler Configuration:

1. Press `Win + R`, type **`taskschd.msc`**, and press `Enter` to open the **Windows Task Scheduler**.
2. On the right-side **Actions** panel, click **Create Basic Task...**.
3. **Name the Task:**
   - **Name:** `Krishi Market Advisor Price Collector`
   - **Description:** `Daily download of Karnataka mandi price data.`
   - Click **Next**.
4. **Trigger:**
   - Select **Daily**.
   - Click **Next**.
5. **Daily Settings:**
   - Set the **Start Time** to **6:00:00 PM** (18:00).
   - Set **Recur every:** `1` days.
   - Click **Next**.
6. **Action:**
   - Select **Start a program**.
   - Click **Next**.
7. **Start a Program Settings:**
   - **Program/script:** Click **Browse...** and select the **`run_pipeline.bat`** file located inside the project directory:
     `C:\Users\yukti\Desktop\krishi\krishi-market-advisor\run_pipeline.bat`
   - **Start in (optional):** Paste the absolute path to your project root folder:
     `C:\Users\yukti\Desktop\krishi\krishi-market-advisor`
   - Click **Next**.
8. **Finish:**
   - Review your settings.
   - Check the box **"Open the Properties dialog for this task when I click Finish"** and click **Finish**.
9. **Configure Properties (Crucial for Silent & Resilient Execution):**
   - In the **General** tab, select **"Run whether user is logged on or not"** (this ensures the task runs in the background even if you're not actively logged in).
   - Check the **"Run with highest privileges"** box to ensure there are no permission blocks when creating directories.
   - In the **Conditions** tab, uncheck **"Start the task only if the computer is on AC power"** (this ensures it runs on laptops even when unplugged).
   - In the **Settings** tab:
     - Check **"Run task as soon as possible after a scheduled start is missed"** (ensures that if your PC was turned off at 6:00 PM, the task runs immediately when you turn it on).
     - Under "If the task fails, restart every:", set it to `15 minutes` and attempt to restart up to `3 times`.
   - Click **OK**. You will be prompted to enter your Windows password to authorize background execution.

Now the script will run silently in the background every day at 6:00 PM. You can verify its status and output logs inside `logs/scheduler.log` and `logs/krishi_pipeline.log`.

---

## 📺 Expected Output

When the pipeline runs successfully and downloads new data, you will see:

```
------------------------------------
  Karnataka Mandi Price Collector   
------------------------------------

  Connection Successful

  Records Downloaded  : 392
  Karnataka Records   : 392

  File Saved:
  data\2026-07-16.csv

  Completed Successfully

------------------------------------
```

If today's data was already downloaded, it will output:
```
Today's data already exists.
```

All detailed pipeline logs are appended to `logs/krishi_pipeline.log`.

---

## 📊 Output CSV Format

The saved CSV file contains one row per commodity–market–date combination:

| Column | Description | Example |
|--------|-------------|---------|
| `state` | State name | `Karnataka` |
| `market` | Market (mandi) name | `Yeshwanthpur` |
| `commodity_group` | Broad category of the crop | `Vegetables` |
| `commodity` | Crop/commodity name | `Tomato` |
| `variety` | Variety of the commodity | `Hybrid` |
| `arrivals` | Quantity of crop arriving in market | `13.8` |
| `unit_of_arrivals` | Unit of measure for arrivals | `Metric Tonnes` |
| `min_price` | Minimum price (₹/quintal) | `1200` |
| `max_price` | Maximum price (₹/quintal) | `1800` |
| `modal_price` | Most common price (₹/quintal) | `1500` |
| `unit_of_price` | Price currency / weight unit | `Rs./Quintal` |
| `arrival_date` | Date of the price record (YYYY-MM-DD) | `2026-07-16` |

---

## 🔄 Pipeline Architecture

```
main.py (entry point)
  │
  ├── [Check] Does today's CSV exist? ──(Yes)──> Stop execution & print warning
  │                                ──(No)───> Proceed
  │
  ├── [Stage 1] ensure_directories()   → Create data/ and logs/ folders
  ├── [Stage 2] fetch_all_records()    → Attempt OGD API first, fallback to Agmarknet 2.0 API on failure
  ├── [Stage 3] filter_karnataka()     → Keep only Karnataka records
  ├── [Stage 4] validate_data()        → Check structure and completeness
  ├── [Stage 5] clean_data()           → Remove duplicates, handle missing values
  ├── [Stage 6] save_data()            → Write to data/YYYY-MM-DD.csv
  └── [Always]  print_summary()        → Terminal summary box
```

---

## 🛑 Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `API key is missing!` | `.env` file not set up | Follow the API Key setup steps above |
| `401 Unauthorized` | Invalid API key | Double-check your key on data.gov.in |
| `No Karnataka records found` | Data not available today | Try again — government data has gaps |
| `Connection error` | No internet | The pipeline will log this error gracefully. Check your network connection. |
| `ModuleNotFoundError` | Dependencies not installed | Run `pip install -r requirements.txt` |
| `Today's data already exists.` | Script ran multiple times today | Normal behavior. Today's CSV is already preserved. |

---

*Built with ❤️ for Karnataka farmers.*
