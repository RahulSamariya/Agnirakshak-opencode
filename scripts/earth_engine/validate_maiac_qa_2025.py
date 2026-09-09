"""
MAIAC AOD QA Validation Script
==============================

This script validates the correct decoding of MAIAC AOD_QA bits and tests
extraction for a single station-date: Chandkheda, 2025-01-15.

OFFICIAL MAIAC AOD_QA BIT DEFINITION (16-bit unsigned integer):
- Bits 0-2: Cloud Mask (3 bits)
  - 000 = Undefined
  - 001 = Clear
  - 010 = Possibly Cloudy (detected by AOD filter)
  - 011 = Cloudy (detected by cloud mask algorithm)
  - 101 = Cloud Shadow
  - 110 = Hot spot of fire
  - 111 = Water Sediments

- Bits 3-4: Land Water Snow/Ice Mask (2 bits)
  - 00 = Land
  - 01 = Water
  - 10 = Snow
  - 11 = Ice

- Bits 5-7: Adjacency Mask (3 bits)
  - 000 = Normal condition/Clear
  - 001 = Adjacent to clouds
  - 010 = Surrounded by >4 cloudy pixels
  - 011 = Adjacent to a single cloudy pixel
  - 100 = Adjacent to snow
  - 101 = Snow was previously detected

- Bits 8-11: QA for AOD (4 bits)
  - 0000 = Best quality
  - 0001 = Water Sediments detected
  - 0011 = 1 neighbor cloud
  - 0100 = >1 neighbor clouds
  - 0101 = No retrieval (cloudy, or whatever)
  - 0110 = No retrieval near detected or previously snow
  - 0111 = Climatology AOD (altitude above 3.5km water, 4.2km land)
  - 1000 = No retrieval due to sun glint
  - 1001 = Retrieved AOD very low (<0.05) due to glint
  - 1010 = AOD within +-2km from coastline replaced by nearby AOD
  - 1011 = Land, research quality: AOD retrieved but CM is possibly cloudy

- Bit 12: Glint Mask
  - 0 = No glint
  - 1 = Glint (glint angle < 40°)

- Bits 13-14: Aerosol Model
  - 00 = Background model (regional)
  - 01 = Smoke model (regional)
  - 10 = Dust model

- Bit 15: Reserved

PRIMARY MODELING AOD REQUIREMENTS:
- Bits 0-2 = 1 (Clear)
- Bits 3-4 = 0 (Land)
- Bits 8-11 = 0 (Best quality)

USAGE:
    python scripts/earth_engine/validate_maiac_qa_2025.py
"""

import sys
from datetime import datetime
from pathlib import Path

# ============================================================
# CONFIGURATION
# ============================================================

EE_PROJECT = "agniraksha-508013"
MAIAC_COLLECTION = "MODIS/061/MCD19A2_GRANULES"
AOD_BAND = "Optical_Depth_055"
QA_BAND = "AOD_QA"
SCALE_FACTOR = 0.001

# Test case: Chandkheda, 2025-01-15
TEST_STATION = {
    "station_id": "site_5453",
    "name": "Chandkheda",
    "lat": 23.107969,
    "lon": 72.574648,
}
TEST_DATE = "2025-01-15"

print("=" * 70)
print("MAIAC AOD QA VALIDATION")
print("=" * 70)
print(f"Script generated: {datetime.now().isoformat()}")
print(f"Test case: {TEST_STATION['name']}, {TEST_DATE}")
print()

# ============================================================
# STEP 1: CHECK EARTH ENGINE AUTHENTICATION
# ============================================================

print("[STEP 1] Checking Earth Engine authentication...")

try:
    import ee
    ee.Initialize(project=EE_PROJECT)
    print("  Earth Engine authenticated successfully")
    print(f"  Project: {EE_PROJECT}")
except Exception as e:
    print(f"  ERROR: Earth Engine authentication failed: {e}")
    print()
    print("  To authenticate:")
    print("    1. Install: pip install earthengine-api")
    print("    2. Authenticate: earthengine authenticate")
    print("    3. Set project: earthengine set_project agniraksha-508013")
    print()
    print("  See: https://developers.google.com/earth-engine/guides/python_install")
    sys.exit(1)

print()

# ============================================================
# STEP 2: DEFINE QA DECODING FUNCTIONS
# ============================================================

print("[STEP 2] Defining QA decoding functions...")

def decode_cloud_mask(qa_value):
    """Decode bits 0-2: Cloud Mask"""
    return qa_value & 7  # Mask with 0b111

def decode_land_mask(qa_value):
    """Decode bits 3-4: Land Water Snow/Ice Mask"""
    return (qa_value >> 3) & 3  # Shift right 3, mask with 0b11

def decode_adjacency_mask(qa_value):
    """Decode bits 5-7: Adjacency Mask"""
    return (qa_value >> 5) & 7  # Shift right 5, mask with 0b111

def decode_aod_qa(qa_value):
    """Decode bits 8-11: QA for AOD"""
    return (qa_value >> 8) & 15  # Shift right 8, mask with 0b1111

def decode_glint_mask(qa_value):
    """Decode bit 12: Glint Mask"""
    return (qa_value >> 12) & 1  # Shift right 12, mask with 0b1

def decode_aerosol_model(qa_value):
    """Decode bits 13-14: Aerosol Model"""
    return (qa_value >> 13) & 3  # Shift right 13, mask with 0b11

def get_cloud_mask_name(value):
    """Get human-readable name for cloud mask value"""
    names = {
        0: "Undefined",
        1: "Clear",
        2: "Possibly Cloudy",
        3: "Cloudy",
        5: "Cloud Shadow",
        6: "Hot spot of fire",
        7: "Water Sediments",
    }
    return names.get(value, f"Unknown ({value})")

def get_land_mask_name(value):
    """Get human-readable name for land mask value"""
    names = {
        0: "Land",
        1: "Water",
        2: "Snow",
        3: "Ice",
    }
    return names.get(value, f"Unknown ({value})")

def get_adjacency_mask_name(value):
    """Get human-readable name for adjacency mask value"""
    names = {
        0: "Normal/Clear",
        1: "Adjacent to clouds",
        2: "Surrounded by >4 cloudy pixels",
        3: "Adjacent to single cloudy pixel",
        4: "Adjacent to snow",
        5: "Snow previously detected",
    }
    return names.get(value, f"Unknown ({value})")

def get_aod_qa_name(value):
    """Get human-readable name for AOD QA value"""
    names = {
        0: "Best quality",
        1: "Water Sediments detected",
        3: "1 neighbor cloud",
        4: ">1 neighbor clouds",
        5: "No retrieval (cloudy)",
        6: "No retrieval near snow",
        7: "Climatology AOD (high altitude)",
        8: "No retrieval due to sun glint",
        9: "Very low AOD due to glint",
        10: "Coastline replacement",
        11: "Research quality (CM possibly cloudy)",
    }
    return names.get(value, f"Unknown ({value})")

def get_glint_mask_name(value):
    """Get human-readable name for glint mask value"""
    names = {
        0: "No glint",
        1: "Glint detected",
    }
    return names.get(value, f"Unknown ({value})")

def get_aerosol_model_name(value):
    """Get human-readable name for aerosol model value"""
    names = {
        0: "Background (regional)",
        1: "Smoke (regional)",
        2: "Dust",
    }
    return names.get(value, f"Unknown ({value})")

print("  QA decoding functions defined")
print()

# ============================================================
# STEP 3: DEFINE QA MASKING FUNCTION
# ============================================================

print("[STEP 3] Defining QA masking function...")

def create_strict_qa_mask():
    """
    Create strict QA mask for primary modeling AOD.
    
    Requirements:
    - Bits 0-2 = 1 (Clear)
    - Bits 3-4 = 0 (Land)
    - Bits 8-11 = 0 (Best quality)
    
    Returns:
        ee.Image: Binary mask (1 = valid, 0 = invalid)
    """
    # Get the QA band
    qa_image = ee.ImageCollection(MAIAC_COLLECTION).select(QA_BAND).first()
    
    # Bits 0-2: Cloud Mask must be 1 (Clear)
    cloud_mask = qa_image.bitwiseAnd(7).eq(1)  # 0b111 = 7
    
    # Bits 3-4: Land Mask must be 0 (Land)
    land_mask = qa_image.rightShift(3).bitwiseAnd(3).eq(0)  # 0b11 = 3
    
    # Bits 8-11: AOD QA must be 0 (Best quality)
    aod_qa_mask = qa_image.rightShift(8).bitwiseAnd(15).eq(0)  # 0b1111 = 15
    
    # Combined mask: all conditions must be true
    valid_mask = cloud_mask.And(land_mask).And(aod_qa_mask)
    
    return valid_mask

print("  Strict QA mask requirements:")
print("    - Bits 0-2 = 1 (Clear)")
print("    - Bits 3-4 = 0 (Land)")
print("    - Bits 8-11 = 0 (Best quality)")
print()

# ============================================================
# STEP 4: EXTRACT AND DECODE QA FOR TEST CASE
# ============================================================

print("[STEP 4] Extracting QA for test case...")
print(f"  Station: {TEST_STATION['name']} ({TEST_STATION['lat']}, {TEST_STATION['lon']})")
print(f"  Date: {TEST_DATE}")
print()

# Get the QA image for the test date
date = ee.Date(TEST_DATE)
next_date = date.advance(1, 'day')

maiac_daily = ee.ImageCollection(MAIAC_COLLECTION) \
    .filterDate(date, next_date) \
    .select([AOD_BAND, QA_BAND])

# Check if any images exist
image_count = maiac_daily.size().getInfo()
print(f"  Number of MAIAC granules: {image_count}")

if image_count == 0:
    print("  ERROR: No MAIAC data for this date")
    sys.exit(1)

# Use composite of all granules for the day
# This ensures we capture data from all overpasses
composite_image = maiac_daily.median()

# Extract raw values at station point
point = ee.Geometry.Point([TEST_STATION['lon'], TEST_STATION['lat']])
EXTRACTION_RADIUS = 2000  # meters (increased for better coverage)

# Try to extract from composite
raw_values = composite_image.reduceRegion(
    ee.Reducer.first(),
    point,
    EXTRACTION_RADIUS
).getInfo()

raw_aod = raw_values.get(AOD_BAND)
raw_qa = raw_values.get(QA_BAND)

# If composite returns None, try each granule individually
if raw_qa is None:
    print("  Composite returned None, trying individual granules...")
    
    # Get list of images
    image_list = maiac_daily.toList(maiac_daily.size())
    image_count_actual = image_list.size().getInfo()
    
    for i in range(image_count_actual):
        img = ee.Image(image_list.get(i))
        values = img.reduceRegion(
            ee.Reducer.first(),
            point,
            EXTRACTION_RADIUS
        ).getInfo()
        
        qa_val = values.get(QA_BAND)
        if qa_val is not None:
            raw_qa = qa_val
            raw_aod = values.get(AOD_BAND)
            print(f"  Found valid data in granule {i+1}")
            break
    
    if raw_qa is None:
        print("  WARNING: No valid data found in any granule")

print()
print("  RAW VALUES:")
if raw_qa is not None:
    print(f"    AOD_QA (decimal): {raw_qa}")
    print(f"    AOD_QA (binary):  {bin(raw_qa)}")
else:
    print(f"    AOD_QA (decimal): None")
    print(f"    AOD_QA (binary):  None")
print(f"    Optical_Depth_055 (raw): {raw_aod}")
if raw_aod is not None:
    print(f"    Optical_Depth_055 (scaled): {raw_aod * SCALE_FACTOR}")
else:
    print(f"    Optical_Depth_055 (scaled): None")
print()

# ============================================================
# STEP 5: DECODE QA BITS
# ============================================================

print("[STEP 5] Decoding QA bits...")

if raw_qa is not None:
    cloud_mask_val = decode_cloud_mask(raw_qa)
    land_mask_val = decode_land_mask(raw_qa)
    adjacency_mask_val = decode_adjacency_mask(raw_qa)
    aod_qa_val = decode_aod_qa(raw_qa)
    glint_mask_val = decode_glint_mask(raw_qa)
    aerosol_model_val = decode_aerosol_model(raw_qa)

    print(f"    Bits 0-2 (Cloud Mask): {cloud_mask_val} = {get_cloud_mask_name(cloud_mask_val)}")
    print(f"    Bits 3-4 (Land Mask): {land_mask_val} = {get_land_mask_name(land_mask_val)}")
    print(f"    Bits 5-7 (Adjacency Mask): {adjacency_mask_val} = {get_adjacency_mask_name(adjacency_mask_val)}")
    print(f"    Bits 8-11 (AOD QA): {aod_qa_val} = {get_aod_qa_name(aod_qa_val)}")
    print(f"    Bit 12 (Glint Mask): {glint_mask_val} = {get_glint_mask_name(glint_mask_val)}")
    print(f"    Bits 13-14 (Aerosol Model): {aerosol_model_val} = {get_aerosol_model_name(aerosol_model_val)}")
else:
    print("    Cannot decode QA bits: raw_qa is None")
    cloud_mask_val = None
    land_mask_val = None
    adjacency_mask_val = None
    aod_qa_val = None
    glint_mask_val = None
    aerosol_model_val = None
print()

# ============================================================
# STEP 6: CHECK QA MASKING
# ============================================================

print("[STEP 6] Checking QA masking...")

if raw_qa is not None:
    cloud_clear = cloud_mask_val == 1
    land_valid = land_mask_val == 0
    aod_best_quality = aod_qa_val == 0

    print(f"    Cloud Mask = Clear (1): {cloud_clear}")
    print(f"    Land Mask = Land (0): {land_valid}")
    print(f"    AOD QA = Best quality (0): {aod_best_quality}")
else:
    print("    Cannot check QA masking: raw_qa is None")
    cloud_clear = False
    land_valid = False
    aod_best_quality = False
print()

# Apply QA mask
qa_mask = create_strict_qa_mask()

# Get masked AOD
masked_composite = composite_image.select(AOD_BAND).multiply(SCALE_FACTOR).updateMask(qa_mask)

masked_value = masked_composite.reduceRegion(
    ee.Reducer.first(),
    point,
    EXTRACTION_RADIUS
).getInfo()

masked_aod = masked_value.get(AOD_BAND)

print("  MASKED AOD:")
print(f"    Station pixel AOD (masked): {masked_aod}")
print()

# ============================================================
# STEP 7: NEIGHBORHOOD ANALYSIS
# ============================================================

print("[STEP 7] Neighborhood analysis...")

# Define neighborhood (3x3 pixels = 3km x 3km)
neighborhood_radius = 1500  # meters

# Get all pixels in neighborhood
neighborhood_values = composite_image.select([AOD_BAND, QA_BAND]).reduceRegion(
    ee.Reducer.toList(),
    point.buffer(neighborhood_radius),
    EXTRACTION_RADIUS
).getInfo()

# Count valid pixels
qa_values = neighborhood_values.get(QA_BAND)
valid_count = 0
total_aod = 0

for qa in qa_values:
    # Check if pixel is valid
    cloud = decode_cloud_mask(qa) == 1
    land = decode_land_mask(qa) == 0
    aod_qa = decode_aod_qa(qa) == 0
    
    if cloud and land and aod_qa:
        valid_count += 1

# Get AOD values
aod_values = neighborhood_values.get(AOD_BAND)
masked_aod_values = []

for i, qa in enumerate(qa_values):
    cloud = decode_cloud_mask(qa) == 1
    land = decode_land_mask(qa) == 0
    aod_qa = decode_aod_qa(qa) == 0
    
    if cloud and land and aod_qa:
        masked_aod_values.append(aod_values[i] * SCALE_FACTOR)

neighborhood_mean = sum(masked_aod_values) / len(masked_aod_values) if masked_aod_values else None

print(f"    Total neighborhood pixels: {len(qa_values)}")
print(f"    Valid neighborhood pixels (masked): {valid_count}")
print(f"    Masked neighborhood mean AOD: {neighborhood_mean}")
print()

# ============================================================
# STEP 8: FINAL REPORT
# ============================================================

print("=" * 70)
print("VALIDATION REPORT")
print("=" * 70)
print()
print(f"Station: {TEST_STATION['name']} ({TEST_STATION['station_id']})")
print(f"Date: {TEST_DATE}")
print()
print("RAW VALUES:")
print(f"  AOD_QA (decimal): {raw_qa}")
print(f"  AOD_QA (binary):  {bin(raw_qa)}")
print(f"  Optical_Depth_055 (raw): {raw_aod}")
print(f"  Optical_Depth_055 (scaled): {raw_aod * SCALE_FACTOR if raw_aod is not None else None}")
print()
print("DECODED QA FIELDS:")
print(f"  Cloud Mask (bits 0-2): {cloud_mask_val} = {get_cloud_mask_name(cloud_mask_val)}")
print(f"  Land Mask (bits 3-4): {land_mask_val} = {get_land_mask_name(land_mask_val)}")
print(f"  Adjacency Mask (bits 5-7): {adjacency_mask_val} = {get_adjacency_mask_name(adjacency_mask_val)}")
print(f"  AOD QA (bits 8-11): {aod_qa_val} = {get_aod_qa_name(aod_qa_val)}")
print(f"  Glint Mask (bit 12): {glint_mask_val} = {get_glint_mask_name(glint_mask_val)}")
print(f"  Aerosol Model (bits 13-14): {aerosol_model_val} = {get_aerosol_model_name(aerosol_model_val)}")
print()
print("QA MASKING:")
print(f"  Cloud Mask = Clear (1): {cloud_clear}")
print(f"  Land Mask = Land (0): {land_valid}")
print(f"  AOD QA = Best quality (0): {aod_best_quality}")
print(f"  Overall QA mask valid: {cloud_clear and land_valid and aod_best_quality}")
print()
print("MASKED AOD:")
print(f"  Station pixel AOD (masked): {masked_aod}")
print()
print("NEIGHBORHOOD ANALYSIS:")
print(f"  Total neighborhood pixels: {len(qa_values)}")
print(f"  Valid neighborhood pixels (masked): {valid_count}")
print(f"  Masked neighborhood mean AOD: {neighborhood_mean}")
print()
print("CONCLUSION:")
if masked_aod is not None:
    print(f"  Station pixel has VALID masked AOD: {masked_aod}")
else:
    print(f"  Station pixel has NO VALID masked AOD (masked out by QA)")
print()
print("STOP.")