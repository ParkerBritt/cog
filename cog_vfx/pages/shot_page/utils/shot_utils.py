import json
import os
import shutil

from ....utils import get_project_root


def add_shot_file_data(shot_data):
    project_root = get_project_root()
    shots_path = os.path.join(project_root, "shots")
    shot_base_name = "SH" + str(shot_data["shot_num"]).zfill(4)
    shot_full_path = os.path.join(shots_path, shot_base_name)
    shot_data.update({"file_name": shot_base_name, "dir": shot_full_path})


def get_shots(shot_name_filter=None):
    project_root = get_project_root()
    shots_path = os.path.join(project_root, "shots")
    shot_dirs = os.listdir(shots_path)
    shot_dirs.sort()
    shots = []

    if shot_name_filter:
        if shot_name_filter in shot_dirs:
            print("using filter:", shot_name_filter)
            shot_dirs = [shot_dirs[shot_dirs.index(shot_name_filter)]]
        else:
            print(f"\n\nERROR: {shot_name_filter} not in {shot_dirs}")
            return 0

    print("getting shots from: ", shot_dirs)
    for i, shot_base_name in enumerate(shot_dirs):
        # ignore files starting with underscores '_'
        if shot_base_name.startswith("_"):
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

        current_shot.update(
            {
                # "name":shot_base_name,
                "dir": shot_dir,
                "formatted_name": shot_base_name.split("SH")[1],
                # "num":int(shot_base_name.split("SH")[1]),
            }
        )
        if "shot_num" in current_shot:
            current_shot["file_name"] = "SH" + str(current_shot["shot_num"]).zfill(4)
        else:
            current_shot["file_name"] = shot_base_name

        shots.append(current_shot)

    return shots


def move_shot(qt_parent, source_shot_name, dest_shot_name):
    from ....utils.interface_utils import quick_dialog

    # find paths
    root_path = get_project_root()
    shots_path = os.path.join(root_path, "shots")
    source_dir = os.path.join(shots_path, source_shot_name)
    dest_dir = os.path.join(shots_path, dest_shot_name)
    print(f"moving {source_dir} to {dest_dir}")

    # check if source is valid
    if not os.path.exists(source_dir):
        print(f"ERROR: source dir: {source_dir} not found")
        return (2, "")  # fail code indicating the original shot directory is incorrect
    # check if destination is valid
    if os.path.exists(dest_dir):
        quick_dialog(
            qt_parent,
            f"{dest_shot_name} already exists.\nCancelling shot move.",
            "Can't move Shot",
        )
        return (1, "")  # fail code indicating shot already exists
    print("TARGET DIR", source_dir)
    print("DEST DIR", dest_dir)

    shutil.move(source_dir, dest_dir)

    return (0, dest_dir)  # success code and the directory the shot was moved to


def copy_template(template_path, dest_root):
    file_list = []

    def filter(file):
        blacklist_names = ["backup"]
        # return True
        # return True if file[:2] != "__" else False
        if file in blacklist_names:
            return False
        # if file[:2] == "__":  # ignores __prefix
        #     return False
        return True

    for root, dirs, files in os.walk(template_path):
        dirs[:] = [d for d in dirs if filter(d)]
        files = [f for f in files if filter(f)]

        for d in dirs:
            src_path = os.path.join(root, d)
            dst_path = os.path.join(dest_root, os.path.relpath(src_path, template_path))

            if not os.path.exists(dst_path):
                os.makedirs(dst_path)

        for file in files:
            src_path = os.path.join(root, file)
            dst_path = os.path.join(dest_root, os.path.relpath(src_path, template_path))
            dst_dir = os.path.dirname(dst_path)
            if not os.path.exists(dst_dir):
                os.makedirs(dst_dir)
            shutil.copy2(src_path, dst_path)

            # print("dst_path:", dst_path)


def new_shot(qt_parent, shot_name, shot_data=None):
    from ....utils.interface_utils import quick_dialog

    print(f"creating new shot: {shot_name}")
    # find paths
    root_path = get_project_root()
    shots_path = os.path.join(root_path, "shots")
    template_path = os.path.join(shots_path, "_template")
    dest_root = os.path.join(shots_path, shot_name)

    # check paths
    if os.path.exists(dest_root):
        print(f"ERROR: file {dest_root} already exists, cancelling shot creation")
        quick_dialog(
            qt_parent,
            f"ERROR: file {dest_root} already exists, cancelling shot creation",
            "Can't Create Shot",
        )
        return None

    print(f"using template {template_path}, copying to {dest_root}")
    copy_template(template_path, dest_root)
    if shot_data:
        make_shot_json(os.path.join(dest_root, "shot_data.json"), shot_data)


def make_shot_json(save_path, shot_data):
    # json dump
    json_save_path = save_path
    json_data = json.dumps(shot_data, indent=4)
    with open(json_save_path, "w") as file:
        file.write(json_data)


def edit_shot_json(save_path, edit_shot_data):
    print("\nwriting to json file:", save_path, "\njson data:", edit_shot_data, "\n")
    json_save_path = save_path

    with open(json_save_path, "r") as file:
        shot_data = json.load(file)
    shot_data.update(edit_shot_data)

    json_data = json.dumps(shot_data, indent=4)
    with open(json_save_path, "w") as file:
        file.write(json_data)

    # return updated shot data
    return shot_data


def format_thumbnail(source_file, dest_file):
    from wand.color import Color
    from wand.drawing import Drawing
    from wand.image import Image

    thumbnail = Image(filename=source_file)

    with Image(filename=source_file) as img:
        dimensions = (img.width, img.height)
    width = dimensions[0]
    height = dimensions[1]
    radius = width * height / 30000

    with Image(width=width, height=height, background=Color("transparent")) as mask:
        with Drawing() as draw:
            draw.rectangle(left=0, top=0, width=width, height=height, radius=radius)
            draw(mask)
        thumbnail.composite_channel("alpha", mask, "copy_opacity")
        thumbnail.save(filename=dest_file)
