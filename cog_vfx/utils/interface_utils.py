import os
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QWidget, QHBoxLayout, QPushButton, QLineEdit, QSpacerItem, QSizePolicy, QListWidget, QListWidgetItem, QSpinBox, QTextEdit, QScrollArea
from PySide6.QtGui import QIcon, QFont
from PySide6.QtCore import QSize, Qt
from . import shot_utils, file_utils

# -- misc small utils -- 
role_mapping = {
    "item_data": Qt.UserRole + 1,
}

def set_list_widget_data(list_item, data):
    print("ROLE MAPPING", role_mapping)
    list_item.setData(role_mapping["item_data"], data)

def get_list_widget_data(list_widget, item=None):
    if(item==None):
        selected_items = list_widget.selectedItems()
        print("selected items", selected_items)
        if(len(selected_items)==0):
            return
        selected_item = selected_items[0]
    else:
        selected_item = item
    sel_object_data =  selected_item.data(role_mapping["item_data"])
    return sel_object_data

def get_style_sheet():
    stylesheet_path = file_utils.get_pkg_asset_path("assets/style/style.css")
    with open(stylesheet_path, "r") as file:
        stylesheet = file.read()

    return stylesheet

def quick_dialog(self=None, dialog_text=" ", title = " "):
    dialog = QDialog(self)
    dialog.setWindowTitle(title)
    dialog_layout = QVBoxLayout()
    dialog.setLayout(dialog_layout)
    dialog_layout.addWidget(QLabel(dialog_text))
    dialog.exec()

