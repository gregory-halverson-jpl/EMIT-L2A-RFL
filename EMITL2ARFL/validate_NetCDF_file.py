import netCDF4
from pathlib import Path
from typing import Union

from .exceptions import (
    NetCDFFileNotFoundError,
    NetCDFEmptyFileError,
    NetCDFCorruptedError,
    NetCDFReadError
)


def validate_NetCDF_file(filename: Union[str, Path], file_type: str = "NetCDF") -> None:
    """
    Validate whether a file is a valid NetCDF file.
    
    This function performs comprehensive validation of a NetCDF file, checking for:
    - File existence
    - Non-zero file size
    - NetCDF format validity
    - Readability of dimensions and variables
    
    Parameters
    ----------
    filename : str or Path
        Path to the NetCDF file to validate
    file_type : str, optional
        Descriptive name for the file type (e.g., "Reflectance", "Mask").
        Used in error messages for better context. Defaults to "NetCDF".
    
    Returns
    -------
    None
        Returns nothing if validation succeeds
    
    Raises
    ------
    NetCDFFileNotFoundError
        If the file does not exist at the specified path
    NetCDFEmptyFileError
        If the file exists but has zero bytes (empty file)
    NetCDFCorruptedError
        If the file is corrupted or has invalid NetCDF format
    NetCDFReadError
        If the file cannot be read due to I/O errors or permission issues
    
    Examples
    --------
    >>> validate_NetCDF_file('data.nc')
    >>> validate_NetCDF_file('reflectance.nc', file_type='Reflectance')
    >>> validate_NetCDF_file('missing.nc')  # Raises NetCDFFileNotFoundError
    """
    filename = Path(filename)
    
    # Check if file exists
    if not filename.exists():
        raise NetCDFFileNotFoundError(
            f"{file_type} file does not exist at path: {filename}"
        )
    
    # Check if file is empty
    file_size = filename.stat().st_size
    if file_size == 0:
        raise NetCDFEmptyFileError(
            f"{file_type} file is empty (0 bytes): {filename}"
        )
    
    # Attempt to open and validate NetCDF structure
    try:
        with netCDF4.Dataset(filename, "r") as ds:
            # Try to access basic attributes to ensure file is readable
            dimensions = ds.dimensions
            variables = ds.variables
            
            # Verify that the file contains data structures
            if len(dimensions) == 0 and len(variables) == 0:
                raise NetCDFCorruptedError(
                    f"{file_type} file is corrupted: contains no dimensions or variables. "
                    f"File: {filename}, Size: {file_size} bytes"
                )
    
    except (OSError, IOError) as e:
        # I/O errors suggest file read problems or corruption
        error_msg = str(e).lower()
        if "permission" in error_msg or "access" in error_msg:
            raise NetCDFReadError(
                f"{file_type} file cannot be read due to permission error: {filename}. "
                f"Error: {e}"
            )
        else:
            raise NetCDFReadError(
                f"{file_type} file cannot be read due to I/O error: {filename}. "
                f"File size: {file_size} bytes. Error: {e}"
            )
    
    except RuntimeError as e:
        # RuntimeError typically indicates NetCDF format problems
        raise NetCDFCorruptedError(
            f"{file_type} file is corrupted or has invalid NetCDF format: {filename}. "
            f"File size: {file_size} bytes. Error: {e}"
        )
    
    except Exception as e:
        # Catch-all for unexpected errors
        raise NetCDFCorruptedError(
            f"{file_type} file validation failed with unexpected error: {filename}. "
            f"File size: {file_size} bytes. Error type: {type(e).__name__}, Message: {e}"
        )
