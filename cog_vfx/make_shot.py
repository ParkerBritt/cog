import os, json
import shutil
from . import shot_utils
from .utils import get_project_root
from .interface_utils import quick_dialog

def new_shot(qt_parent, shot_name, shot_data = None):
    print(f"creating new shot: {shot_name}")
    # find paths
    root_path = get_project_root()
    shots_path = os.path.join(root_path, "shots")
    template_path = os.path.join(shots_path, "_template")
    dest_root = os.path.join(shots_path, shot_name)

    # check paths
    if(os.path.exists(dest_root)):
        print("ERROR: file {dest_root} already exists, cancelling shot creation")
        quick_dialog(qt_parent, "ERROR: file {dest_root} already exists, cancelling shot creation", "Can't Create Shot")
        return None

    print(f"using template {template_path}, copying to {dest_root}")
    copy_template(shot_name, template_path, dest_root)
    if(shot_data):
        make_json(os.path.join(dest_root, "shot_data.json"), shot_data)


def copy_template(shot_name, template_path, dest_root):

    file_list = []
    def filter(file):
        blacklist_names = ["backup"]
        # return True
        # return True if file[:2] != "__" else False
        if file in blacklist_names:
            return False
        if(file[:2] == "__"):
            return False
        return True

    for root, dirs, files in os.walk(template_path):
        dirs[:] = [d for d in dirs if filter(d)]
        files = [f for f in files if filter(f)]

        for d in dirs:
            src_path = os.path.join(root, d)
            dst_path = os.path.join(dest_root, os.path.relpath(src_path, template_path))

            if(not os.path.exists(dst_path)):
                os.makedirs(dst_path)

        for file in files:
            src_path = os.path.join(root, file)
            dst_path = os.path.join(dest_root, os.path.relpath(src_path, template_path))
            dst_dir = os.path.dirname(dst_path)
            if(not os.path.exists(dst_dir)):
                os.makedirs(dst_dir)
            shutil.copy2(src_path, dst_path)

            # print("dst_path:", dst_path)

def make_json(save_path, shot_data):
    # json dump
    json_save_path = save_path 
    json_data = json.dumps(shot_data, indent=4)
    with open(json_save_path, "w") as file:
        file.write(json_data)


if __name__ == "__main__":
    new_shot("SH030")
