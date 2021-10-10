import json
from pathlib import Path

import util.file.file_util as fu
import util.config.config_util as cu
import util.json.json_util as ju
import util.linkage_agent.linkage_agent_util as lau
import os
import time


root_dir = "test-data/envs/time-test-no-households"


def run_time_test():
    print("Starting tests...")
    # get the configuration
    config = cu.get_config(root_dir + "/config.json")
    print("------------------------------------")
    print("Configuration:")
    print(ju.pretty_print(config.config_json))
    print("------------------------------------")
    # get the output dir and the test dirs
    root_dir_name = fu.get_file_name(root_dir)
    outbox_root = config.output_folder
    patient_dirs = fu.get_dirs(fu.get_file_name(root_dir + "/patients"))
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
    msg = ""
    for dir_name in patient_dirs:
        # get the directories for this run
        print("------------------------------------")
        print("Starting test for " + dir_name)
        infile_dir_name = os.path.split(dir_name)[-1]
        output_dir_name = infile_dir_name + "-output"
        out_dir_name = infile_dir_name + "-out"
        output_dir = Path(root_dir_name, "output/" + output_dir_name)
        out_dir = Path(root_dir_name, "output/" + out_dir_name)
        print("Input dir name is:  " + infile_dir_name)
        print("Output dir name is: " + output_dir_name)
        print("Input dir is:       " + str(dir_name))
        print("Out dir is          " + str(out_dir))
        print("Output dir is:      " + str(output_dir))
        # update the config file
        print(str(json.dumps(config.config_json)))
        data = json.loads(str(json.dumps(config.config_json)))
        data["inbox_folder"] = str(dir_name)
        data["matching_results_folder"] = str(out_dir)
        data["output_folder"] = str(output_dir)
        config_str = ju.get_str(data)
        current_config = cu.get_config_from_string(config_str)
        print("Config:\n" + ju.pretty_print(current_config.config_json))
        start = time.time()
        lau.generate_link_ids(config)
        end = time.time()
        elapsed = end - start
        msg = msg + str(elapsed) + "," + infile_dir_name + "\n"
        print(msg)
    # done
    print("")
    print("")
    print("Final measurements:")
    print(msg)
    print("")
    print("")
    print("Done.")


if __name__ == "__main__":
    run_time_test()


