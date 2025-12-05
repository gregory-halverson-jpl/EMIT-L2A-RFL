#!/usr/bin/env python
"""
Test file validation with HPC-specific workarounds.

This version tries multiple approaches to handle common HPC issues:
1. HDF5 file locking on network filesystems
2. Path resolution issues
3. Library initialization order
"""

import os
import sys
from pathlib import Path

# WORKAROUND 1: Disable HDF5 file locking BEFORE importing netCDF4
# This must be done before any HDF5/NetCDF4 imports
print("Setting HDF5_USE_FILE_LOCKING=FALSE...")
os.environ['HDF5_USE_FILE_LOCKING'] = 'FALSE'

# Now import EMITL2ARFL (which will import netCDF4)
from EMITL2ARFL import validate_NetCDF_file

filename = "~/data/EMIT_L2A_RFL_001_20230129T004447_2302816_003.nc"

# WORKAROUND 2: Ensure path is fully resolved
filepath = Path(os.path.expanduser(filename)).resolve()
print(f"Validating file: {filepath}")
print(f"File exists: {filepath.exists()}")
if filepath.exists():
    print(f"File size: {filepath.stat().st_size:,} bytes")

try:
    validate_NetCDF_file(str(filepath))
    print(f"✓ Valid NetCDF file: {filepath}")
except Exception as e:
    print(f"✗ Invalid NetCDF file: {filepath}")
    print(f"  Error type: {type(e).__name__}")
    print(f"  Error message: {e}")
    
    # Additional debugging
    print("\nTrying direct netCDF4 access...")
    try:
        import netCDF4
        with netCDF4.Dataset(str(filepath), 'r') as ds:
            print(f"  ✓ Direct access works! Dimensions: {len(ds.dimensions)}, Variables: {len(ds.variables)}")
    except Exception as e2:
        print(f"  ✗ Direct access also fails: {e2}")
