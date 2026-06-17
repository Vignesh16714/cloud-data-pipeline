import boto3
import sqlite3
import csv
import os
import logging
import time
from datetime import datetime

# --- CloudWatch Logging Setup ---
LOG_GROUP = "/ai-pipeline/vicky-2026"
LOG_STREAM = f"pipeline-run-{datetime.now().strftime('%Y-%m-%d')}"

cw_client = boto3.client('logs', region_name='us-east-1')

def create_log_group_and_stream():
    # Create log group (ignore if exists)
    try:
        cw_client.create_log_group(logGroupName=LOG_GROUP)
        print(f"Created log group: {LOG_GROUP}")
    except cw_client.exceptions.ResourceAlreadyExistsException:
        pass

    # Create log stream (ignore if exists)
    try:
        cw_client.create_log_stream(logGroupName=LOG_GROUP, logStreamName=LOG_STREAM)
        print(f"Created log stream: {LOG_STREAM}")
    except cw_client.exceptions.ResourceAlreadyExistsException:
        pass

def send_log(message):
    timestamp = int(round(time.time() * 1000))
    print(f"[LOG] {message}")
    try:
        cw_client.put_log_events(
            logGroupName=LOG_GROUP,
            logStreamName=LOG_STREAM,
            logEvents=[{"timestamp": timestamp, "message": message}]
        )
    except Exception as e:
        print(f"CloudWatch log error: {e}")

# --- S3 Setup ---
s3 = boto3.client('s3', region_name='us-east-1')
BUCKET = 'ai-pipeline-vicky-2026'
CSV_FILE = 'data/sample_data.csv'
S3_KEY = 'uploads/sample_data.csv'

# --- SQLite Setup ---
DB_FILE = 'pipeline.db'

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS pipeline_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT,
                    row_count INTEGER,
                    status TEXT,
                    timestamp TEXT
                )''')
    conn.commit()
    return conn

def run_pipeline():
    create_log_group_and_stream()
    send_log("Pipeline started")

    # Upload CSV to S3
    try:
        s3.upload_file(CSV_FILE, BUCKET, S3_KEY)
        send_log(f"Uploaded {CSV_FILE} to s3://{BUCKET}/{S3_KEY}")
    except Exception as e:
        send_log(f"S3 upload failed: {e}")
        return

    # Count rows
    with open(CSV_FILE, 'r') as f:
        row_count = sum(1 for _ in csv.reader(f)) - 1
    send_log(f"CSV row count: {row_count}")

    # Save to SQLite
    conn = init_db()
    c = conn.cursor()
    c.execute("INSERT INTO pipeline_runs (filename, row_count, status, timestamp) VALUES (?, ?, ?, ?)",
              (CSV_FILE, row_count, 'success', datetime.now().isoformat()))
    conn.commit()
    conn.close()
    send_log("Pipeline run saved to database")
    send_log("Pipeline completed successfully ✅")

if __name__ == '__main__':
    run_pipeline()