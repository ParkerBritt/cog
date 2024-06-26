import json
import os
import platform
import shutil
import subprocess
import sys

import pkg_resources
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from . import p4utils


def get_pkg_asset_path(path):
    PACKAGE_NAME = "cog_vfx"
    asset_path = pkg_resources.resource_filename(PACKAGE_NAME, path)
    return asset_path


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


# -- update
class UpdateDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        from cog_vfx.utils.interface_utils import get_style_sheet

        self.setWindowTitle("Update")
        self.layout = QVBoxLayout()
        self.setStyleSheet(get_style_sheet())
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
    file_info = p4utils.get_file_info(dist_file_depot)
    print("dist file info")
    file_info = file_info[0]
    # check if update is needed
    if not check_updatable(file_info=file_info):
        return
    dist_file = file_info["client_file"]

    # Ask user
    update_dialog = UpdateDialog()
    update_dialog.exec()
    if not update_dialog.update_selection:
        return

    print("Installing update")
    # fetch latest revision
    p4utils.get_latest(dist_file_depot)

    update_finished_dialog = UpdateFinishedDialog()
    # updater_script_path = p4utils.get_file_info(
    #     "//finalProjectDepot/finalProjectStream/pipeline/_scripts/updater.py"
    # )[0]["client_file"]
    if platform.system() == "Windows":
        home_dir = os.getenv("USERPROFILE")
    else:
        home_dir = os.getenv("HOME")
    if not home_dir:
        raise Exception("Env var USERPROFILE not found")

    updater_script_path = os.path.join(home_dir, "Perforce/y3-film/pipeline/_scripts/updater.py")
    updater_script_path = os.path.normpath(updater_script_path)

    dist_file = os.path.join(home_dir, "Perforce/y3-film/pipeline/packages/2AM/cog/dist/cog_vfx-0.1.tar.gz")
    dist_file = os.path.normpath(updater_script_path)

    if not os.path.exists(updater_script_path):
        raise Exception("Cannot find update script in path:", updater_script_path)

    # updater_script_path = os.path.join(os.getenv("film_root"), os.path.normpath("/pipeline/_scripts/updater.py"))
    print("dist file", dist_file)
    main_script = sys.argv[0]
    if platform.system() == "Windows":
        main_script += ".exe"

    update_command_args = [sys.executable, updater_script_path, dist_file, main_script]
    print("Executing command", update_command_args)
    subprocess.Popen(update_command_args)
    app.quit()
    exit()
    # subprocess.check_call([f'"{sys.executable}"', "-m", "pip", "install", f'"{dist_file}"'])
    # os.execv(sys.executable, ['python'] + sys.argv)


def check_updatable(dist_file=None, file_info=None):
    # if(not os.path.exists(dist_file)):
    #     raise Exception("Distribution file does not exist: "+dist_file)
    if not file_info:
        file_info = p4utils.get_file_info(dist_file)[0]

    if not "have_rev" in file_info or not "head_rev" in file_info:
        print("Have rev or head rev not in file info:", file_info)
        return False

    if file_info["have_rev"] != file_info["head_rev"]:
        print("Package version out of date, getting latest revision")
        return True

    else:
        return False


if __name__ == "__main__":
    pass
