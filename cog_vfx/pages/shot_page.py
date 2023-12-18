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
from ..panels import AbstractInfoPanel, AbstractListPanel, ShotListPanel, ShotInfoPanel

style_sheet = interface_utils.get_style_sheet()







class Old_ShotListWidget(QListWidget):
    def __init__(self, tree_widget=None, info_widget=None, parent=None):
        super().__init__(tree_widget, info_widget, parent)

    def contextMenuEvent(self, event):
        contextMenu = QMenu(self)

        # Check if right-click is on an item
        item = self.itemAt(event.pos())
        if item is not None:
            # Add "Open Shot" action only if clicked on an item
            action_open = contextMenu.addAction("Open Shot")
            action_render = contextMenu.addAction("Render Shot")
            action_delete = contextMenu.addAction("Delete Shot")
            shot_data = interface_utils.get_list_widget_data(item=item)

        action = contextMenu.exec_(self.mapToGlobal(event.pos()))


        if item is not None:
            if action == action_open:
                self.handle_action_open(shot_data)
            elif action == action_delete:
                self.handle_action_delete()
            elif action == action_render:
                self.handle_action_render(shot_data)

    def handle_action_open(self, shot_data):
        print("Opening Shot")
        scene_path = os.path.join(shot_data["dir"],"scene.hipnc")
        if(os.path.exists(scene_path)):
            launch_houdini(scene_path, shot_data, "shot")
        else:
            print("Error:", shot_data["file_name"],"has no scene.hipnc file")


    def handle_action_delete(self):
        print("Deleting Shot")

    def handle_action_render(self, shot_data):
        print("Rendering Shot")
        scene_path = os.path.join(shot_data["dir"],"scene.hipnc")
        if(os.path.exists(scene_path)):
            select_render_node = SelectRenderNodeDialog(self, scene_path, shot_data)
            # select_render_node.exec()
            print("created window")

            
            return
            # launch_hython(scene_path, shot_data, get_pkg_asset_path("husk_render.py"))
        else:
            print("Error:", shot_data["file_name"],"has no scene.hipnc file")


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
        self.init_icons()
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
        self.create_role_list_panel()
        self.create_file_tree_panel()
        self.populate_file_tree()

    def create_file_tree_panel(self):
        self.file_tree_widget = QWidget()
        self.file_tree_layout_parent.addWidget(self.file_tree_widget)
        self.file_tree_layout = QVBoxLayout(self.file_tree_widget)
        self.file_tree_widget.setStyleSheet("""
    QWidget {
        border-radius: 15px;
        background-color: #1b1e20;
    }
""")

        # Label
        self.files_page_label = QLabel("Files")
        self.files_page_label.setFont(self.header_font)
        self.file_tree_layout.addWidget(self.files_page_label)

        self.role_layout = QHBoxLayout()
        self.file_tree_layout.addLayout(self.role_layout)
        self.role_button_group = QButtonGroup()
        self.create_role_button("FX", "fx")
        anim_button = self.create_role_button("Anim", "anim")
        self.create_role_button("Comp", "comp")
        # default button
        anim_button.click()

        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderLabel("")
        self.file_tree_layout.addWidget(self.file_tree)

    def create_role_button(self, label, role_name):
        role_button = QPushButton(label)
        role_button.setStyleSheet(style_sheet)
        role_button.setCheckable(True)
        self.role_button_group.addButton(role_button)
        role_button.clicked.connect(lambda: self.set_selected_role(role_name))
        self.role_layout.addWidget(role_button)
        return role_button
    
    def set_selected_role(self, role_name):
        self.selected_role = role_name
        self.populate_file_tree()

    def init_icons(self):
        #icons
        self.icon_file = QIcon(get_pkg_asset_path("assets/icons/file_white.png"))
        self.icon_dir_full = QIcon(get_pkg_asset_path("assets/icons/folder_open_white.png"))
        self.icon_dir_empty = QIcon(get_pkg_asset_path("assets/icons/folder_closed_white.png"))
        self.file_name_icon_mapping = {"anim.mb": QIcon(get_pkg_asset_path("assets/icons/animation_white.png")),
                        "scene.hipnc": QIcon(get_pkg_asset_path("assets/icons/scene_white.png")),
                        }
        self.file_type_icon_mapping = {"hipnc": QIcon(get_pkg_asset_path("assets/icons/houdini_white.png")),
                          }

    def populate_file_tree(self):
        self.file_tree.clear()

        # Font
        tree_font = QFont()
        tree_font.setPointSize(12)

        # fetch directory path
        selected_items = self.shot_list.selectedItems()
        if(len(selected_items)==0):
            return
        selected_shot = selected_items[0]
        sel_shot_data = interface_utils.get_list_widget_data(self.shot_list_widget.element_list, item=selected_shot) 
        directory_path = sel_shot_data["dir"]
        directory_path += "/"+self.selected_role
        if(not os.path.exists(directory_path)):
            raise Exception("ERROR: directory does not exist: "+directory_path)
            return
        # whitelist_dirs = ["comp", "fx", "anim"]
        # whitelist_files = ["scene.hipnc"]

        # walk through files
        path_to_item = {}
        for (root, dirs, files) in os.walk(directory_path):
            # filter top level directories
            # if(root == directory_path):
            #     dirs[:] = [d for d in dirs if d in whitelist_dirs]
            #     files[:] = [f for f in files if f in whitelist_files]

            parent_item = path_to_item.get(root, self.file_tree)

            # handle directories
            for dir_name in dirs:
                dir_item = QTreeWidgetItem(parent_item, [dir_name])
                dir_path = os.path.join(root, dir_name)
                path_to_item[dir_path] = dir_item

                # font
                dir_item.setFont(0, tree_font)
                #icons
                if(len(os.listdir(dir_path)) == 0):
                    dir_item.setIcon(0, self.icon_dir_empty)
                else:
                    dir_item.setIcon(0, self.icon_dir_full)

            # handle files
            for file_name in files:
                file_item = QTreeWidgetItem(parent_item, [file_name])

                # font
                file_item.setFont(0, tree_font)
                # icons
                file_name_split = file_name.split(".")
                file_type = file_name_split[-1].lower() if len(file_name_split)!=0 else ""
                if file_name.lower() in self.file_name_icon_mapping:
                    icon = self.file_name_icon_mapping[file_name.lower()]
                elif(file_type in self.file_type_icon_mapping):
                    icon = self.file_type_icon_mapping[file_type]
                else:
                    icon = self.icon_file
                file_item.setIcon(0, icon)
            # print("root:",root)
            # print("dirs:", dirs)
            # print("files:", files)


    def create_role_list_panel(self):
        # Label
        self.role_list_widget = QWidget()
        self.role_list_layout = QVBoxLayout(self.role_list_widget)
        self.role_page_label = QLabel("Roles")
        self.role_page_label.setFont(self.header_font)
        self.role_list_layout.addWidget(self.role_page_label)


        # Role list
        self.role_list = QListWidget()
        self.role_list.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.role_list.setMaximumHeight(self.role_list.minimumSizeHint().height())
        self.role_list.setSortingEnabled(True)
        self.role_list.addItem("Anim")
        self.role_list.addItem("FX")
        self.role_list.addItem("Stage")
        # self.role_list.itemSelectionChanged.connect(self.update_role_info)
        self.role_list.setAlternatingRowColors(True)
        self.role_list.setIconSize(QSize(500,50))
        # self.populate_role_list()
        self.role_list_layout.addWidget(self.role_list)

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



            
