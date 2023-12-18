# general
import os
# pyside
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QButtonGroup, QPushButton, QTreeWidget, QTreeWidgetItem
from PySide6.QtGui import QIcon
# project modules
from ..utils import get_fonts, get_list_widget_data, get_style_sheet, get_pkg_asset_path

class AbstractWorkspaceView(QWidget):
    def __init__(self, list_panel):
        super().__init__()
        self.init_icons()
        self.file_tree_layout = QVBoxLayout(self)
        self.element_list = list_panel.element_list
        self.style_sheet = get_style_sheet()
        self.setStyleSheet("""
    QWidget {
        border-radius: 15px;
        background-color: #1b1e20;
    }
""")

        # fonts
        self.fonts = get_fonts()

        # Label
        self.files_page_label = QLabel("Files")
        self.files_page_label.setFont(self.fonts["header"])
        self.file_tree_layout.addWidget(self.files_page_label)

        self.role_layout = QHBoxLayout()
        self.file_tree_layout.addLayout(self.role_layout)
        self.role_button_group = QButtonGroup()
        self.init_role_buttons()

        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderLabel("")
        self.file_tree_layout.addWidget(self.file_tree)

    def init_role_buttons(self):
        print("init_role_buttons method meant to be overloaded")

    def create_role_button(self, label, role_name):
        role_button = QPushButton(label)
        role_button.setStyleSheet(self.style_sheet)
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
        tree_font=self.fonts["tree"]

        # fetch directory path
        sel_element_data = get_list_widget_data(self.element_list) 
        directory_path = sel_element_data["dir"]
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
