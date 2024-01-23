# from PySide6.QtGui import QIcon, QFont
import os

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialog, QLabel, QVBoxLayout

from .file_utils import get_pkg_asset_path

# -- misc small utils --
role_mapping = {
    "item_data": Qt.UserRole + 1,
}


def get_icon(file_name):
    icons_dir_path = "assets/icons"
    icon_path = get_pkg_asset_path(os.path.join(icons_dir_path, file_name))
    if not os.path.exists(icon_path):
        print("Icon doesn't exit: ", icon_path)
        return QIcon()
    return QIcon(icon_path)


def set_list_widget_data(list_item, data):
    # print("ROLE MAPPING", role_mapping)
    list_item.setData(role_mapping["item_data"], data)


def get_list_widget_data(list_widget=None, item=None):
    if item == None:
        if list_widget == None:
            raise Exception("get_list_widget function called without list or list item")
        selected_items = list_widget.selectedItems()
        # print("selected items", selected_items)
        if len(selected_items) == 0:
            print("list is empty")
            return None
        selected_item = selected_items[0]
    else:
        selected_item = item
    sel_object_data = selected_item.data(role_mapping["item_data"])
    return sel_object_data


def get_style_sheet():
    from .file_utils import get_pkg_asset_path

    stylesheet_path = get_pkg_asset_path("assets/style/style.css")
    with open(stylesheet_path, "r") as file:
        stylesheet = file.read()

    return stylesheet


def quick_dialog(self=None, dialog_text=" ", title=" "):
    dialog = QDialog(self)
    dialog.setWindowTitle(title)
    dialog_layout = QVBoxLayout()
    dialog.setLayout(dialog_layout)
    dialog_layout.addWidget(QLabel(dialog_text))
    dialog.exec()
