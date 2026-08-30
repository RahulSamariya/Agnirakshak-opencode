"""GIS profiling script for Ahmedabad wards."""
import json
import hashlib
from pathlib import Path
import geopandas as gpd

# Load the GeoJSON file
gdf = gpd.read_file('ERA5/wards_ahmedabad.geojson')

print('=== Ahmedabad Wards GIS Profile ===')
print(f'Feature count: {len(gdf)}')
print(f'Columns: {list(gdf.columns)}')
print(f'CRS: {gdf.crs}')
print(f'Geometry type: {gdf.geometry.geom_type.unique()}')

# Get bounding box
bounds = gdf.total_bounds
print(f'Bounding box: {bounds}')

# Check for invalid geometries
invalid_geom = ~gdf.geometry.is_valid
print(f'Invalid geometries: {invalid_geom.sum()}')

# Check for empty geometries
empty_geom = gdf.geometry.is_empty
print(f'Empty geometries: {empty_geom.sum()}')

# Check for duplicate IDs
if 'ward_id' in gdf.columns:
    duplicate_ids = gdf['ward_id'].duplicated().sum()
    print(f'Duplicate ward IDs: {duplicate_ids}')
elif 'id' in gdf.columns:
    duplicate_ids = gdf['id'].duplicated().sum()
    print(f'Duplicate IDs: {duplicate_ids}')

# Show first few rows
print('\nFirst 5 rows:')
print(gdf.head())

# Show column info
print('\nColumn info:')
for col in gdf.columns:
    if col != 'geometry':
        print(f'  {col}: {gdf[col].dtype}, unique={gdf[col].nunique()}, null={gdf[col].isnull().sum()}')

# Calculate source checksum
with open('ERA5/wards_ahmedabad.geojson', 'rb') as f:
    source_hash = hashlib.md5(f.read()).hexdigest()
print(f'\nSource file hash (MD5): {source_hash}')

# Save profile as JSON
profile = {
    "file": "wards_ahmedabad.geojson",
    "feature_count": len(gdf),
    "columns": list(gdf.columns),
    "crs": str(gdf.crs),
    "geometry_types": list(gdf.geometry.geom_type.unique()),
    "bounding_box": {
        "min_lon": float(bounds[0]),
        "min_lat": float(bounds[1]),
        "max_lon": float(bounds[2]),
        "max_lat": float(bounds[3])
    },
    "invalid_geometries": int(invalid_geom.sum()),
    "empty_geometries": int(empty_geom.sum()),
    "source_hash": source_hash,
    "column_info": {}
}

for col in gdf.columns:
    if col != 'geometry':
        profile["column_info"][col] = {
            "dtype": str(gdf[col].dtype),
            "unique_count": int(gdf[col].nunique()),
            "null_count": int(gdf[col].isnull().sum())
        }

# Save to JSON
output_path = Path("data/profiles/gis_ahmedabad_wards.json")
output_path.parent.mkdir(parents=True, exist_ok=True)
with open(output_path, 'w') as f:
    json.dump(profile, f, indent=2, default=str)

print(f'\nProfile saved to: {output_path}')
