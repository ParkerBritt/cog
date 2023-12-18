import os, json
# import QT
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QStackedLayout, QListWidget, QSizePolicy, QMenu, QSplitter, QListWidgetItem, QSpinBox, QTextEdit, QDialog, QScrollArea, QProgressBar, QLineEdit, QSpacerItem, QTreeWidget, QTreeWidgetItem, QButtonGroup
from PySide6.QtGui import QIcon, QFont, QPixmap
from PySide6.QtCore import QSize, Qt, QThread, Signal
import pkg_resources

# import utilities
from ..utils import shot_utils, file_utils, utils, interface_utils
from ..utils.houdini_wrapper import launch_houdini, launch_hython
from ..utils.interface_utils import quick_dialog
from ..utils.file_utils import get_pkg_asset_path
from ..dialogs.new_element_dialog import NewElementDialog

# import panels
from ..panels import AbstractInfoPanel, AbstractListPanel, ShotListPanel, ShotInfoPanel, ShotWorkspaceView

style_sheet = interface_utils.get_style_sheet()








class NewShotDialog(NewElementDialog):
    def __init__(self, shot_list, edit=False, parent=None):
        super().__init__(self, shot_list, edit, parent)

    # ----- SIGNALS ------- 

    def on_ok_pressed(self):
        print("ok_pressed")
        # get shot data in variables from widgets
        self.finished_status = 0

        start_frame = self.select_start_frame.value()
        end_frame = self.select_end_frame.value()
        shot_num = self.select_shot_num.value()
        res_width = self.select_res_width.value()
        res_height = self.select_res_height.value()
        fps = self.select_fps.value()
        shot_desc = self.shot_description_box.toPlainText()

        # format shot data in dictionary
        self.new_shot_data = {
            "shot_num":shot_num,
            "start_frame":start_frame,
            "end_frame":end_frame,
            "description":shot_desc,
            "res_width":res_width,
            "res_height":res_height,
            "fps":fps
        }


        self.shot_file_name = "SH"+str(shot_num).zfill(4)
        self.close()

    def on_cancel_pressed(self):
        self.finished_status = 1
        self.close()

# class NewShotDialog(NewElementDialog):
#     def __init__(self, element_list, edit=False, element_name="element", parent=None):
#         super().__init__():

# ------------- SHOT PAGE -----------------



class ShotPage(QWidget):
    def __init__(self, parent=None):
        super(ShotPage, self).__init__(parent)
        # make font
        self.header_font = QFont()
        self.header_font.setPointSize(12)

        self.set_shots()
        self.create_shot_page()

    def set_shots(self):
        self.shots = shot_utils.get_shots()


    def create_shot_page(self):
        # Create content for Tab 1
        self.shot_page_layout = QHBoxLayout(self)

        # Layout
        self.shot_list_layout_parent = QVBoxLayout()
        self.shot_page_layout.addLayout(self.shot_list_layout_parent)
        self.shot_side_layout = QVBoxLayout()
        self.shot_page_layout.addLayout(self.shot_side_layout)
        self.files_layout = QVBoxLayout()
        self.shot_page_layout.addLayout(self.files_layout)
        # self.role_list_layout_parent = QVBoxLayout()
        # self.files_layout.addLayout(self.role_list_layout_parent)
        self.file_tree_layout_parent = QVBoxLayout()
        self.files_layout.addLayout(self.file_tree_layout_parent)

        self.create_shot_side_panel()
        self.create_shot_list_panel()
        self.create_file_tree_panel()
        # connect widgets so selecting a new shot updates the tree
        self.shot_list_widget.tree_widget = self.workspace_files

    def create_file_tree_panel(self):
        self.workspace_files=ShotWorkspaceView(self.shot_list_widget)
        self.file_tree_layout_parent.addWidget(self.workspace_files)
        self.workspace_files.populate_file_tree()

    def create_shot_list_panel(self):
        self.shot_list_widget = ShotListPanel(info_widget=self.shot_side_widget, parent=self)
        self.shot_list_layout_parent.addWidget(self.shot_list_widget)
        self.shot_list = self.shot_list_widget.element_list

    def create_shot_side_panel(self):
        self.shot_side_widget = ShotInfoPanel()

        # Create a content widget and a layout for it
        self.shot_page_layout.addWidget(self.shot_side_widget)

    def on_shot_edit(self):
        selected_items = self.shot_list.selectedItems()
        if(len(selected_items)==0):
            print("no shot selected for editing")
            return

        selected_shot_data = selected_items[0].data(role_mapping["shot_data"])

        self.edit_shot_window = NewShotInterface(self, self.shot_list, edit=True, shot_data=selected_shot_data)
        self.edit_shot_window.finished.connect(self.on_shot_edit_finished)
        self.edit_shot_window.exec()

    def on_shot_edit_finished(self):
        # make sure user confirmed edit by pressing ok
        finished_stats = self.edit_shot_window.finished_status
        if(finished_stats != 0):
            return

        # setup variables
        selected_shot = self.shot_list.selectedItems()[0]
        old_shot_data = selected_shot.data(role_mapping["shot_data"])
        print("OLD SHOT DATA", old_shot_data)
        shot_dir = old_shot_data["dir"]
        shot_name = old_shot_data["file_name"]
        edit_shot_data = self.edit_shot_window.new_shot_data



        # move shot
        if(not "shot_num" in old_shot_data or old_shot_data["shot_num"] != edit_shot_data["shot_num"]):
            print("\n\nSHOT NUMBER CHANGED!!!!")
            # print(f"old_shot_data: {old_shot_data} \nnew_shot_data: {new_shot_data}")
            dest_shot_name = "SH"+str(edit_shot_data["shot_num"]).zfill(4)
            dest_dir = file_utils.move_shot(self, shot_name, dest_shot_name)
            # check if move was successful
            if(not dest_dir):
                edit_shot_data.pop("shot_num")
                return

            # reformat list widget
            shot_dir = dest_dir
            shot_name = os.path.basename(dest_dir)
            new_shot_data = shot_utils.get_shots(shot_name)[0]
            selected_shot.setText("Shot " + new_shot_data["formatted_name"])

        # edit json
        shot_file_name = os.path.join(shot_dir, "shot_data.json")
        new_shot_data = file_utils.edit_shot_json(shot_file_name, edit_shot_data)
        new_shot_data = shot_utils.get_shots(shot_name)[0]

        # update list item data
        print("SETTING NEW SHOT DATA", new_shot_data)
        if(new_shot_data!=0):
            selected_shot.setData(role_mapping["shot_data"], new_shot_data)
        else:
            print("can't find shot")

        # update info pannel
        self.update_shot_info()
        print("edit finished")

    def on_shot_add_finished(self):
        finished_stats = self.new_shot.finished_status
        if(finished_stats != 0):
            return
        new_shot_data = self.new_shot.new_shot_data

        shot_file_name = self.new_shot.shot_file_name
        print("creating shot", shot_file_name)
        file_utils.new_shot(self, shot_file_name, new_shot_data)

        self.populate_shot_list()



            
