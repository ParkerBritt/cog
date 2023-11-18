from .utils import get_project_root
import os, json

def get_shots():
    project_root = get_project_root()
    shots_path = os.path.join(project_root, "shots")
    shot_dirs = os.listdir(shots_path)
    shot_dirs.sort()
    shots = []

    for i, shot_base_name in enumerate(shot_dirs):
        # ignore files starting with underscores '_'
        if(shot_base_name.startswith("_")):
           continue

        shot_dir = os.path.join(shots_path, shot_base_name)
        current_shot = {}
        current_shot.update({
            "name":shot_base_name,
            "dir":shot_dir,
            "formatted_name":"Shot " +shot_base_name.split("SH")[1],
        })

        # get json data
        json_path = os.path.join(shot_dir, "shot_data.json")
        if os.path.exists(json_path):
            with open(json_path, "r") as file:
                try:
                    json_data = json.load(file)
                    current_shot.update(json_data)
                except json.JSONDecodeError as e:
                    print(f"Error reading JSON file {json_path}: {e}")
                except Exception as e:
                    print(f"An unexpected error occurred: {e}")
        else:
            print(f"File not found: {json_path}")

        shots.append(current_shot)

            
    return shots

