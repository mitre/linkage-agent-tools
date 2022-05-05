import util.config.config_util as cu
import util.file.file_util as fu
import util.linkage_agent.time_test_runner as ttr


def test_time_test_runner():
    root_dir = "test-data/envs/time-test-no-households"
    config = cu.get_config(root_dir + "/config.json")
    root_dir_name = fu.get_file_name(root_dir)
    patient_dirs = fu.get_dirs(fu.get_file_name(root_dir + "/patients"))
    ttr.run_time_test(root_dir_name, patient_dirs, config)
