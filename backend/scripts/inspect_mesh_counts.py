from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "census"
    / "mesh_block_counts_2021.xlsx"
)


excel = pd.ExcelFile(DATA_PATH)

print("Worksheets:")

for sheet in excel.sheet_names:
    print(f"  {sheet}")


print("\nQueensland sample:")

df = pd.read_excel(
    DATA_PATH,
    sheet_name="Table 3",
    header=6,
    usecols="A:F",
    nrows=10,
)

print(df.columns.tolist())

print(df.head().to_string(index=False))