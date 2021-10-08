import util.config.config_util as cu
import util.json.json_util as ju


def test_get_config_json():
    print("\nStarting test")
    json_obj = cu.get_config_json_obj("test/util/config/config.json")
    print(ju.pretty_print(json_obj))
    print("Done.")


def test_get_config():
    print("\nStarting test...")
    config = cu.get_config("test/util/config/config.json")
    print(ju.pretty_print(config.config_json))
    print("Done.")

