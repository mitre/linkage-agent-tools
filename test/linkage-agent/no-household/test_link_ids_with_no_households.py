import util.config.config_util as cu
import util.linkage_agent.linkage_agent_util as lau


def test_match():
    print("\nStarting test...")
    config = cu.get_config("test/linkage-agent/no-household/config-no-households.json")
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
    print("Doing drop...")
    lau.drop(config)
    print("Done.")

