# Edmingle Batch Data Fetcher — `batches_data.py`

---

## What This Script Does

What This Script Does

* Connects to the Vyoma API using API key and organization ID
* Fetches batch data for:

  * Active batches
  * Archived batches
  * Completed batches
* Handles API pagination to retrieve all available records
* Converts Unix timestamps into **human-readable IST date format**
* Combines all results into a single dataset
* Uses `utf-8-sig` encoding so special characters (e.g. `–`, `'`) render correctly in Excel

* Saves the final data into a CSV file
---

## Output

* **File:** `batches_data.csv`
* **Location:**
  `C:\your_path\Desktop\yourfolder\`

---

## Columns in the CSV

| Column                 | Description                                                        |
| ---------------------- | ------------------------------------------------------------------ |
| `bundle_id`            | Unique ID of the course (called "bundle" in Edmingle API)          |
| `bundle_name`          | Name of the course                                                 |
| `batch_id`             | Unique ID of the batch (called "class_id" internally in the API)   |
| `batch_name`           | Name of the batch (called "class_name" internally in the API)      |
| `batch_status`         | Active / Archived / Completed                                      |
| `start_date`           | Batch start date as raw Unix timestamp                             |
| `start_date_converted` | Batch start date converted to IST (e.g. `23-01-2014 05:30 AM IST`) |
| `end_date`             | Batch end date as raw Unix timestamp                               |
| `end_date_converted`   | Batch end date converted to IST                                    |
| `tutor_id`             | Unique ID of the assigned tutor                                    |
| `tutor_name`           | Name of the assigned tutor                                         |
| `admitted_students`    | Number of students enrolled in the batch                           |

---

## Configuration

All settings are defined at the top of the script:

```python id="cfg1"
API_KEY    = "your_api_key"        # Edmingle API key — rotates every 30 days
ORG_ID     = "683"                 # Organization ID — constant

FILE_NAME  = "batches_data.csv"    # Output file name
OUTPUT_DIR = r"C:\your\folder"     # Output directory

OUTPUT_FILE = os.path.join(OUTPUT_DIR, FILE_NAME)  # Do not modify
```

> ⚠️ If you receive a `401 Unauthorized` error, regenerate your API key and update it here.

---

## Functions

### `to_ist(ts)`

Converts a Unix timestamp into a human-readable IST format.

* **Input:** Unix timestamp (e.g. `1390435200`) or `None`
* **Output:** Formatted string (`DD-MM-YYYY HH:MM AM/PM IST`) or empty string

---

### `fetch(status, label)`

Fetches all batches for a given status using API pagination.

**How it works:**

* Sends request to:
  `GET /nuSource/api/v1/short/masterbatch`

* Uses parameters:
  * `status`
  * `page`
  * `per_page`
  * `organization_id`
  
* Reads `total_rows` from `page_context` to control pagination
* Extracts nested structure:
  `course → batch[]`
* Flattens data into one row per batch

**Returns:**
A list of dictionaries (each representing one batch)

---

### `save(rows)`

Writes all collected data into a CSV file.

* Uses `csv.DictWriter`
* Maintains consistent column order
* Uses `utf-8-sig` encoding so special characters (e.g. `–`, `'`) render correctly in Excel

---

## How Pagination Works

The API returns data in pages (100 records per request).

The script:

1. Fetches page 1
2. Reads `total_rows` from response
3. Continues fetching subsequent pages
4. Stops when `len(rows) >= total_rows`

> ⚠️ The `has_more_page` flag is unreliable and intentionally not used.

---

## How Status Fetching Works

The API does not reliably return all statuses in one call.

The script fetches each status separately:

| API Call | Status Code | Label     |
| -------- | ----------- | --------- |
| Call 1   | `0`         | Active    |
| Call 2   | `1`         | Archived  |
| Call 3   | `3`         | Completed |

---

## API Response Structure

The API returns nested data, which is flattened by the script:

```id="cfg2"
courses[]
  ├── bundle_id        ← course level
  ├── bundle_name      ← course level
  └── batch[]          ← list of batches
        ├── class_id   → batch_id
        ├── class_name → batch_name
        ├── start_date
        ├── end_date
        ├── tutor_id
        ├── tutor_name
        └── admitted_students
```

Each batch becomes a **single row in the CSV output**.

---

## Libraries Used

* `requests` → API communication
* `csv` → CSV writing
* `datetime` → timestamp conversion
* `os` → file path handling

---

## Things Handled in the Script

| Issue                  | Handling                                     |
| ---------------------- | -------------------------------------------- |
| API key management     | Centralized in config section                |
| Output path management | Controlled via `OUTPUT_DIR` and `FILE_NAME`  |
| Null timestamps        | Handled in `to_ist()`                        |
| Excel encoding issues  | Uses `utf-8-sig`                             |
| Pagination reliability | Uses `total_rows` instead of `has_more_page` |
| Nested API structure   | Flattened into tabular format                |
| Status readability     | Uses `STATUS_MAP`                            |
| File lock issues       | Requires closing CSV before re-run           |

---

## How to Run

```bash id="run1"
pip install requests
python fetch_batches.py
```

---

## Requirements

* Python 3.7+
* `requests` library
* Valid Edmingle API key
* Organization ID

---

## Summary

This script provides a **complete and reliable batch data extraction solution**:

* Handles API pagination correctly
* Converts timestamps into readable format
* Flattens complex API structure
* Produces clean, analysis-ready CSV output
