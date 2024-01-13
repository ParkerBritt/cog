# general
import os

from PySide6.QtCore import QSize, Qt, QThread
from PySide6.QtGui import QIcon

# pyside
from PySide6.QtWidgets import (
    QButtonGroup,
    QHBoxLayout,
    QLabel,
    QMenu,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

# project modules
from ....utils import (
    filter_env_vars,
    get_fonts,
    get_list_widget_data,
    get_pkg_asset_path,
    get_style_sheet,
    open_file,
)
from ....utils.p4utils import get_file_info as p4_get_file_info

role_mapping = {
    "item_data": Qt.UserRole + 1,
}
FILE_NAME_COL = 0


def set_tree_item_data(tree_item, data):
    tree_item.setData(0, role_mapping["item_data"], data)


def get_tree_item_data(item):
    item_data = item.data(0, role_mapping["item_data"])
    return item_data


class AbstractWorkspaceView(QWidget):
    def __init__(self, list_panel):
        super().__init__()
        self.init_icons()
        self.file_tree_layout = QVBoxLayout(self)
        self.element_list = list_panel.element_list
        self.style_sheet = get_style_sheet()
        self.element_type = None
        self.setStyleSheet(
            """
    QWidget {
        border-radius: 15px;
        background-color: #1b1e20;
    }
"""
        )

        # fonts
        self.fonts = get_fonts()

        # Label
        self.files_page_label = QLabel("Files")
        self.files_page_label.setFont(self.fonts["header"])
        self.files_page_label.setStyleSheet(
            "QLabel { background-color: rgba(0,0,0,0); }"
        )
        self.file_tree_layout.addWidget(self.files_page_label)

        self.role_layout = QHBoxLayout()
        self.file_tree_layout.addLayout(self.role_layout)
        self.role_button_group = QButtonGroup()

        # init file tree
        self.file_tree = QTreeWidget()
        self.file_tree.setColumnCount(0)
        self.file_tree.setHeaderLabels(["File Name"])
        self.file_tree_layout.addWidget(self.file_tree)

        self.init_role_buttons()

        # init context menu
        # self.context_menu = QMenu()
        # self.context_menu.setStyleSheet(self.style_sheet)
        # self.file_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        # self.file_tree.customContextMenuRequested.connect(
        #         lambda pos: self.context_menu.exec(self.file_tree.mapToGlobal(pos)))
        # self.context_menu.addAction("test")
        # self.context_menu.addAction("test")
        # self.context_menu.addAction("test")

    def contextMenuEvent(self, event):
        cmenu = QMenu()
        cmenu.setStyleSheet(self.style_sheet)
        selected_items = self.file_tree.selectedItems()

        if len(selected_items) > 0:
            selected_item = selected_items[0]
        else:
            return
        item_data = get_tree_item_data(selected_item)

        if item_data["is_dir"] == True:
            newAct = cmenu.addAction("New")
            opnAct = cmenu.addAction("Open")
            return

        else:
            file_type = item_data["file_type"]
            if file_type in [".mb", ".ma", ".hipnc"]:
                sel_element_data = get_list_widget_data(self.element_list)
                env_vars = filter_env_vars(sel_element_data, self.element_type)
                cmenu.addAction(
                    "Open", lambda: open_file(item_data["file_path"], env_vars)
                )
            cmenu.addAction("not_dir")
        action = cmenu.exec_(self.mapToGlobal(event.pos()))

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
        def get_icon(file_name):
            file_icons_path = "assets/icons/file_icons"
            return QIcon(get_pkg_asset_path(os.path.join(file_icons_path, file_name)))

        # icons
        self.icon_file = get_icon("file_white.png")
        self.icon_dir_full = get_icon("folder_open_white.png")
        self.icon_dir_empty = get_icon("folder_closed_white.png")
        self.file_name_icon_mapping = {
            "anim.mb": get_icon("animation_white.png"),
            "scene.hipnc": get_icon("scene_white.png"),
        }
        self.file_type_icon_mapping = {
            ".hipnc": get_icon("houdini_white.png"),
        }

    def populate_file_tree(self):
        self.file_tree.clear()

        # Font
        tree_font = self.fonts["tree"]

        # fetch directory path
        sel_element_data = get_list_widget_data(self.element_list)
        if isinstance(sel_element_data, int):  # check for get_list_widget_data() error
            return

        if sel_element_data is None:
            raise Exception("ERROR:", "no element selected")
        directory_path = sel_element_data["dir"]
        directory_path += "/" + self.selected_role
        if not os.path.exists(directory_path):
            print("ERROR: directory does not exist: " + directory_path)
            return
            # raise Exception("ERROR: directory does not exist: " + directory_path)

        # walk through files
        path_to_item = {}
        self.files = []
        for root, dirs, files in os.walk(directory_path):
            # filter top level directories
            # if(root == directory_path):
            #     dirs[:] = [d for d in dirs if d in whitelist_dirs]
            #     files[:] = [f for f in files if f in whitelist_files]

            parent_item = path_to_item.get(root, self.file_tree)

            # handle directories
            for dir_name in dirs:
                dir_item = QTreeWidgetItem(parent_item)
                dir_item.setText(FILE_NAME_COL, dir_name)
                dir_path = os.path.join(root, dir_name)
                path_to_item[dir_path] = dir_item

                # data
                item_data = {"is_dir": True}
                set_tree_item_data(dir_item, item_data)

                # font
                dir_item.setFont(FILE_NAME_COL, tree_font)
                # icons
                if len(os.listdir(dir_path)) == 0:
                    dir_item.setIcon(FILE_NAME_COL, self.icon_dir_empty)
                else:
                    dir_item.setIcon(FILE_NAME_COL, self.icon_dir_full)

            # handle files
            for file_name in files:
                file_item = QTreeWidgetItem(parent_item)
                file_item.setText(FILE_NAME_COL, file_name)
                p4_status = "None"
                file_item.setToolTip(FILE_NAME_COL, "P4: " + p4_status)
                self.files.append(file_item)

                # data
                file_type = os.path.splitext(file_name)[1]
                file_path = os.path.join(root, file_name)
                item_data = {
                    "is_dir": False,
                    "file_type": file_type,
                    "file_path": file_path,
                }
                set_tree_item_data(file_item, item_data)

                # font
                file_item.setFont(FILE_NAME_COL, tree_font)
                # icons
                if file_name.lower() in self.file_name_icon_mapping:
                    icon = self.file_name_icon_mapping[file_name.lower()]
                elif file_type in self.file_type_icon_mapping:
                    icon = self.file_type_icon_mapping[file_type]
                else:
                    icon = self.icon_file
                file_item.setIcon(FILE_NAME_COL, icon)
            # print("root:",root)
            # print("dirs:", dirs)
            # print("files:", files)
        self.populate_p4_status()

    def populate_p4_status(self):
        if hasattr(self, "populate_p4_status_thread"):
            self.populate_p4_status_thread.stop()
            self.populate_p4_status_thread.wait()
        self.populate_p4_status_thread = populate_p4_status_thread(self.files)
        self.populate_p4_status_thread.start()

        # print("file paths", file_paths)
        # for file in self.files:
        #     print("file data", get_tree_item_data(file)["file_path"])


class populate_p4_status_thread(QThread):
    def __init__(self, file_items):
        super().__init__()
        self._is_running = True
        self.file_items = file_items

    def stop(self):
        self._is_running = False

    def run(self):
        file_paths = [get_tree_item_data(file)["file_path"] for file in self.file_items]
        if not self._is_running:
            return
        file_p4_info = p4_get_file_info(file_paths)
        if not self._is_running:
            return
        print("file_paths", file_paths)
        print("p4 info", file_p4_info)
        for i, file_info in enumerate(file_p4_info):
            if not self._is_running:
                return
            self.file_items[i].setToolTip(FILE_NAME_COL, file_info["status"])
