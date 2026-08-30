"""Quick Census inspection."""
import pandas as pd

df = pd.read_excel("data/raw/census/DDW_PCA2407_2011_MDDS with UI (1).xlsx")
ward = df[(df["District"] == 474) & (df["Level"] == "WARD")]
print(f"WARD records: {len(ward)}")
print(f"TRU values: {ward['TRU'].unique()}")
print(f"Ward IDs: {sorted(ward['Ward'].unique())}")
print(f"Ward count: {ward['Ward'].nunique()}")
print()
print(ward[["Ward", "Name", "TRU", "TOT_P", "TOT_M", "TOT_F"]].head(15).to_string())
print()
# Check if there's a ward-level Total row somewhere
total_ward = ward[ward["Name"].str.contains("Total", case=False, na=False)]
print(f"Total-named wards: {len(total_ward)}")
# Check EB column
print(f"EB values: {ward['EB'].unique()}")
