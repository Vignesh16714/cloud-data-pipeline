import boto3
import pandas as pd
import sqlite3
import os
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

S3_BUCKET = os.getenv('S3_BUCKET')
AWS_REGION = os.getenv('AWS_REGION')

def get_db_connection():
    """Connect to local SQLite database (simulates RDS PostgreSQL)"""
    conn = sqlite3.connect('pipeline.db')
    return conn

def create_table(conn):
    """Create table if it doesn't exist"""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS pipeline_data (
            id TEXT,
            name TEXT,
            value REAL,
            category TEXT,
            processed_at TEXT,
            is_high_value INTEGER
        )
    """)
    conn.commit()

def transform_row(row):
    """AI transformation layer"""
    return {
        'id': str(row['id']),
        'name': str(row['name']).strip().title(),
        'value': float(row['value']),
        'category': str(row['category']).lower(),
        'processed_at': datetime.utcnow().isoformat(),
        'is_high_value': 1 if float(row['value']) > 100 else 0
    }

def upload_to_s3(file_path):
    """Upload CSV file to S3"""
    s3 = boto3.client('s3', region_name=AWS_REGION)
    file_name = os.path.basename(file_path)
    print(f"Uploading {file_name} to S3 bucket {S3_BUCKET}...")
    s3.upload_file(file_path, S3_BUCKET, file_name)
    print(f"✅ Uploaded successfully to s3://{S3_BUCKET}/{file_name}")
    return file_name

def process_csv(file_path):
    """Read, transform and store CSV data"""
    print(f"Processing {file_path}...")
    
    # Read CSV
    df = pd.read_csv(file_path)
    print(f"Found {len(df)} rows")
    
    # Transform each row
    transformed = [transform_row(row) for _, row in df.iterrows()]
    
    # Store in SQLite
    conn = get_db_connection()
    create_table(conn)
    
    for row in transformed:
        conn.execute("""
            INSERT INTO pipeline_data 
            (id, name, value, category, processed_at, is_high_value)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            row['id'], row['name'], row['value'],
            row['category'], row['processed_at'], row['is_high_value']
        ))
    
    conn.commit()
    print(f"✅ Stored {len(transformed)} rows in database")
    
    return transformed

def generate_report():
    """Generate summary report from database"""
    conn = get_db_connection()
    cursor = conn.execute("""
        SELECT category, COUNT(*) as count, AVG(value) as avg_value, 
               SUM(is_high_value) as high_value_count
        FROM pipeline_data 
        GROUP BY category
    """)
    
    print("\n📊 Pipeline Report:")
    print("-" * 50)
    for row in cursor.fetchall():
        print(f"Category : {row[0]}")
        print(f"Count    : {row[1]}")
        print(f"Avg Value: ${row[2]:.2f}")
        print(f"High Value Items: {row[3]}")
        print("-" * 50)
    
    conn.close()

def lambda_handler(event=None, context=None):
    """Main handler - simulates Lambda function"""
    print("🚀 Pipeline started...")
    
    # Step 1: Upload to S3
    upload_to_s3('data/sample.csv')
    
    # Step 2: Process and transform
    process_csv('data/sample.csv')
    
    # Step 3: Generate report
    generate_report()
    
    print("\n✅ Pipeline completed successfully!")
    return {
        'statusCode': 200,
        'body': json.dumps('Pipeline completed successfully!')
    }

if __name__ == "__main__":
    lambda_handler()