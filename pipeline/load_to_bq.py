# pipeline/load_to_bq.py
import os
import sys
from google.cloud import bigquery

def load_gcs_to_bq(env: str):
    """Simple GCS to BigQuery load job."""
    
    project_id = os.environ.get("PROJECT_ID")
    bucket_name = f"{project_id}-{env}-data-bucket"
    dataset_id  = f"{env}_dataset"
    table_id    = "users"

    gcs_uri  = f"gs://{bucket_name}/input/sample.csv"
    table_ref = f"{project_id}.{dataset_id}.{table_id}"

    client = bigquery.Client(project=project_id)

    # Define schema FOR SAMPLE
    schema = [
        bigquery.SchemaField("id",         "INTEGER"),
        bigquery.SchemaField("name",       "STRING"),
        bigquery.SchemaField("age",        "INTEGER"),
        bigquery.SchemaField("city",       "STRING"),
        bigquery.SchemaField("created_at", "DATE"),
    ]

    job_config = bigquery.LoadJobConfig(
        schema=schema,
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,          # skip header
        write_disposition="WRITE_TRUNCATE",  # overwrite each run
    )

    print(f"[{env.upper()}] Loading {gcs_uri} → {table_ref}")

    load_job = client.load_table_from_uri(
        gcs_uri, table_ref, job_config=job_config
    )
    load_job.result()  # Wait for completion

    table = client.get_table(table_ref)
    print(f"[{env.upper()}] ✅ Loaded {table.num_rows} rows into {table_ref}")


if __name__ == "__main__":
    env = sys.argv[1] if len(sys.argv) > 1 else "dev"
    load_gcs_to_bq(env)