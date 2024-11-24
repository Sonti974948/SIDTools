import argparse
import os
from sidtools import s_make, s_run

def s_make_main():
    parser = argparse.ArgumentParser(
        description="Split an .xyz file into multiple trajectories and organize them into folders."
    )
    parser.add_argument("-T", "--trajectory", required=True, help="Path to the input .xyz file.")
    parser.add_argument("--base", required=True, help="Name of the base directory to create.")
    parser.add_argument(
        "-F", "--files", nargs="*", default=["01_submit.py", "script.sh", "src"],
        help="List of files or folders to copy into each trajectory folder. Defaults to ['01_submit.py', 'script.sh', 'src']."  
    )
    
    args = parser.parse_args()
    
    # Call the main functionality of s_make
    s_make.split_trajectories_and_setup_directories(args.trajectory, args.base, args.files)

def s_run_main():
    parser = argparse.ArgumentParser(
        description="Run 'sbatch script.sh' in all directories containing script.sh."
    )
    parser.add_argument(
        "--base", required=True, help="Path to the base directory where subdirectories contain script.sh files."
    )
    
    args = parser.parse_args()

    # Call the main functionality of s_run
    s_run.run_sbatch_in_all_directories(args.base)

def main():
    parser = argparse.ArgumentParser(
        description="Command-line interface for sidtools utilities."
    )
    subparsers = parser.add_subparsers(help="sub-command help")

    # s_make command
    s_make_parser = subparsers.add_parser('s_make', help="Split .xyz file into trajectories and organize them into folders.")
    s_make_parser.set_defaults(func=s_make_main)

    # s_run command
    s_run_parser = subparsers.add_parser('s_run', help="Run 'sbatch script.sh' in all directories containing script.sh.")
    s_run_parser.set_defaults(func=s_run_main)

    # Parse the arguments and call the appropriate function
    args = parser.parse_args()
    args.func()  # Calls the appropriate main function for s_make or s_run

if __name__ == "__main__":
    main()

