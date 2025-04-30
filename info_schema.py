#!/usr/bin/env python3
"""
BigQuery Schema to Parquet Converter
This script connects to BigQuery, retrieves schema information from the
INFORMATION_SCHEMA tables, and saves the results as a parquet file locally.
"""

import os
import argparse
from google.cloud import bigquery
from google.oauth2 import service_account
from datetime import datetime
import yaml


def setup_args():
    """Set up command-line arguments"""
    parser = argparse.ArgumentParser(description="Convert BigQuery schema information to parquet")
    parser.add_argument("--project", required=True, help="Google Cloud Project ID")
    parser.add_argument("--region", default = "region-asia-south1", help="Google Cloud Region")
    parser.add_argument("--dataset", required=True, help="BigQuery dataset to extract schema from")
    parser.add_argument("--schema_type", default="TABLES", choices=["TABLES", "COLUMNS", "VIEWS", "ROUTINES"],
                        help="INFORMATION_SCHEMA view to query")
    parser.add_argument("--output_dir", default="./output", help="Directory to save the parquet file")
    parser.add_argument("--credentials", default=None, help="Path to Google Cloud service account JSON key file")
    return parser.parse_args()


def setup_client(args):
    """Set up BigQuery client with credentials"""
    if args.credentials:
        credentials = service_account.Credentials.from_service_account_file(
            args.credentials,
            scopes=["https://www.googleapis.com/auth/bigquery"]
        )
        client = bigquery.Client(project=args.project, credentials=credentials)
    else:
        client = bigquery.Client(project=args.project)
    return client

def load_queries(filepath="queries.yaml"):
    with open(filepath, 'r') as file:
        return yaml.safe_load(file)

def func(client, query):
    return client.query(query).to_dataframe()

def save_to_parquet(df, output_dir, dataset_id, name):
    """Save the dataframe to a parquet file"""
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Generate filename with timestamp
    now = datetime.now()
    timestamp =  now.strftime("%Y%m%d_%H%M%S")
    filename = f"{dataset_id}_{timestamp}_{name}.parquet"
    filepath = os.path.join(output_dir, filename)

    # Save dataframe to parquet
    df.to_parquet(filepath, index=False)
    return filepath


def main():
    """Main execution function"""
    args = setup_args()
    client = setup_client(args)

    print(f"Fetching {args.schema_type} schema information from {args.project}.{args.dataset}...")
    queries = load_queries("queries.yaml")
    for name, query in queries.items():
        print(name)
        try:
            # Query the information schema
            region = args.region
            dataset = args.dataset
            project_id = args.project
            query = query.format(region=region,dataset=dataset,project_id=project_id)
            # print(query)
            df = func(client,query)
            filepath = save_to_parquet(df, args.output_dir, args.dataset, name)

            print(f"Successfully saved {len(df)} rows of schema information to:")
            print(filepath)
            print(f"File size: {os.path.getsize(filepath) / (1024 * 1024):.2f} MB")

        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()