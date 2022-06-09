import test_util.linkage.run_full_linkage_test as flt


def run_test():
    print("Starting test...")
    flt.run_full_linkage_test(
        "test-data/envs/small-no-households-with-matches/config.json"
    )
    print("Done with test")


if __name__ == "__main__":
    run_test()
