import util.config.config_util as cu
import util.linkage_agent.linkage_agent_util as lau


def test_match():
    print("\nStarting test...")
    config = cu.get_config("test-data/defaults/config.json")
    lau.validate(config)
    lau.match(config)
    print("Done.")

