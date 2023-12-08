import os, json, shutil, subprocess, sys, platform
from PySide6.QtWidgets import (
        QDialog, QVBoxLayout, QLabel, QApplication, QVBoxLayout, QHBoxLayout, QPushButton,
        )
from . import shot_utils, p4utils
from .utils import get_project_root
from .interface_utils import quick_dialog
import pkg_resources

def get_pkg_asset_path(path):
    PACKAGE_NAME = "cog_vfx"
    asset_path = pkg_resources.resource_filename(PACKAGE_NAME, path)
    return asset_path

def new_shot(qt_parent, shot_name, shot_data = None):
    print(f"creating new shot: {shot_name}")
    # find paths
    root_path = get_project_root()
    shots_path = os.path.join(root_path, "shots")
    template_path = os.path.join(shots_path, "_template")
    dest_root = os.path.join(shots_path, shot_name)

    # check paths
    if(os.path.exists(dest_root)):
        print(f"ERROR: file {dest_root} already exists, cancelling shot creation")
        quick_dialog(qt_parent, f"ERROR: file {dest_root} already exists, cancelling shot creation", "Can't Create Shot")
        return None

    print(f"using template {template_path}, copying to {dest_root}")
    copy_template(shot_name, template_path, dest_root)
    if(shot_data):
        make_shot_json(os.path.join(dest_root, "shot_data.json"), shot_data)


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

def make_shot_json(save_path, shot_data):
    # json dump
    json_save_path = save_path 
    json_data = json.dumps(shot_data, indent=4)
    with open(json_save_path, "w") as file:
        file.write(json_data)

def edit_shot_json(save_path, edit_shot_data):
    json_save_path = save_path 

    with open(json_save_path, "r") as file:
        shot_data = json.load(file)
    shot_data.update(edit_shot_data)

    json_data = json.dumps(shot_data, indent=4)
    with open(json_save_path, "w") as file:
        file.write(json_data)

    # return updated shot data
    return shot_data

def edit_asset_json(save_path, edit_shot_data):
    json_save_path = save_path 

    with open(json_save_path, "r") as file:
        asset_data = json.load(file)
    asset_data.update(edit_shot_data)

    json_data = json.dumps(asset_data, indent=4)
    with open(json_save_path, "w") as file:
        file.write(json_data)

    # return updated asset data
    return asset_data

def move_shot(qt_parent, source_shot_name, dest_shot_name):
    # find paths
    root_path = get_project_root()
    shots_path = os.path.join(root_path, "shots")
    source_dir = os.path.join(shots_path, source_shot_name)
    dest_dir = os.path.join(shots_path, dest_shot_name)
    print(f"moving {source_dir} to {dest_dir}")
    if(not os.path.exists(source_dir)):
        print(f"ERROR: source dir: {source_dir} not found")
        return
    if(os.path.exists(dest_dir)):
        quick_dialog(qt_parent, f"{dest_shot_name} already exists.\nCancelling shot move.", "Can't move Shot")
        return
    print("TARGET DIR", source_dir)
    print("DEST DIR", dest_dir)

    shutil.move(source_dir, dest_dir)

    return dest_dir

# -- update
class UpdateDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Update")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(QLabel("New update available, update now?"))
        
        # buttons
        button_layout = QHBoxLayout()
        self.layout.addLayout(button_layout)
        update_button = QPushButton("Update")
        update_button.clicked.connect(lambda: self.make_selection(1))
        button_layout.addWidget(update_button)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(lambda: self.make_selection(0))
        button_layout.addWidget(cancel_button)

    def make_selection(self, selection):
        self.update_selection = selection
        self.close()

class UpdateFinishedDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Update")
        dialog_layout = QVBoxLayout()
        self.setLayout(dialog_layout)
        dialog_layout.addWidget(QLabel("Starting update\nPress 'ok' to continue"))
        ok_button = QPushButton("Ok")
        ok_button.clicked.connect(lambda: self.close())
        dialog_layout.addWidget(ok_button)
        self.exec()

def software_update(app):
    dist_dir = "//finalProjectDepot/finalProjectStream/pipeline/packages/2AM/cog/dist/"
    dist_file_depot = os.path.join(dist_dir, "cog_vfx-0.1.tar.gz")
    file_info = p4utils.get_file_info(dist_file_depot)[0]
    # check if update is needed
    if(not check_updatable(file_info=file_info)):
        return
    dist_file = file_info["client_file"]

    # Ask user
    update_dialog = UpdateDialog()
    update_dialog.exec()
    if(not update_dialog.update_selection):
        return

    print("Installing update")
    # fetch latest revision
    p4utils.get_latest(dist_file_depot)

    update_finished_dialog = UpdateFinishedDialog()
    updater_script_path = p4utils.get_file_info("//finalProjectDepot/finalProjectStream/pipeline/_scripts/updater.py")[0]["client_file"]
    # updater_script_path = os.path.join(os.getenv("film_root"), os.path.normpath("/pipeline/_scripts/updater.py"))
    print("dist file", dist_file)
    main_script = sys.argv[0]
    if platform.system() == 'Windows':
        main_script+=".exe"
    subprocess.Popen([sys.executable, updater_script_path, dist_file, main_script])
    app.quit()
    exit()
    # subprocess.check_call([f'"{sys.executable}"', "-m", "pip", "install", f'"{dist_file}"'])
    # os.execv(sys.executable, ['python'] + sys.argv)


def check_updatable(dist_file=None, file_info=None):
    # if(not os.path.exists(dist_file)):
    #     raise Exception("Distribution file does not exist: "+dist_file)
    if(not file_info):
        file_info = p4utils.get_file_info(dist_file)[0]

    if(file_info["have_rev"] != file_info["head_rev"]):
        print("Package version out of date, getting latest revision")
        return True


    else:
        return False



if __name__ == "__main__":
    pass
