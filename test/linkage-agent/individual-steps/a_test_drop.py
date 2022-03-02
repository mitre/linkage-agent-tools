import util.config.config_util as cu
import util.linkage_agent.linkage_agent_util as lau


def test_drop():
    print("\nStarting test...")
    config = cu.get_config("test-data/defaults/config.json")
    lau.drop(config)
    print("Done.")

