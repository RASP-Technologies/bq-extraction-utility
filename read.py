import pandas as pd

df = pd.read_parquet('output/techsteer_20250430_175903_query2.parquet', engine='pyarrow')  # or engine='fastparquet'

print(df.head())  # Show first few rows


print(df.columns.tolist())
print(len(df))
# print(df["error_result"])