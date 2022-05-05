import json
import argparse
from pathlib import Path

import util.file.file_util as fu
import util.config.config_util as cu
import util.json.json_util as ju
import util.linkage_agent.linkage_agent_util as lau
import os
import time


def run_time_test(root_dir_name, patient_dirs, config):
    print("Starting tests...")
    print("------------------------------------")
    print("Configuration:")
    print(ju.pretty_print(config.config_json))
    print("------------------------------------")
    # get the output dir and the test dirs
    outbox_root = config.output_folder
    print("Got " + str(len(patient_dirs)) + " test directories:")
    for dir_name in patient_dirs:
        print("\t" + dir_name)
    print("Root dir:")
    print(root_dir_name)
    print("Output Dir:")
    print(outbox_root)
    print("------------------------------------")
    print("")
    print("")
    # crate the dir to write intermediate results
    time_test_result_dir = Path(root_dir_name, "time-test-results")
    fu.mkdirs(time_test_result_dir)
    msg = ""
    for dir_name in patient_dirs:
        # get the directories for this run
        print("------------------------------------")
        print("Starting test for " + dir_name)
        infile_dir_name = os.path.split(dir_name)[-1]
        output_dir_name = infile_dir_name + "-output"
        output_dir = Path(root_dir_name, "output/" + output_dir_name)
        print("Input dir name is: " + infile_dir_name)
        print("Out dir name is:   " + output_dir_name)
        print("Input dir is:      " + str(dir_name))
        print("Out dir is         " + str(output_dir))
        # update the config file
        print(str(json.dumps(config.config_json)))
        data = json.loads(str(json.dumps(config.config_json)))
        data["inbox_folder"] = str(dir_name)
        data["matching_results_folder"] = str(output_dir)
        data["output_folder"] = str(output_dir)
        config_str = ju.get_str(data)
        current_config = cu.get_config_from_string(config_str)
        fu.mkdirs(current_config.matching_results_folder)
        fu.mkdirs(current_config.output_folder)
        print("Exists:")
        print(
            "matching_folder: "
            + str(fu.exists(config.matching_results_folder))
            + "\t"
            + config.matching_results_folder
        )
        print(
            "output_folder:   "
            + str(fu.exists(config.output_folder))
            + "\t"
            + config.output_folder
        )
        print("Config:\n" + ju.pretty_print(current_config.config_json))
        start = time.time()
        lau.generate_link_ids(current_config)
        end = time.time()
        elapsed = end - start
        msg = msg + str(elapsed) + "," + infile_dir_name + "\n"
        print(msg)
        time_test_result_file = Path(
            time_test_result_dir, "time-test-results-" + infile_dir_name + ".txt"
        )
        print("Writing results to: " + str(time_test_result_file))
        fu.write_string_to_file(msg, str(time_test_result_file))
        print("Done writing file")
    # done
    print("")
    print("")
    print("Final measurements:")
    print(msg)
    print("Writing results to: " + str(time_test_result_file))
    time_test_result_file = Path(time_test_result_dir, "time-test-results-FINAL.txt")
    fu.write_string_to_file(msg, str(time_test_result_file))
    print("Done writing file")
    print("")
    print("")
    print("Done.")
