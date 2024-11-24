import argparse
from sidtools.s_make import main as s_make_main

def main():
    parser = argparse.ArgumentParser(
        prog="s_make",
        description="Split and organize trajectories."
    )
    parser.add_argument(
        "-T", "--trajectory",
        required=True,
        help="Path to the input .xyz file."
    )
    parser.add_argument(
        "--base",
        required=True,
        help="Name of the base directory to create."
    )
    parser.add_argument(
        "-F", "--files",
        nargs="*",
        default=["01_submit.py", "script.sh", "src"],
        help="List of files or folders to copy into each trajectory folder."
    )

    args = parser.parse_args()

    # Call the main function from s_make
    s_make_main(
        trajectory=args.trajectory,
        base=args.base,
        files=args.files
    )

if __name__ == "__main__":
    main()

