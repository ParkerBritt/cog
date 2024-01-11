import os

from .....utils import (
    add_shot_file_data,
    edit_shot_json,
    get_list_widget_data,
    get_shots,
    move_shot,
    new_shot,
    set_list_widget_data,
)
from ...abstract_list_panel.dialogs.new_element_dialog import NewElementDialog


class NewShotDialog(NewElementDialog):
    def __init__(self, element_list, edit=False, info_widget=None):
        super().__init__(element_list, edit, "shot", info_widget=info_widget)
        self.add_fields()

    def add_fields(self):
        shot_data = get_list_widget_data(self.element_list)
        if shot_data == 1:
            print("ERROR: cannot edit empty shot list")
            return
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
        old_shot_data = get_list_widget_data(self.element_list)
        if old_shot_data == 1:
            print("ERROR: cannot edit empty shot list")
            return
        print("OLD SHOT DATA", old_shot_data)
        shot_dir = old_shot_data["dir"]
        shot_name = old_shot_data["file_name"]
        edit_shot_data = self.new_element_data
        selected_shot = self.element_list.selectedItems()[0]

        # move shot
        if not "shot_num" in old_shot_data or int(old_shot_data["shot_num"]) != int(
            edit_shot_data["shot_num"]
        ):
            print("\n\nSHOT NUMBER CHANGED")
            print(
                "previous shot number:",
                old_shot_data["shot_num"],
                type(old_shot_data["shot_num"]),
                "new shot number",
                edit_shot_data["shot_num"],
                type(edit_shot_data["shot_num"]),
            )
            # print(f"old_shot_data: {old_shot_data} \nnew_shot_data: {new_shot_data}")
            dest_shot_name = "SH" + str(edit_shot_data["shot_num"]).zfill(4)
            dest_dir = move_shot(self, shot_name, dest_shot_name)
            # check if move was successful
            if not dest_dir:
                edit_shot_data.pop("shot_num")
                return

            # reformat list widget
            shot_dir = dest_dir
            shot_name = os.path.basename(dest_dir)
            new_shot_data = get_shots(shot_name)
            if isinstance(new_shot_data, int):  # protect against failed get_shots()
                return
            else:
                new_shot_data = new_shot_data[0]
            selected_shot.setText("Shot " + new_shot_data["formatted_name"])

        # edit json
        shot_file_name = os.path.join(shot_dir, "shot_data.json")
        new_shot_data = edit_shot_json(shot_file_name, edit_shot_data)
        new_shot_data = get_shots(shot_name)
        if isinstance(new_shot_data, int):  # protect against failed get_shots()
            return
        else:
            new_shot_data = new_shot_data[0]

        # update list item data
        print("SETTING NEW SHOT DATA", new_shot_data)
        if new_shot_data != 0:
            set_list_widget_data(selected_shot, new_shot_data)
        else:
            print("can't find shot")

        # update info pannel
        if self.info_widget:
            print("\n\n\n\nUPDATING INFO PANNEL")
            self.info_widget.update_panel_info(self.element_list)
        print("edit finished")

    def on_shot_add_finished(self):
        finished_stats = self.finished_status
        if finished_stats != 0:
            return
        new_shot_data = self.new_element_data
        add_shot_file_data(new_shot_data)

        # shot_num = new_shot_data["shot_num"]
        shot_file_name = new_shot_data["file_name"]
        print("creating shot", shot_file_name)
        new_shot(self, shot_file_name, new_shot_data)
