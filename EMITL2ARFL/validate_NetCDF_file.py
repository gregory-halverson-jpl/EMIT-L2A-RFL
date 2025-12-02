import os
import netCDF4
from pathlib import Path
from typing import Union


def validate_NetCDF_file(filename: Union[str, Path]) -> bool:
    """
    Validate whether a file is a valid NetCDF file.
    
    Parameters
    ----------
    filename : str or Path
        Path to the NetCDF file to validate
    
    Returns
    -------
    bool
        True if the file is a valid NetCDF file, False otherwise
    
    Raises
    ------
    FileNotFoundError
        If the file does not exist
    
    Examples
    --------
    >>> validate_NetCDF_file('data.nc')
    True
    >>> validate_NetCDF_file('corrupted.nc')
    False
    """
    filename = Path(filename)
    
    if not filename.exists():
        raise FileNotFoundError(f"File not found: {filename}")
    
    if filename.stat().st_size == 0:
        return False
    
    try:
        with netCDF4.Dataset(filename, "r") as ds:
            # Try to access basic attributes to ensure file is readable
            _ = ds.dimensions
            _ = ds.variables
        return True
    except (OSError, IOError, RuntimeError) as e:
        # NetCDF4 raises OSError for invalid files
        return False
