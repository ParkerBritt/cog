import os

from ....abstract_dialogs import NewElementDialog

# abstract utilities
from ....utils import get_list_widget_data, set_list_widget_data

# local utilities
from ..utils import (
    add_shot_file_data,
    edit_shot_json,
    format_thumbnail,
    get_shots,
    move_shot,
    new_shot,
)


class NewShotDialog(NewElementDialog):
    def __init__(self, element_list, edit=False, info_widget=None, qt_parent=None):
        super().__init__(
            element_list, edit, "shot", info_widget=info_widget, qt_parent=qt_parent
        )
        self.add_fields()

    def add_fields(self):
        shot_data = get_list_widget_data(self.element_list)
        if not shot_data:
            print("ERROR: cannot edit empty shot list")
            return
        self.add_file_selector("Thumbnail", "thumbnail")
        self.add_spin_box(
            "Shot Number",
            "shot_num",
            int(shot_data["shot_num"]) + (10 if not self.edit_mode else 0),
            max_value=99999,
        )
        self.add_spin_box("FPS", "fps", 24)
        self.add_double_spin_box("Resolution", ("res_width", "res_height"), 1920, 1080)
        self.add_double_spin_box(
            "Frame Range", ("start_frame", "end_frame"), 1001, 1100
        )
        self.add_edit_box(
            "Description",
            "description",
        )

    def on_exit(self):
        if self.edit_mode:
            self.on_shot_edit_finished()
        else:
            self.on_shot_add_finished()

    def on_shot_edit_finished(self):
        # make sure user confirmed edit by pressing ok
        finished_stats = self.finished_status
        if finished_stats != 0:
            return

        # setup variables
        self.old_shot_data = get_list_widget_data(self.element_list)
        if not self.old_shot_data:
            print("ERROR: cannot edit empty shot list")
            return
        print("OLD SHOT DATA", self.old_shot_data)
        self.shot_name = self.old_shot_data["file_name"]
        self.edit_shot_data = self.new_element_data
        print("EDIT SHOT DATA", self.edit_shot_data)
        selected_shot = self.element_list.selectedItems()[0]
        self.shot_dir = self.old_shot_data["dir"]

        # move shot
        self.move_shot(selected_shot)

        # edit json
        self.shot_json_data_blacklist = ["thumbnail"]
        # filter according to blacklist
        json_shot_data = {}
        for key, value in self.new_element_data.items():
            if key in self.shot_json_data_blacklist:
                continue
            json_shot_data[key] = value
        shot_config_path = os.path.join(self.shot_dir, "shot_data.json")
        self.new_shot_data = edit_shot_json(shot_config_path, json_shot_data)
        self.new_shot_data = get_shots(self.shot_name)
        if isinstance(self.new_shot_data, int):  # protect against failed get_shots()
            return
        else:
            self.new_shot_data = self.new_shot_data[0]

        self.update_thumbnail(self.edit_shot_data)

        # update list item data
        print("SETTING NEW SHOT DATA", self.new_shot_data)
        if self.new_shot_data != 0:
            set_list_widget_data(selected_shot, self.new_shot_data)
        else:
            print("can't find shot")

        # update info pannel
        if self.info_widget:
            print("\n\n\n\nUPDATING INFO PANNEL")
            self.info_widget.update_panel_info(self.element_list)
        print("edit finished")

    def update_thumbnail(self, shot_data):
        print("setting thumbnail")
        # check if thumbnail is specified
        if not "thumbnail" in shot_data or shot_data["thumbnail"] is None:
            print("no thumbnail specified, skipping\n")
            return

        thumbnail_path = shot_data["thumbnail"]
        # check if thumbnail file exists
        if not os.path.exists(thumbnail_path):
            print("ERROR: thumbnail path does not exists:", thumbnail_path, "\n")
            return
        print("thumbnail path is valid:", thumbnail_path)

        dest_dir = os.path.join(self.shot_dir, "thumbnail.png")
        print("moving", thumbnail_path, "to", dest_dir)
        format_thumbnail(thumbnail_path, dest_dir)
        if self.qt_parent:
            selected_items = self.element_list.selectedItems()
            if len(selected_items) == 0:
                print("No item selected, can't update thumbnail")
            self.qt_parent.update_thumbnail(selected_items[0])

        print()  # new line

    def move_shot(self, selected_shot):
        if not self.old_shot_data:
            print("ERROR: cannot move shot, old_shot_data is int")
            return
        self.shot_name = self.old_shot_data["file_name"]
        if not "shot_num" in self.old_shot_data or int(
            self.old_shot_data["shot_num"]
        ) != int(self.edit_shot_data["shot_num"]):
            print("\n\nSHOT NUMBER CHANGED")
            print(
                "previous shot number:",
                self.old_shot_data["shot_num"],
                type(self.old_shot_data["shot_num"]),
                "new shot number",
                self.edit_shot_data["shot_num"],
                type(self.edit_shot_data["shot_num"]),
            )

            dest_shot_name = "SH" + str(self.edit_shot_data["shot_num"]).zfill(4)
            exit_code, dest_dir = move_shot(self, self.shot_name, dest_shot_name)
            self.shot_dir = (
                dest_dir  # update shot directory so later code can find the json file
            )
            # check if move was successful
            if not dest_dir:
                self.edit_shot_data.pop("shot_num")
                return

            # reformat list widget
            self.shot_name = os.path.basename(dest_dir)
            self.new_shot_data = get_shots(self.shot_name)
            if isinstance(
                self.new_shot_data, int
            ):  # protect against failed get_shots()
                return
            else:
                self.new_shot_data = self.new_shot_data[0]
            selected_shot.setText("Shot " + self.new_shot_data["formatted_name"])

    def on_shot_add_finished(self):
        finished_stats = self.finished_status
        if finished_stats != 0:
            return
        self.new_shot_data = self.new_element_data
        add_shot_file_data(self.new_shot_data)

        # shot_num = self.new_shot_data["shot_num"]
        shot_file_name = self.new_shot_data["file_name"]
        print("creating shot", shot_file_name)
        new_shot(self, shot_file_name, self.new_shot_data)
        # for shot list panel to read to update list
        self.new_shot_dir = self.new_shot_data["dir"]
        # self.update_thumbnail(self.new_shot_data)
