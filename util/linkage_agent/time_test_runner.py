import util.file.file_util as fu
import util.config.config_util as cu
import util.json.json_util as ju


root_dir = "test-data/envs/time-test-no-households"


def run_time_test():
    print("Starting tests...")
    # get the configuration
    config = cu.get_config(root_dir + "/config.json")
    print("------------------------------------")
    print("Configuration")
    print("Config" + ju.pretty_print(config.config_json))
    print("------------------------------------")
    # get the output dir and the test dirs
    outbox_root = config.output_folder
    patient_dirs = fu.get_dirs(fu.get_file_name(root_dir + "/patients"))
    print("Got " + str(len(patient_dirs)) + " test directories:")
    for dir_name in patient_dirs:
        print("\t" + dir_name)
    print("Output Dir:")
    print(outbox_root)
    print("------------------------------------")
    print("")
    print("")
    for dir_name in patient_dirs:
        print("Starting test for " + dir_name)
    print("Done.")


if __name__ == "__main__":
    run_time_test()


