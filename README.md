# Commands to run py files :-

## Pre-requisite

1. Service account credentials json


## Setup venv

```
python -m venv venv
pip install -r requirements.txt
```

## Run the code

Before running need to do the following:

Replace <path_to_credentials_json> with your path
Replace <project_id> with your project_id
Replace <dataset> with your dataset name

```
python info_schema.py --project <project_id> --dataset <dataset> --credentials <path_to_credentials_json>
python bq_logs.py --project_id <project_id>  --credentials <path_to_credentials_json>
```

## Output

The output parquet file will be store in output directory and bq_logs_parquet directory
