from pathlib import Path
import pandas as pd
from prefect import flow, task
from prefect_gcp.cloud_storage import GcsBucket
from prefect_gcp import GcpCredentials

@task(retries=3)
def extract_from_gcs(color, year, month) -> Path:
    """Data Extract from Google Cloud Storage"""
    gcs_path = f"{color}/{color}_tripdata_{year}-{month:02}.parquet"
    gcs_block = GcsBucket.load("zoom-gcs")
    gcs_block.get_directory(from_path=gcs_path, local_path=f"/home/tomzoomcamp/homeworkzoomcamp/week3/data/")
    print(gcs_path)
    return Path(f"/home/tomzoomcamp/homeworkzoomcamp/week3/data/{gcs_path}")

@task()
def transform(path) -> pd.DataFrame:
    """Data Cleaning"""
    df = pd.read_parquet(path)
    return df

@task()
def write_bq(df) -> None:
    """Write DataFrame to BigQuery"""

    gcp_credentials_block = GcpCredentials.load("zoom-gcp-creds")

    df.to_gbq(
        destination_table="trips_data_all.rides",
        project_id="de-bootcamp123",
        credentials=gcp_credentials_block.get_credentials_from_service_account(),
        chunksize=500_000, 
        if_exists="append"
    )

@flow()
def etl_gcs_to_bq(year: int, month: int, color: str):
    path = extract_from_gcs(color, year, month)
    df = transform(path)
    print(f"rows: {len(df)}")
    write_bq(df)

@flow(log_prints=True)
def etl_parent_flow(
    months: list[int] = [2,3], year: int = 2019, color: str = "yellow"
):
    for month in months:
        etl_gcs_to_bq(year,month,color)

if __name__ == "__main__":
    months= [2,3]
    year=2019
    color="yellow"
    etl_gcs_to_bq(months, year, color)