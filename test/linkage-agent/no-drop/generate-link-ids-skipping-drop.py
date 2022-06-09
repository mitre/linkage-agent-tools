import util.config.config_util as cu
import util.linkage_agent.linkage_agent_util as lau

# ---
#
# This test case can be used to trouble shoot MongoDB issues.
# It basically does the link_id process  but does not delete (drop) the MongoDB records
# We running it as a main so we can watch it chug away in PyCharm
#
# ---


def run_test_match():
    print("\nStarting test...")
    config = cu.get_config("test-data/envs/perf-testing/six-the-same-1k/config.json")
    print("Doing validation...")
    lau.validate(config)
    print("Running projects...")
    lau.projects(config)
    print("Doing match...")
    lau.match(config)
    print("Doing link_id...")
    lau.link_id(config)
    print("Doing data_owner_ids")
    lau.data_owner_ids(config)
    print("Done.")


if __name__ == "__main__":
    run_test_match()
