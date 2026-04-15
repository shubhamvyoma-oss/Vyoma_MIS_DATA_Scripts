import os
import requests
import csv
from datetime import datetime, timezone, timedelta

#  CONFIGURATION 

API_KEY  = "05a3fd758f3f9cd1315a362d34b18503"  #  Edmingle API key (rotates every 30 days)
ORG_ID   = "683"                                #  Edmingle Organization ID

# Output file settings
FILE_NAME  = "batches_data.csv"  # Name of the output CSV file

OUTPUT_DIR = r"C:\Users\asust\OneDrive\Desktop\vyoma\MasterBatch_Full_Load"  # Folder where CSV will be saved

# Full path — do not change this line unless you want to change the output file name or location
OUTPUT_FILE = os.path.join(OUTPUT_DIR, FILE_NAME)  # Full path — do not change this line


BASE_URL   = "https://vyoma-api.edmingle.com/nuSource/api/v1/short/masterbatch"
PER_PAGE   = 100
IST        = timezone(timedelta(hours=5, minutes=30))
STATUS_MAP = {0: "Active", 1: "Archived", 3: "Completed"}

def to_ist(ts):
    if not ts:
        return ""
    return datetime.fromtimestamp(int(ts), tz=IST).strftime("%d-%m-%Y %I:%M %p IST")

def fetch(status, label):
    rows, page = [], 1
    headers = {"apikey": API_KEY, "ORGID": ORG_ID}

    while True:
        resp = requests.get(BASE_URL, headers=headers, params={
            "page": page, "per_page": PER_PAGE,
            "organization_id": ORG_ID, "status": status
        }, timeout=30).json()

        courses    = resp.get("courses", [])
        total_rows = resp.get("page_context", {}).get("total_rows", 0)

        if page == 1:
            print(f"  {label}: {total_rows} total")
        if not courses:
            break

        for c in courses:
            for b in (c.get("batch") or []):
                rows.append({
                    "bundle_id":            c.get("bundle_id"),
                    "bundle_name":          c.get("bundle_name"),
                    "batch_id":             b.get("class_id"),  # class_id is batch_id
                    "batch_name":           b.get("class_name"),# class_name is batch_name
                    "batch_status":         STATUS_MAP.get(status),
                    "start_date":           b.get("start_date"),
                    "end_date":             b.get("end_date"),
                    "start_date_converted": to_ist(b.get("start_date")),# convert to IST and readable format
                    "end_date_converted":   to_ist(b.get("end_date")), # convert to IST and readable format
                    "tutor_id":             b.get("tutor_id"),
                    "tutor_name":           b.get("tutor_name"),
                    "admitted_students":    b.get("admitted_students"),
                })

        print(f"  {label}: page {page} → {len(courses)} courses (total so far: {len(rows)})")

        if len(rows) >= total_rows:
            break
        page += 1

    print(f"  {label} done: {len(rows)} rows\n")
    return rows

def save(rows):
    fields = [
        "bundle_id", "bundle_name",
        "batch_id",  "batch_name",          "batch_status",
        "start_date","start_date_converted",
        "end_date",  "end_date_converted",
        "tutor_id",  "tutor_name",           "admitted_students",
    ]
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print(f" {len(rows)} rows saved to:\n    {OUTPUT_FILE}")

# ── Run ──
if __name__ == "__main__":
    print("Fetching batches...\n")
    all_rows = []
    for status, label in [(0, "Active"), (1, "Archived"), (3, "Completed")]:
        all_rows.extend(fetch(status, label))
    print(f"Total: {len(all_rows)} rows")
    save(all_rows)