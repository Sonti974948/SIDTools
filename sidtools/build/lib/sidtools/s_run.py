import os
import subprocess
import argparse

def run_sbatch_in_all_directories(base_dir):
    """
    Runs 'sbatch script.sh' in all directories that contain a 'script.sh' file.

    Parameters:
    - base_dir: str, the directory where the search will start.
    """
    for root, dirs, files in os.walk(base_dir):
        if 'script.sh' in files:
            print(f"Found 'script.sh' in {root}. Running sbatch...")
            try:
                # Change directory to the one containing 'script.sh' and run sbatch
                subprocess.run(['sbatch', 'script.sh'], cwd=root, check=True)
                print(f"Successfully submitted 'script.sh' in {root}.")
            except subprocess.CalledProcessError as e:
                print(f"Error running sbatch in {root}: {e}")
            except Exception as e:
                print(f"An error occurred in {root}: {e}")

def main():
    """
    Command-line interface for the `s_run` tool.
    """
    parser = argparse.ArgumentParser(
        description="Run 'sbatch script.sh' in all directories containing script.sh."
    )
    parser.add_argument(
        "--base", required=True, help="Base directory to search for 'script.sh' and run sbatch."
    )
    
    args = parser.parse_args()

    # Run sbatch in all directories containing 'script.sh'
    run_sbatch_in_all_directories(args.base)

if __name__ == "__main__":
    main()

