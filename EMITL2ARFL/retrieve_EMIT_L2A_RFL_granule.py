import posixpath
import logging
from os import remove
from os.path import join, expanduser, abspath, exists
from typing import List, Optional

import earthaccess

from .constants import *
from .EMITL2ARFLGranule import EMITL2ARFLGranule
from .find_EMIT_L2A_RFL_granule import find_EMIT_L2A_RFL_granule
from .validate_NetCDF_file import validate_NetCDF_file

logger = logging.getLogger(__name__)

def retrieve_EMIT_L2A_RFL_granule(
        remote_granule: earthaccess.search.DataGranule = None,
        orbit: int = None,
        scene: int = None, 
        download_directory: str = DOWNLOAD_DIRECTORY,
        max_retries: int = 3) -> EMITL2ARFLGranule:
    """
    Retrieve an EMIT L2A Reflectance granule with resilient error handling and retry logic.

    This function retrieves an EMIT L2A Reflectance granule based on the provided granule, orbit, and scene.
    If the granule is not provided, it searches for the granule using the orbit and scene parameters.
    The granule is then downloaded to the specified directory and validated. If files are missing or corrupted,
    the function will attempt to re-download them up to max_retries times.

    Args:
        remote_granule (earthaccess.search.DataGranule, optional): The granule to retrieve. Defaults to None.
        orbit (int, optional): The orbit number to search for the granule. Defaults to None.
        scene (int, optional): The scene number to search for the granule. Defaults to None.
        download_directory (str, optional): The directory to download the granule files to. Defaults to DOWNLOAD_DIRECTORY.
        max_retries (int, optional): Maximum number of retry attempts for downloading corrupted files. Defaults to 3.

    Returns:
        EMITL2ARFLGranule: The retrieved EMIT L2A Reflectance granule wrapped in an EMITL2ARFLGranule object.

    Raises:
        ValueError: If no granule is found for the provided orbit and scene, or if the provided granule is not an EMIT L2A Reflectance collection 1 granule.
        FileNotFoundError: If required files cannot be downloaded after max_retries attempts.
    """
    if remote_granule is None and orbit is not None and scene is not None:
        remote_granule = find_EMIT_L2A_RFL_granule(granule=remote_granule, orbit=orbit, scene=scene)
    
    if remote_granule is None:
        raise ValueError("either granule or orbit and scene must be provided")

    # Parse granule ID from the first data link
    granule_ID = posixpath.splitext(posixpath.basename(remote_granule.data_links()[0]))[0]

    # Validate that this is an EMIT L2A Reflectance collection 1 granule
    if not granule_ID.startswith("EMIT_L2A_RFL_001_"):
        raise ValueError("The provided granule is not an EMIT L2A Reflectance collection 1 granule.")

    # Set up the granule directory
    directory = join(download_directory, granule_ID)
    abs_directory = abspath(expanduser(directory))
    
    # Get expected filenames from the remote granule
    base_filenames = [posixpath.basename(URL) for URL in remote_granule.data_links()]
    local_files = [join(abs_directory, fname) for fname in base_filenames]
    
    # Helper function to identify file types
    def _identify_files(files: List[str]) -> tuple[Optional[str], Optional[str], Optional[str]]:
        """Identify RFL, MASK, and RFLUNCERT files from a list of filenames."""
        reflectance = next((f for f in files if '_RFL_' in f and '_RFLUNCERT_' not in f), None)
        mask = next((f for f in files if '_MASK_' in f), None)
        uncertainty = next((f for f in files if '_RFLUNCERT_' in f), None)
        return reflectance, mask, uncertainty
    
    # Helper function to validate a single file
    def _validate_file(filepath: str, file_type: str) -> bool:
        """Validate that a file exists and is a valid NetCDF file."""
        if not exists(filepath):
            logger.warning(f"{file_type} file does not exist: {filepath}")
            return False
        if not validate_NetCDF_file(filepath):
            logger.warning(f"{file_type} file is corrupted: {filepath}")
            return False
        return True
    
    # Helper function to download specific files
    def _download_files(urls: List[str], retry_attempt: int = 0) -> bool:
        """Download files from URLs to the granule directory."""
        try:
            logger.info(f"Downloading granule files (attempt {retry_attempt + 1}/{max_retries})...")
            earthaccess.download(urls, local_path=abs_directory)
            return True
        except Exception as e:
            logger.error(f"Download failed: {e}")
            return False
    
    # Identify expected file paths
    reflectance_filename, mask_filename, uncertainty_filename = _identify_files(local_files)
    
    if not all([reflectance_filename, mask_filename, uncertainty_filename]):
        raise ValueError('Could not identify all required file types (RFL, MASK, RFLUNCERT) from granule data links.')
    
    # Track which files need to be (re)downloaded
    files_to_download = []
    file_info = {
        'reflectance': (reflectance_filename, 'Reflectance'),
        'mask': (mask_filename, 'Mask'),
        'uncertainty': (uncertainty_filename, 'Uncertainty')
    }
    
    # Initial validation check
    for filepath, file_type in file_info.values():
        if not _validate_file(filepath, file_type):
            files_to_download.append(filepath)
    
    # Retry loop for downloading/repairing files
    retry_count = 0
    while files_to_download and retry_count < max_retries:
        # Remove corrupted files before re-downloading
        for filepath in files_to_download:
            if exists(filepath):
                logger.info(f"Removing corrupted file: {filepath}")
                try:
                    remove(filepath)
                except Exception as e:
                    logger.error(f"Failed to remove corrupted file {filepath}: {e}")
        
        # Download all files (earthaccess will skip existing valid files)
        if not _download_files(remote_granule.data_links(), retry_count):
            retry_count += 1
            continue
        
        # Re-validate files
        files_to_download = []
        for filepath, file_type in file_info.values():
            if not _validate_file(filepath, file_type):
                files_to_download.append(filepath)
        
        if not files_to_download:
            logger.info("All files successfully downloaded and validated.")
            break
        
        retry_count += 1
    
    # Final validation - raise error if any files are still invalid
    if files_to_download:
        raise FileNotFoundError(
            f"Failed to download valid files after {max_retries} attempts. "
            f"Missing or corrupted files: {files_to_download}"
        )
    
    # Create and return the granule object
    local_granule = EMITL2ARFLGranule(
        reflectance_filename=reflectance_filename,
        mask_filename=mask_filename,
        uncertainty_filename=uncertainty_filename
    )

    return local_granule