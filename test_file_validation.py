from os.path import expanduser

from EMITL2ARFL import validate_NetCDF_file

filename = "~/data/EMIT_L2A_RFL_001_20230129T004447_2302816_003.nc"

try:
    validate_NetCDF_file(filename)
    print(f"✓ Valid NetCDF file: {filename}")
except Exception as e:
    print(f"✗ Invalid NetCDF file: {filename} - {type(e).__name__}: {e}")

