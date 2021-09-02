from dcctools.config import Configuration

c = Configuration("config.json")
missing_files = c.validate_all_present()
if len(missing_files):
    print("All necessary input is present")
else:
    print("One or more files missing from data owners:")
    for filename in missing_files:
        print(filename)
