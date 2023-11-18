import os
import shutil
from . import shot_utils
from .utils import get_project_root

def new_shot(shot_name):
    print(f"creating new shot: {shot_name}")
    copy_template(shot_name)

def copy_template(shot_name):
    root_path = get_project_root()
    shot_path = os.path.join(root_path, "shots")
    template_path = os.path.join(shot_path, "_template")
    dest_root = os.path.join(shot_path, shot_name)
    print("dest_root", dest_root)

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

if __name__ == "__main__":
    new_shot("SH030")
