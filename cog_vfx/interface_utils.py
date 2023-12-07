import os
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QWidget, QHBoxLayout, QPushButton, QLineEdit, QSpacerItem, QSizePolicy, QListWidget, QListWidgetItem, QSpinBox, QTextEdit, QScrollArea
from PySide6.QtGui import QIcon, QFont
from PySide6.QtCore import QSize, Qt
from . import shot_utils, file_utils

# -- misc small utils -- 
def data_from_list_widget(list_widget):
    selected_items = list_widget.selectedItems()
    if(len(selected_items)==0):
        return
    selected_item = selected_items[0]
    sel_object_data =  selected_item.data(Qt.UserRole+1)
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

role_mapping = {
    "object_data": Qt.UserRole + 1,
}

# -- Object Selector -- 

class ObjectSelector(QWidget):
    def __init__(self, tree_widget = None, info_widget = None, parent=None):
        super().__init__(parent)
        # assign argument variables
        self.tree_widget = tree_widget
        self.info_widget = info_widget

        # create ui
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)
        # self.setMaximumWidth(self.minimumSizeHint().width())
        self.setMinimumWidth(215)
        self.setMaximumWidth(280)
        print(" MAXIMUM SIZE:", self.minimumSizeHint().width())

        # Label
        self.object_page_label = QLabel("Objects")
        # self.object_page_label.setFont(self.header_font)
        self.layout.addWidget(self.object_page_label)

        # Search Bar
        self.object_search_bar = QLineEdit()
        # self.object_search_bar.setMaximumWidth(self.object_search_bar.minimumSizeHint().width())
        self.object_search_bar.setTextMargins(5, 1, 5, 1)
        search_bar_font = QFont()
        search_bar_font.setPointSize(12)
        self.object_search_bar.setFont(search_bar_font)
        self.object_search_bar.textChanged.connect(self.on_search_changed)
        self.layout.addWidget(self.object_search_bar)
        spacer = QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Preferred)
        self.layout.addItem(spacer)


        self.object_list = QListWidget()
        self.object_list.setSortingEnabled(True)
        self.object_list.itemSelectionChanged.connect(self.on_object_selection_changed)
        self.object_list.setAlternatingRowColors(True)
        self.object_list.setIconSize(QSize(500,50))
        self.populate_object_list()
        self.layout.addWidget(self.object_list)

        # buttons
        bottom_buttons_layout = QHBoxLayout()
        bottom_buttons_layout.addStretch()


        self.object_refresh_button = QPushButton("Refresh")
        self.object_refresh_button.clicked.connect(self.populate_object_list)
        bottom_buttons_layout.addWidget(self.object_refresh_button)

        self.new_object_button = QPushButton("+")
        self.new_object_button.setMaximumWidth(25)
        self.new_object_button.clicked.connect(self.on_object_add)
        bottom_buttons_layout.addWidget(self.new_object_button)

        self.delete_object_button = QPushButton("-")
        self.delete_object_button.setMaximumWidth(25)
        self.delete_object_button.clicked.connect(self.on_object_delete)
        bottom_buttons_layout.addWidget(self.delete_object_button)

        self.layout.addLayout(bottom_buttons_layout)

    def on_search_changed(self, search_text):
        for object_index in range(self.object_list.count()):
            object_item = self.object_list.item(object_index)
            if(not search_text.lower() in object_item.text().lower()):
                object_item.setHidden(True)
            else:
                object_item.setHidden(False)

    def on_object_selection_changed(self):
        if(self.info_widget):
            self.info_widget.update(self.object_list)
        if(self.tree_widget):
            self.populate_file_tree()

    def update_object_info():
        pass

    def populate_object_list(self):
        # check for previous selection
        prev_selected_items = self.object_list.selectedItems()
        has_prev_selection = len(prev_selected_items)!=0
        if(has_prev_selection):
            prev_selected_text = prev_selected_items[0].text()

        # clear contents
        self.object_list.clear()

        # create new objects
        self.set_objects()
        for object in self.objects:
            item_label = "Object " + object["formatted_name"]
            item = QListWidgetItem(item_label, self.object_list)
            item.setData(role_mapping["object_data"], object)
            thumbnail_path = os.path.join(object["dir"],"thumbnail.png")
            # print("thumbnail path", thumbnail_path)
            item.setIcon(QIcon(thumbnail_path))

            if(has_prev_selection and item_label == prev_selected_text):
                item.setSelected(True)
            
        if(not has_prev_selection):
            self.object_list.setCurrentRow(0)

    def set_objects(self):
        self.objects = shot_utils.get_shots()

    def on_object_add(self):
        print("method meant to be overloaded")

    def on_object_delete(self):
        print('object delete')
        quick_dialog(self, "Deleting objects isn't implemented yet")

class NewObjectInterface(QDialog):
    def __init__(self, parent=None, object_list=None, edit=False, object_data=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Window)
        self.setWindowTitle("New Object")
        self.resize(400,600)
        self.object_list = object_list

        # edit mode stuff
        self.edit_mode=edit
        self.existing_object_data = object_data

        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)


        # if(self.existing_object_data):
        #     self.fill_existing_values()

    # def fill_existing_values(self):
    #     self.fill_value(self.select_start_frame, "start_frame")
    #     self.fill_value(self.select_end_frame, "end_frame")
    #     self.fill_value(self.object_description_box, "description")
    #     self.fill_value(self.select_res_width, "res_width")
    #     self.fill_value(self.select_res_height, "res_height")
    #     self.fill_value(self.select_fps, "fps")
    #
    # def fill_value(self, widget, value):
    #     if(value in self.existing_object_data):
    #         if(isinstance(widget, QTextEdit)):
    #             widget.setPlainText(self.existing_object_data[value])
    #         elif(isinstance(widget, QSpinBox)):
    #             widget.setValue(self.existing_object_data[value])
    def create_bottom_buttons():
        # bottom buttons
        bottom_buttons_layout = QHBoxLayout()
        bottom_button_min_size = (50,30)
        ok_button = QPushButton("ok")
        cancel_button = QPushButton("cancel")
        ok_button.clicked.connect(self.on_ok_pressed)
        cancel_button.clicked.connect(self.on_cancel_pressed)
        ok_button.setMinimumSize(*bottom_button_min_size)
        cancel_button.setMinimumSize(*bottom_button_min_size)
        bottom_buttons_layout.addStretch()
        # add widgets
        bottom_buttons_layout.addWidget(ok_button)
        bottom_buttons_layout.addWidget(cancel_button)
        self.layout.addLayout(bottom_buttons_layout)

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


