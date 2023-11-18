import json

file_path = "/home/parker/Perforce/y3-film/shots/SH0080/shot_data.json"

with open(file_path, "r") as file:
    data = json.load(file)

print(data["test_key"])
