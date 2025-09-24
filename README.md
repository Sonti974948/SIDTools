# ![sidtools logo](https://github.com/user-attachments/assets/df05f05b-e728-4b46-a28a-26b66522abcc)
 # SIDTools

A Python package for processing and organizing ASE trajectory files with utilities for running jobs on HPC clusters using Slurm.

## Features

- **s_make**: Split multi-frame `.xyz` or `.db` files into individual trajectory folders
- **s_run**: Submit Slurm batch jobs across multiple directories
- **s_store**: Collect VASP results into ASE databases with support for optimization and MD trajectories
- **s_gpumd**: Prepare and launch GPUMD simulations from structure files

## Installation

### Prerequisites

- Python 3.7 or higher
- ASE (Atomic Simulation Environment)
- Slurm (for job submission)
- GPUMD (optional, for molecular dynamics)

### Install Sidtools

```bash
# Install from PyPI
pip install sidtools

# Or install from source
git clone https://github.com/Sonti974948/SIDTools.git
cd sidtools
pip install -e .
```

### Dependencies

The package automatically installs:
- `ase>=3.22.0` - For reading/writing atomic structures
- `numpy>=1.20.0` - For numerical operations

## Quick Start

### 1. Split Trajectories

```bash
# Split an XYZ file into individual trajectory folders
s_make -T input.xyz --base output_dir -F script.sh src/

# Split a database file
s_make -T structures.db --base output_dir -F script.sh src/

```

This creates:
```
output_dir/
├── trajectory_1/
│   ├── init.traj
│   ├── script.sh
│   └── src/
├── trajectory_2/
│   ├── init.traj
│   ├── script.sh
│   └── src/
└── ...
```

### 2. Submit Jobs

```bash
# Submit all script.sh files found in subdirectories
s_run --base output_dir

# Use a different script pattern
s_run --base output_dir --pattern run.sh

```

### 3. Collect Results

```bash
# Collect optimized structures
s_store --base output_dir --db results.db --type opt

# Collect MD trajectories with stride
s_store --base output_dir --db md_results.db --type md --stride 10 --max-frames 100

```

### 4. Prepare GPUMD Simulations

```bash
# Create GPUMD input folders and submit jobs
s_gpumd --base gpumd_out --db structures.db --input run_GPUMD.sh nep.txt run.in --min 1 --max 50

# Submit all configurations
s_gpumd --base gpumd_out --db structures.db --input run_GPUMD.sh nep.txt run.in
```

## Detailed Usage

### s_make - Split Trajectories

Splits multi-frame files into individual trajectory folders.

```bash
s_make -T <input_file> --base <output_dir> [options]
```

**Arguments:**
- `-T, --trajectory`: Input `.xyz` or `.db` file
- `--base`: Base directory for output folders
- `-F, --files`: Files/folders to copy (default: `01_submit.py script.sh src`)

**Options:**
- `--verbose, -v`: Enable verbose logging
- `--overwrite`: Overwrite existing directories

**Examples:**
```bash
# Basic usage
s_make -T trajs.xyz --base run_dir

# Copy specific files
s_make -T trajs.xyz --base run_dir -F script.sh input.in src/

# Overwrite existing directories
s_make -T trajs.xyz --base run_dir --overwrite

```

### s_run - Submit Jobs

Submits Slurm batch jobs in directories containing job scripts.

```bash
s_run --base <directory> [options]
```

**Arguments:**
- `--base`: Base directory to search for job scripts

**Options:**
- `--pattern`: Script filename pattern (default: `script.sh`)
- `--verbose, -v`: Enable verbose logging

**Examples:**
```bash
# Submit all script.sh files
s_run --base run_dir

# Use different script pattern
s_run --base run_dir --pattern run.sh

```

### s_store - Collect Results

Collects VASP results into ASE databases.

```bash
s_store --base <directory> --db <output.db> [options]
```

**Arguments:**
- `--base`: Directory containing trajectory folders
- `--db`: Output database filename

**Options:**
- `--type`: DFT type - `opt` (optimization) or `md` (molecular dynamics)
- `--subfolder`: Subfolder name (auto-set based on type)
- `--filename`: VASP output filename (default: `vasprun.xml`)
- `--stride`: For MD: process every Nth frame (default: 1)
- `--max-frames`: For MD: maximum frames to process
- `--verbose, -v`: Enable verbose logging

**Examples:**
```bash
# Collect optimized structures
s_store --base run_dir --db optimized.db --type opt

# Collect MD trajectories with sampling
s_store --base run_dir --db md.db --type md --stride 5 --max-frames 100

# Use custom subfolder
s_store --base run_dir --db results.db --type opt --subfolder my_calc

```

### s_gpumd - GPUMD Simulations

Prepares and launches GPUMD simulations.

```bash
s_gpumd --base <directory> --db <input_file> [options]
```

**Arguments:**
- `--base`: Base directory for GPUMD folders
- `--db`: Input `.xyz` or `.db` file

**Options:**
- `--input`: Input files to copy (default: `run_GPUMD.sh nep.txt run.in`)
- `--min`: Minimum trajectory index (default: 1)
- `--max`: Maximum trajectory index (default: all configs)
- `--overwrite`: Overwrite existing directories
- `--verbose, -v`: Enable verbose logging

**Examples:**
```bash
# Process all configurations
s_gpumd --base gpumd_out --db structures.db

# Process subset with custom inputs
s_gpumd --base gpumd_out --db structures.db --min 10 --max 50 --input run.sh model.txt

# Overwrite existing directories
s_gpumd --base gpumd_out --db structures.db --overwrite

```

## File Structure

### Input Files

- **XYZ files**: Multi-frame atomic structures
- **Database files**: ASE databases with atomic structures
- **VASP files**: `vasprun.xml` output files

### Output Structure

```
base_directory/
├── trajectory_1/
│   ├── init.traj          # Atomic structure
│   ├── script.sh          # Job script
│   ├── src/               # Source files
│   └── opt_PBE_400_111/   # VASP output (for optimization)
│       └── vasprun.xml
├── trajectory_2/
│   └── ...
└── ...
```

## Troubleshooting

### Common Issues

**1. "sbatch command not found"**
- Ensure Slurm is installed and `sbatch` is in your PATH
- Check if you're on a system with Slurm scheduler

**2. "File not found" errors**
- Check file paths and permissions
- Use `--verbose` for detailed logging

**3. "Directory already exists"**
- Use `--overwrite` to force overwrite
- Or manually remove existing directories

**4. Memory issues with large MD trajectories**
- Use `--stride` to sample frames
- Use `--max-frames` to limit processing
- Process in smaller batches

### Verbose Logging

Enable detailed logging for debugging:

```bash
s_make -T input.xyz --base out --verbose
s_run --base out --verbose
s_store --base out --db results.db --verbose
s_gpumd --base out --db input.db --verbose
```


## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For issues and questions:
- Check the troubleshooting section
- Enable verbose logging for debugging
- Open an issue on GitHub

