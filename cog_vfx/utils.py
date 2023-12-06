import os, pkg_resources, json

def get_project_root():
    return os.getenv("film_root")




def get_assets(asset_name_filter = None):
    project_root = get_project_root()
    assets_path = os.path.join(project_root, "assets")
    asset_dirs = os.listdir(assets_path)
    asset_dirs.sort()
    assets = []

    if(asset_name_filter):
        if(asset_name_filter in asset_dirs):
            asset_dirs = [asset_dirs[asset_dirs.index(asset_name_filter)]]
        else:
            print(f"\n\nERROR: {asset_name_filter} not in {asset_dirs}")
            return 0

    # ignore files starting with underscores '_'
    for i, asset_base_name in enumerate(asset_dirs):
        if(asset_base_name.startswith("_")):
           continue

        asset_dir = os.path.join(assets_path, asset_base_name)
        current_asset = {}

        # get json data
        json_path = os.path.join(asset_dir, "asset_data.json")
        if os.path.exists(json_path):
            with open(json_path, "r") as file:
                try:
                    json_data = json.load(file)
                    current_asset.update(json_data)
                except json.JSONDecodeError as e:
                    print(f"Error reading JSON file {json_path}: {e}")
                except Exception as e:
                    print(f"An unexpected error occurred: {e}")
        else:
            print(f"File not found: {json_path}")

        current_asset.update({
            # "name":asset_base_name,
            "dir":asset_dir,
            "formatted_name":asset_base_name.replace("_"," ").title(),
            "file_name":asset_base_name,
            # "num":int(asset_base_name.split("SH")[1]),
        })
        # current_asset["file_name"] = asset_base_name


        assets.append(current_asset)

            
    return assets

