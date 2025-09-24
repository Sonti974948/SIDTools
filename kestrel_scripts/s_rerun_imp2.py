import os
import argparse
import shutil
import subprocess
import re


CONVERGENCE_MARKER = "reached required accuracy - stopping structural energy minimisation"


def find_helper_file(filename: str, helpers_dir: str | None = None) -> str:
    """Return an absolute path to `filename` by checking CWD then this script's directory.

    Raises FileNotFoundError if not found.
    """
    # If a helpers_dir is supplied, check it first
    if helpers_dir:
        helpers_candidate = os.path.abspath(os.path.join(helpers_dir, filename))
        if os.path.isfile(helpers_candidate):
            return helpers_candidate

    # Check current working directory first
    cwd_candidate = os.path.abspath(os.path.join(os.getcwd(), filename))
    if os.path.isfile(cwd_candidate):
        return cwd_candidate

    # Check the directory where this script resides
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_candidate = os.path.join(script_dir, filename)
    if os.path.isfile(script_candidate):
        return script_candidate

    raise FileNotFoundError(f"Could not find required file: {filename}")


def is_converged(outcar_path: str) -> bool:
    """Check if OUTCAR contains the required convergence marker line."""
    try:
        with open(outcar_path, "r", errors="ignore") as f:
            for line in f:
                if CONVERGENCE_MARKER in line:
                    return True
    except Exception:
        return False
    return False


def prepare_and_submit_rerun(
    source_dir: str,
    run_dir: str,
    trajectory_dir: str,
    helpers_dir: str | None = None,
    copy_to_run_dir: bool = False,
    dry_run: bool = False,
) -> None:
    """Copy rerun helpers into `run_dir` and submit via sbatch.

    - Copies `01_submit_rerun.py` and `script_rerun.sh` from either CWD or script dir
    - Copies helpers to `trajectory_dir` and (optionally) to `run_dir`
    - Submits the job from the trajectory directory: `sbatch script_rerun.sh`
    """
    # Ensure destination exists (already created by caller)
    os.makedirs(run_dir, exist_ok=True)
    os.makedirs(trajectory_dir, exist_ok=True)

    # Always (re)generate 01_submit_rerun.py tailored for this run; copy only script_rerun.sh
    dst_submit_traj = os.path.join(trajectory_dir, "01_submit_rerun.py")
    dst_script_traj = os.path.join(trajectory_dir, "script_rerun.sh")

    # Write a function-based 01_submit_rerun.py that targets the new run folder
    # Infer folder name from run_dir basename or source_dir basename? Use run_dir basename
    run_folder_basename = os.path.basename(run_dir)
    submit_contents = (
        "import os, sys\n"
        "print(os.getcwd())\n"
        "from ase import io\n"
        "from src.kul_tools import KulTools as KT\n\n"
        "def main():\n"
        f"    target = '{run_folder_basename}/CONTCAR'\n"
        "    try:\n"
        "        atoms = io.read(target)\n"
        "    except Exception as e:\n"
        "        print(f'Failed to read CONTCAR at {target}: {e}')\n"
        "        return 1\n"
        "    atoms.pbc=True\n"
        "    kt = KT(gamma_only=False,structure_type='zeo')\n"
        "    kt.set_calculation_type('opt')\n"
        "    kt.set_structure(atoms)\n"
        "    kt.set_overall_vasp_params({'gga':'RP','encut':400,'lreal':'Auto', 'algo':'fast', 'isif':3, 'kpts':(1,1,1)})\n"
        "    kt.run()\n"
        "    return 0\n\n"
        "if __name__ == '__main__':\n"
        "    raise SystemExit(main())\n"
    )
    with open(dst_submit_traj, "w", encoding="utf-8") as f:
        f.write(submit_contents)

    # Copy the sbatch script from helpers_dir or CWD/script dir
    src_script = find_helper_file("script_rerun.sh", helpers_dir=helpers_dir)
    shutil.copy2(src_script, dst_script_traj)

    if copy_to_run_dir:
        dst_submit_run = os.path.join(run_dir, "01_submit_rerun.py")
        dst_script_run = os.path.join(run_dir, "script_rerun.sh")
        # Write the same generated submit script into the run folder if requested
        with open(dst_submit_run, "w", encoding="utf-8") as f:
            f.write(submit_contents)
        shutil.copy2(src_script, dst_script_run)

    # Make sure script is executable (best-effort; harmless on Windows)
    try:
        mode_traj = os.stat(dst_script_traj).st_mode
        os.chmod(dst_script_traj, mode_traj | 0o111)
    except Exception:
        pass

    if dry_run:
        print(f"[DRY-RUN] Would submit: sbatch script_rerun.sh (cwd={trajectory_dir})")
        return

    # Submit using sbatch from the run directory
    try:
        result = subprocess.run(
            ["sbatch", "script_rerun.sh"],
            cwd=trajectory_dir,
            capture_output=True,
            text=True,
            check=False,
        )
        print(f"Submitted sbatch in {trajectory_dir} -> returncode={result.returncode}")
        if result.stdout:
            print(result.stdout.strip())
        if result.stderr:
            print(result.stderr.strip())
    except FileNotFoundError:
        print("Error: 'sbatch' command not found in PATH. Submit manually or load Slurm.")


def update_submit_io_read(trajectory_dir: str, target_subpath: str) -> None:
    """Deprecated: no-op. We now rewrite 01_submit_rerun.py per run."""
    print(f"Info: Skipping regex edit; 01_submit_rerun.py is rewritten to use {target_subpath}.")


def process(base_folder: str, subfolder_name: str, run_index: int, helpers_dir: str | None = None, dry_run: bool = False) -> None:
    """For each `trajectory_*` directory, check convergence in the given subfolder.

    If not converged, create `<subfolder_name>_run{run_index}`, copy helper scripts, and submit.
    """
    # Enumerate trajectory_* directories in the base folder numerically
    trajectory_dirs = sorted(
        [d for d in os.listdir(base_folder) if os.path.isdir(os.path.join(base_folder, d)) and d.startswith("trajectory_")],
        key=lambda x: int(x.split("_")[-1]) if x.split("_")[-1].isdigit() else float("inf"),
    )

    for folder in trajectory_dirs:
        traj_dir = os.path.join(base_folder, folder)
        source_dir = os.path.join(traj_dir, subfolder_name)
        outcar_path = os.path.join(source_dir, "OUTCAR")

        if not os.path.isdir(source_dir):
            print(f"Skipping {folder}: missing subfolder '{subfolder_name}'.")
            continue

        if not os.path.isfile(outcar_path):
            print(f"Skipping {folder}: missing OUTCAR in '{subfolder_name}'.")
            continue

        if is_converged(outcar_path):
            print(f"Converged: {folder}/{subfolder_name}")
            continue

        print(f"Not converged: {folder}/{subfolder_name} -> creating rerun folder")

        rerun_dir_name = f"{subfolder_name}_run{run_index}"
        rerun_dir = os.path.join(traj_dir, rerun_dir_name)

        rerun_exists = os.path.exists(rerun_dir)
        if rerun_exists:
            print(f"Rerun folder already exists: {folder}/{rerun_dir_name}. Will reuse it.")
        else:
            # Copy the entire calculation folder as baseline for rerun
            if dry_run:
                print(f"[DRY-RUN] Would copy folder: {source_dir} -> {rerun_dir}")
            else:
                shutil.copytree(source_dir, rerun_dir)

        # Copy helper scripts and submit job
        try:
            prepare_and_submit_rerun(
                source_dir=source_dir,
                run_dir=rerun_dir,
                trajectory_dir=traj_dir,
                helpers_dir=helpers_dir,
                copy_to_run_dir=False,
                dry_run=dry_run,
            )
        except FileNotFoundError as e:
            print(str(e))
            print(f"Skipping submission for {folder}/{rerun_dir_name} due to missing helper file(s).")
            continue

        # The generated 01_submit_rerun.py is already targeting the new run folder


def main():
    parser = argparse.ArgumentParser(description="Check VASP convergence and rerun non-converged jobs.")
    parser.add_argument("--base", required=True, help="Base folder containing trajectory_* directories")
    parser.add_argument("--folder", required=True, help="Subfolder inside trajectory folders (e.g., opt_PBE_400_111)")
    parser.add_argument("--run", required=True, type=int, help="Run index used for _run<index> suffix")
    parser.add_argument("--helpers-dir", default=None, help="Directory containing 01_submit_rerun.py and script_rerun.sh")
    parser.add_argument("--dry-run", action="store_true", help="Do not modify files or submit jobs; just print actions")

    args = parser.parse_args()

    process(args.base, args.folder, run_index=args.run, helpers_dir=args.helpers_dir, dry_run=args.dry_run)


if __name__ == "__main__":
    main()


