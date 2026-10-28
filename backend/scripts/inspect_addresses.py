from pathlib import Path
import csv

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "addresses"
    / "property-address-locations.csv"
)


# Detect whether the CSV uses commas,
# semicolons or tabs as separators.
with DATA_PATH.open(
    "r",
    encoding="utf-8-sig",
    newline="",
) as file:
    sample = file.read(8192)

delimiter = csv.Sniffer().sniff(
    sample,
    delimiters=";,\t",
).delimiter


df = pd.read_csv(
    DATA_PATH,
    sep=delimiter,
    encoding="utf-8-sig",
    dtype=str,
)


print("Number of records:", len(df))

print("\nColumns:")
print(df.columns.tolist())

print("\nSample records:")
print(df.head(5).to_string(index=False))

print("\nAddress use types:")

if "ADDRESS USE TYPE" in df.columns:
    print(
        df["ADDRESS USE TYPE"]
        .value_counts(dropna=False)
        .head(20)
    )