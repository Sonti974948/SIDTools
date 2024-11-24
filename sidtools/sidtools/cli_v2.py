import argparse
import os
import shutil
from ase.io import read, write

def split_trajectories_and_setup_directories(xyz_file, base_dir, files_to_copy):
    """
    Splits an .xyz file with multiple trajectories into separate folders using ASE.

    Parameters:
    - xyz_file: str, path to the input .xyz file.
    - base_dir: str, base directory where folders for trajectories will be created.
    - files_to_copy: list of str, paths of files and folders to copy into each trajectory folder.
    """
    # Check if the input .xyz file exists
    if not os.path.exists(xyz_file):
        raise FileNotFoundError(f"Input file '{xyz_file}' not found.")
    
    # Create the base directory if it doesn't exist
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    # Read the trajectories using ASE
    try:
        trajectories = read(xyz_file, index=":")
    except Exception as e:
        raise ValueError(f"Error reading the .xyz file with ASE: {e}")

    # Process each trajectory frame
    for i, atoms in enumerate(trajectories):
        traj_dir = os.path.join(base_dir, f"trajectory_{i+1}")
        os.makedirs(traj_dir, exist_ok=True)

        # Save trajectory as init.traj
        init_traj_path = os.path.join(traj_dir, "init.traj")
        write(init_traj_path, atoms)

        # Copy additional files and directories
        for item in files_to_copy:
            if os.path.exists(item):
                destination = os.path.join(traj_dir, os.path.basename(item))
                if os.path.isdir(item):
                    shutil.copytree(item, destination, dirs_exist_ok=True)
                else:
                    shutil.copy(item, destination)
            else:
                print(f"Warning: {item} does not exist and will not be copied.")

    print(f"Processed {len(trajectories)} trajectories into separate folders.")

def main():
    """
    Command-line interface for the `s_make` tool.
    """
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

    # Call the main functionality
    split_trajectories_and_setup_directories(args.trajectory, args.base, args.files)

if __name__ == "__main__":
    main()

