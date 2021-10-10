import argparse
from pathlib import Path

import util.config.config_util as cu
import util.linkage_agent.time_test_runner as ttr


def run_test(root_dir_abs_path):
    config = cu.get_config_from_abs_path(root_dir_abs_path + "/config.json")
    print("---------------------------")
    print("Config:\n" + cu.get_json_pretty_printed(config))
    print("---------------------------")
    root_dir_name = root_dir_abs_path
    patient_dirs = str(Path(root_dir_abs_path, "patients"))
    print("root_dir:     " + root_dir_abs_path)
    print("patient_dirs: " + patient_dirs)
    ttr.run_time_test(root_dir_name, patient_dirs, config)


if __name__ == "__main__":
    # get the args from the cmd line
    print("Reading arguments...")
    parser = argparse.ArgumentParser(
        description="Tool for running time tests for generating LINK_IDs in the CODI PPRL process"
    )
    parser.add_argument(
        "--dir",
        help="Fully specified path to where the test files are",
    )
    args = parser.parse_args()
    print("Path: " + args.dir)
    # get the derived params
    root_dir = args.dir
    run_test(root_dir)

