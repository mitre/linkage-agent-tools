import util.linkage_agent.time_test_runner
import argparse

def run_test(root_dir):
    print("Running...")


if __name__ == "__main__":
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
