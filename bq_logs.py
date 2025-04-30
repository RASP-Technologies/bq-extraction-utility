#!/usr/bin/env python3
# BigQuery Logs to Parquet Converter
# This script fetches recent BigQuery logs and converts them to Parquet files

import os
import argparse
from datetime import datetime, timedelta
from google.cloud import bigquery
from google.api_core.exceptions import GoogleAPIError
import pandas as pd
from google.oauth2 import service_account

# credentials = service_account.Credentials.from_service_account_file(
#     "cred.json"
# )

def setup_client(args):
    """Set up BigQuery client with credentials"""
    if args.credentials:
        credentials = service_account.Credentials.from_service_account_file(
            args.credentials,
            scopes=["https://www.googleapis.com/auth/bigquery"]
        )
        client = bigquery.Client(project=args.project_id, credentials=credentials)
    else:
        client = bigquery.Client(project=args.project_id)
    return client


def setup_args():
    """Set up command line arguments."""
    parser = argparse.ArgumentParser(description='Convert BigQuery logs to Parquet files')
    parser.add_argument('--project_id', required=True, help='Your GCP project ID')
    parser.add_argument("--region", default = "region-asia-south1", help="Google Cloud Region")
    parser.add_argument('--days', type=int, default=1, help='Number of days of logs to retrieve (default: 7)')
    parser.add_argument('--output_dir', default='./bq_logs_parquet', help='Directory to save Parquet files')
    parser.add_argument('--log_type', default='query',
                        choices=['query', 'job', 'resource', 'all'],
                        help='Type of logs to extract (default: query)')
    parser.add_argument("--credentials", default='/Users/kprashant/Downloads/linen-striker-454116-c9-491d0d49f463.json', help="Path to Google Cloud service account JSON key file")
    return parser.parse_args()

def get_resource_logs_sql(project_id, days, region):
    """Create SQL query to fetch BigQuery resource usage logs for the last `days`."""
    return f"""
    SELECT *
    FROM
      `{project_id}.{region}.INFORMATION_SCHEMA.JOBS_BY_PROJECT` AS a
    WHERE
      creation_time > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {days} DAY)
    """

def execute_query(client, query):
    """Execute a BigQuery query and return results as DataFrame."""
    try:
        query_job = client.query(query)
        results = query_job.result()
        return results.to_dataframe()
    except GoogleAPIError as e:
        print(f"Error executing query: {e}")
        return pd.DataFrame()


def save_to_parquet(df, output_path, file_name):
    """Save DataFrame to Parquet file."""
    os.makedirs(output_path, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    file_path = os.path.join(output_path, f"{file_name}_{timestamp}.parquet")

    df.to_parquet(file_path, engine='pyarrow', compression='snappy')
    print(f"Saved {df.shape[0]} records to {file_path}")
    return file_path


def main():
    args = setup_args()
    client = setup_client(args)

    if args.log_type == 'all':
        log_types_to_process = ['query', 'resource']
    else:
        log_types_to_process = [args.log_type]

    for log_type in log_types_to_process:
        print(f"\nFetching {log_type} logs for the past {args.days} days...")
        query = get_resource_logs_sql(args.project_id, args.days, args.region)
        df = execute_query(client, query)
        if not df.empty:
            file_path = save_to_parquet(df, args.output_dir, "bq_resource_logs")
            print(f"Resource logs saved to: {file_path}")
        else:
            print("No resource logs found or error occurred.")

if __name__ == "__main__":
    main()