from dcctools.config import Configuration


def validate():
    c = Configuration("config.json")
    if c.validate_all_present():
        return "All necessary input is present"
    else:
        return "One or more files missing from data owners"

if __name__ == "__main__":
    print(validate())