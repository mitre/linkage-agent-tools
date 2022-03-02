import util.config.config_util as cu
import util.linkage_agent.linkage_agent_util as lau


def run_full_linkage_test(local_config_file):
    print("\nStarting test...")
    config = cu.get_config(local_config_file)
    print("Doing drop...")
    lau.drop(config)
    print("Doing validation...")
    lau.validate(config)
    print("Doing match...")
    lau.match(config)
    print("Doing link_id...")
    lau.link_id(config)
    print("Doing data_owner_ids")
    lau.data_owner_ids(config)
    # No drop done at the end so we can look at the data after the run if we need to
    print("Done.")
