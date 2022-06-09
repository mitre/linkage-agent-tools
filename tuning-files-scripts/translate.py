# File may be deprecated - need to check with Andy

import csv

systems = ["a", "b", "c"]
root_path = "/Users/andrewg/projects/anonlink-multiparty/data/siblings/system-{}.csv"

systems_raw_data = {}

for s in systems:
    with open(root_path.format(s)) as csvfile:
        reader = csv.DictReader(csvfile)
        systems_raw_data[s] = list(reader)

with open("network_ids.csv", newline="") as source:
    with open("translated_network_ids.csv", "w", newline="") as output:
        reader = csv.DictReader(source)
        writer = csv.writer(output)
        header = ["network_id"]
        header.extend(systems)
        writer.writerow(header)
        for row in reader:
            translated_row = []
            translated_row.append(row["network_id"])
            for s in systems:
                id = row[s]
                if id == "":
                    translated_row.append("")
                else:
                    translated_row.append(systems_raw_data[s][int(id)]["record_id"])
            writer.writerow(translated_row)
