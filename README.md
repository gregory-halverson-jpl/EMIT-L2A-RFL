# EMIT L2A Estimated Surface Reflectance and Uncertainty and Masks 60 m Search and Download Utility

This Python package is a tool for searching, downloading, and reading hypspectral surface reflectance from the Earth Surface Mineral Dust Source Investigation (EMIT) L2A RFL data product.

Gregory H. Halverson (they/them)<br>
[gregory.h.halverson@jpl.nasa.gov](mailto:gregory.h.halverson@jpl.nasa.gov)<br>
NASA Jet Propulsion Laboratory 329G<br>

## Installation

### Standard Installation (pip)

```bash
pip install EMITL2ARFL
```

### HPC Systems with HDF5 Issues

If you encounter HDF5 errors (like `HDF Error -101`) on HPC systems, the issue is typically caused by conflicts between system HDF5 libraries and pip-installed packages. The solution is to use conda-forge packages which bundle compatible HDF5 libraries.

**Using the makefile (recommended):**

```bash
git clone https://github.com/STARS-Data-Fusion/EMIT-L2A-RFL.git
cd EMIT-L2A-RFL
make environment  # Creates mamba environment with conda-forge HDF5
mamba activate EMITL2ARFL
make install
```

**Manual setup:**

```bash
# Create environment with HDF5 from conda-forge
mamba create -n EMITL2ARFL -c conda-forge python=3.10 hdf5 h5py netcdf4
mamba activate EMITL2ARFL

# Install package
pip install EMITL2ARFL
# Or for development: pip install -e .
```

**Set environment variable (HPC systems only):**

```bash
# For fish shell
set -Ux HDF5_USE_FILE_LOCKING FALSE

# For bash shell (add to ~/.bashrc)
export HDF5_USE_FILE_LOCKING=FALSE
```

See [diagnostics/Install HPC.md](diagnostics/Install%20HPC.md) for detailed HPC installation instructions and troubleshooting.

## Diagnostics

Diagnostic tools and troubleshooting guides are available in the [diagnostics/](diagnostics/) folder:

- **[Install HPC.md](diagnostics/Install%20HPC.md)** - Complete HPC installation guide
- **[HPC Troubleshooting.md](diagnostics/HPC%20Troubleshooting.md)** - Common HPC issues and solutions
- **verify_installation.py** - Check if HDF5/NetCDF libraries are properly configured
- **check_hdf5_version.py** - Display library versions and test file opening
- **debug_hpc_environment.py** - Comprehensive environment diagnostic tool

## References

* Green, R. O., et al. (2023). Earth Surface Mineral Dust Source Investigation (EMIT) L2A Estimated Surface Reflectance and Uncertainty and Masks, Version 1. [Data set]. NASA EOSDIS Land Processes DAAC. [doi:10.5067/EMIT/EMITL2ARFL.001](https://doi.org/10.5067/EMIT/EMITL2ARFL.001)

* Green, R. O., et al. (2024). The Earth Surface Mineral Dust Source Investigation (EMIT) on the International Space Station: In-flight instrument performance and first results. *Remote Sensing of Environment*, 282, 113277. [doi:10.1016/j.rse.2023.113277](https://doi.org/10.1016/j.rse.2023.113277)
