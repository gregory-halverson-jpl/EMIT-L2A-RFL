#!/usr/bin/env python
"""
Diagnostic script to debug HPC environment issues with NetCDF file access.

This script helps identify differences between interactive iPython sessions
and script execution that might cause HDF/NetCDF errors on HPC systems.
"""

import os
import sys
from pathlib import Path

def print_section(title):
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f" {title}")
    print('='*60)

def check_file_details(filename):
    """Check basic file system details."""
    print_section("FILE SYSTEM DETAILS")
    
    filepath = Path(os.path.expanduser(filename))
    print(f"Original path: {filename}")
    print(f"Expanded path: {filepath}")
    print(f"Absolute path: {filepath.resolve()}")
    print(f"File exists: {filepath.exists()}")
    
    if filepath.exists():
        stat = filepath.stat()
        print(f"File size: {stat.st_size:,} bytes")
        print(f"File mode: {oct(stat.st_mode)}")
        print(f"Is readable: {os.access(filepath, os.R_OK)}")
        print(f"Is writable: {os.access(filepath, os.W_OK)}")
        
        # Check if it's on a network filesystem
        try:
            import subprocess
            result = subprocess.run(['df', '-T', str(filepath)], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print(f"\nFilesystem info:")
                print(result.stdout)
        except Exception as e:
            print(f"Could not check filesystem type: {e}")

def check_library_versions():
    """Check versions of critical libraries."""
    print_section("LIBRARY VERSIONS")
    
    try:
        import netCDF4
        print(f"netCDF4 version: {netCDF4.__version__}")
        print(f"netCDF4 file: {netCDF4.__file__}")
    except ImportError as e:
        print(f"ERROR: Cannot import netCDF4: {e}")
        return False
    
    try:
        import h5py
        print(f"h5py version: {h5py.__version__}")
        print(f"h5py file: {h5py.__file__}")
        print(f"HDF5 version: {h5py.version.hdf5_version}")
    except ImportError:
        print("h5py not available (optional)")
    
    try:
        import numpy
        print(f"numpy version: {numpy.__version__}")
    except ImportError:
        print("numpy not available")
    
    return True

def check_environment_variables():
    """Check relevant environment variables."""
    print_section("ENVIRONMENT VARIABLES")
    
    env_vars = [
        'HDF5_USE_FILE_LOCKING',
        'HDF5_PLUGIN_PATH',
        'NETCDF_PLUGIN_DIR',
        'LD_LIBRARY_PATH',
        'DYLD_LIBRARY_PATH',
        'PYTHONPATH',
    ]
    
    for var in env_vars:
        value = os.environ.get(var, '<not set>')
        print(f"{var}: {value}")

def test_direct_netcdf4_access(filename):
    """Test direct netCDF4.Dataset access."""
    print_section("DIRECT NETCDF4 ACCESS TEST")
    
    import netCDF4
    filepath = Path(os.path.expanduser(filename)).resolve()
    
    print(f"Attempting to open: {filepath}")
    
    try:
        # Try opening with explicit path conversion
        print("\nTest 1: Opening with resolved absolute path...")
        with netCDF4.Dataset(str(filepath), 'r') as ds:
            print(f"✓ SUCCESS: File opened")
            print(f"  Dimensions: {len(ds.dimensions)}")
            print(f"  Variables: {len(ds.variables)}")
            if ds.dimensions:
                print(f"  Dimension names: {list(ds.dimensions.keys())[:5]}")
            if ds.variables:
                print(f"  Variable names: {list(ds.variables.keys())[:5]}")
        return True
        
    except Exception as e:
        print(f"✗ FAILED: {type(e).__name__}: {e}")
        print(f"\nError details:")
        print(f"  Error type: {type(e)}")
        print(f"  Error args: {e.args}")
        
        # Check for specific error patterns
        error_str = str(e)
        if "errno -101" in error_str.lower():
            print(f"\n⚠ HDF Error -101 detected!")
            print(f"  This typically indicates:")
            print(f"  - File corruption")
            print(f"  - Network filesystem caching issues")
            print(f"  - HDF5 library incompatibility")
        
        return False

def test_with_file_locking_disabled(filename):
    """Test with HDF5 file locking disabled."""
    print_section("TEST WITH FILE LOCKING DISABLED")
    
    # Save original value
    original_value = os.environ.get('HDF5_USE_FILE_LOCKING')
    
    try:
        # Disable file locking
        os.environ['HDF5_USE_FILE_LOCKING'] = 'FALSE'
        print("Set HDF5_USE_FILE_LOCKING=FALSE")
        
        # Force reload of netCDF4 to pick up new environment
        import netCDF4
        if 'netCDF4' in sys.modules:
            print("Reloading netCDF4 module...")
            import importlib
            importlib.reload(netCDF4)
        
        filepath = Path(os.path.expanduser(filename)).resolve()
        print(f"Attempting to open: {filepath}")
        
        with netCDF4.Dataset(str(filepath), 'r') as ds:
            print(f"✓ SUCCESS with HDF5_USE_FILE_LOCKING=FALSE")
            return True
            
    except Exception as e:
        print(f"✗ FAILED even with file locking disabled: {e}")
        return False
        
    finally:
        # Restore original value
        if original_value is None:
            os.environ.pop('HDF5_USE_FILE_LOCKING', None)
        else:
            os.environ['HDF5_USE_FILE_LOCKING'] = original_value

def test_validate_function(filename):
    """Test the actual validate_NetCDF_file function."""
    print_section("VALIDATE_NETCDF_FILE FUNCTION TEST")
    
    try:
        from EMITL2ARFL import validate_NetCDF_file
        print(f"Attempting validation with validate_NetCDF_file()...")
        
        validate_NetCDF_file(filename)
        print(f"✓ SUCCESS: File passed validation")
        return True
        
    except Exception as e:
        print(f"✗ FAILED: {type(e).__name__}: {e}")
        
        # Show the full traceback
        import traceback
        print(f"\nFull traceback:")
        traceback.print_exc()
        return False

def main():
    """Main diagnostic routine."""
    print("="*60)
    print(" HPC NetCDF Environment Diagnostic Tool")
    print("="*60)
    
    if len(sys.argv) < 2:
        print("\nUsage: python debug_hpc_environment.py <path_to_netcdf_file>")
        print("\nExample:")
        print("  python debug_hpc_environment.py ~/data/EMIT_L2A_RFL_001_20230129T004447_2302816_003.nc")
        sys.exit(1)
    
    filename = sys.argv[1]
    
    # Run all diagnostic checks
    check_file_details(filename)
    
    if not check_library_versions():
        print("\nERROR: Required libraries not available. Exiting.")
        sys.exit(1)
    
    check_environment_variables()
    
    # Try different access methods
    test1 = test_direct_netcdf4_access(filename)
    test2 = test_with_file_locking_disabled(filename)
    test3 = test_validate_function(filename)
    
    # Summary
    print_section("SUMMARY")
    print(f"Direct netCDF4 access: {'✓ PASS' if test1 else '✗ FAIL'}")
    print(f"With file locking disabled: {'✓ PASS' if test2 else '✗ FAIL'}")
    print(f"validate_NetCDF_file function: {'✓ PASS' if test3 else '✗ FAIL'}")
    
    if not test1 and test2:
        print("\n⚠ RECOMMENDATION:")
        print("  The file opens successfully with HDF5_USE_FILE_LOCKING=FALSE")
        print("  This is a common issue on NFS/Lustre filesystems.")
        print()
        print("  FIX: Add this to your ~/.bashrc on the HPC system:")
        print("    export HDF5_USE_FILE_LOCKING=FALSE")
        print("    source ~/.bashrc")
        print()
        print("  Or run scripts with:")
        print("    HDF5_USE_FILE_LOCKING=FALSE python your_script.py")
        print()
        print("  Or use the wrapper script:")
        print("    ./test_hpc.sh")
        print()
        print("  NOTE: Setting os.environ in Python code is often too late!")
        print("  The environment variable must be set BEFORE Python starts.")
    
    if not test1 and not test2:
        print("\n⚠ RECOMMENDATION:")
        print("  The file cannot be opened even with file locking disabled.")
        print("  This suggests:")
        print("    1. File may be corrupted")
        print("    2. HDF5/NetCDF library incompatibility")
        print("    3. Filesystem-level issues")
        print("  Try:")
        print("    - Re-downloading the file")
        print("    - Checking md5/checksum integrity")
        print("    - Verifying HDF5 library versions match")

if __name__ == "__main__":
    main()
