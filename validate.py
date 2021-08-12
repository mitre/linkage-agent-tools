from dcctools.config import Configuration

c = Configuration("config.json")
if c.validate_all_present():
    print("All necessary input is present")
else:
    print("One or more files missing from data owners")
