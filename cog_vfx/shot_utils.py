from .utils import get_project_root
import os, json

def get_shots(shot_name_filter = None):
    project_root = get_project_root()
    shots_path = os.path.join(project_root, "shots")
    shot_dirs = os.listdir(shots_path)
    shot_dirs.sort()
    shots = []

    if(shot_name_filter):
        if(shot_name_filter in shot_dirs):
            shot_dirs = [shot_dirs[shot_dirs.index(shot_name_filter)]]
        else:
            print(f"\n\nERROR: {shot_name_filter} not in {shot_dirs}")
            return 0

    for i, shot_base_name in enumerate(shot_dirs):
        # ignore files starting with underscores '_'
        if(shot_base_name.startswith("_")):
           continue

        shot_dir = os.path.join(shots_path, shot_base_name)
        current_shot = {}

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

        current_shot.update({
            # "name":shot_base_name,
            "dir":shot_dir,
            "formatted_name":shot_base_name.split("SH")[1],
            # "num":int(shot_base_name.split("SH")[1]),
        })
        if("shot_num" in current_shot):
            current_shot["file_name"] = "SH"+str(current_shot["shot_num"]).zfill(4)
        else:
            current_shot["file_name"] = shot_base_name


        shots.append(current_shot)

            
    return shots

