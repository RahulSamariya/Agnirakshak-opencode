"""Filter Census to AMC-only ward records."""
import pandas as pd

df = pd.read_excel("data/raw/census/DDW_PCA2407_2011_MDDS with UI (1).xlsx")
ward = df[(df["District"] == 474) & (df["Level"] == "WARD")]

# Check what town names are in ward records
print("Town names in ward records:")
town_names = ward["Name"].str.extract(r"^(.+?)\s*WARD", expand=False).unique()
for name in sorted(town_names):
    count = len(ward[ward["Name"].str.startswith(name)])
    print(f"  {name}: {count} wards")

# Filter to AMC (Ahmedabad Municipal Corporation)
# AMC wards typically have "Ahmedabad" or "Amdavad" in the name
amc_mask = ward["Name"].str.contains(
    "Ahmedabad|Amdavad|Ahmadabad", case=False, na=False
)
amc_wards = ward[amc_mask].copy()
print(f"\nAMC wards: {len(amc_wards)}")
print(f"AMC ward IDs: {sorted(amc_wards['Ward'].unique())}")
print(f"AMC ward count: {amc_wards['Ward'].nunique()}")
print()
print(amc_wards[["Ward", "Name", "TOT_P", "TOT_M", "TOT_F"]].head(10).to_string())
print()
# Show all
print(amc_wards[["Ward", "Name", "TOT_P"]].to_string())
