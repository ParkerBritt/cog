import os

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpacerItem,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ....utils import file_utils, fonts, interface_utils, shot_utils

# -- Object Selector --
# def showContextMenu(position, list_widget):
#     ContextMenu(position, list_widget)


class AbstractListPanel(QWidget):
    def __init__(
        self, tree_widget=None, info_widget=None, parent=None, object_type="object"
    ):
        super().__init__(parent)
        # assign argument variables
        self.object_type = object_type
        self.tree_widget = tree_widget
        self.info_widget = info_widget
        self.elements = []
        # self.element_data = {}
        self.fonts = fonts.get_fonts()

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
        self.element_page_label = QLabel(self.object_type.title() + "s")
        self.element_page_label.setFont(self.fonts["header"])
        self.layout.addWidget(self.element_page_label)

        # Search Bar
        self.element_search_bar = QLineEdit()
        # self.element_search_bar.setMaximumWidth(self.element_search_bar.minimumSizeHint().width())
        self.element_search_bar.setTextMargins(5, 3, 5, 3)
        self.element_search_bar.setStyleSheet("QLineEdit {border-radius: 10px;}")
        search_bar_font = QFont()
        search_bar_font.setPointSize(10)
        self.element_search_bar.setFont(search_bar_font)
        self.element_search_bar.textChanged.connect(self.on_search_changed)
        self.element_search_bar.setPlaceholderText("Search...")
        self.layout.addWidget(self.element_search_bar)
        spacer = QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Preferred)
        self.layout.addItem(spacer)

        self.element_list = QListWidget()
        self.element_list.setSortingEnabled(True)
        self.element_list.itemSelectionChanged.connect(
            self.on_element_selection_changed
        )
        self.element_list.setAlternatingRowColors(True)
        self.element_list.setIconSize(QSize(500, 50))
        self.populate_element_list()
        self.layout.addWidget(self.element_list)
        # context menu
        self.context_menu = QMenu()
        style_sheet = interface_utils.get_style_sheet()
        self.context_menu.setStyleSheet(style_sheet)
        self.element_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.element_list.customContextMenuRequested.connect(
            lambda pos: self.context_menu.exec(self.element_list.mapToGlobal(pos))
        )

        # buttons
        bottom_buttons_layout = QHBoxLayout()
        bottom_buttons_layout.addStretch()

        self.element_refresh_button = QPushButton("Refresh")
        self.element_refresh_button.clicked.connect(self.populate_element_list)
        bottom_buttons_layout.addWidget(self.element_refresh_button)

        self.new_element_button = QPushButton("+")
        self.new_element_button.setMaximumWidth(25)
        self.new_element_button.clicked.connect(self.on_element_add)
        bottom_buttons_layout.addWidget(self.new_element_button)

        self.delete_element_button = QPushButton("-")
        self.delete_element_button.setMaximumWidth(25)
        self.delete_element_button.clicked.connect(self.on_element_delete)
        bottom_buttons_layout.addWidget(self.delete_element_button)

        self.layout.addLayout(bottom_buttons_layout)

    def on_search_changed(self, search_text):
        for element_index in range(self.element_list.count()):
            element_item = self.element_list.item(element_index)
            if not search_text.lower() in element_item.text().lower():
                element_item.setHidden(True)
            else:
                element_item.setHidden(False)

    def on_element_selection_changed(self):
        if self.info_widget:
            self.info_widget.update_panel_info(self.element_list)
        if self.tree_widget:
            self.tree_widget.populate_file_tree()

    def update_element_info(self):
        pass

    def populate_element_list(self):
        # check for previous selection
        prev_selected_items = self.element_list.selectedItems()
        has_prev_selection = len(prev_selected_items) != 0
        if has_prev_selection:
            prev_selected_text = prev_selected_items[0].text()

        # clear contents
        self.element_list.clear()

        # create new elements
        self.set_elements()
        for element_data in self.elements:
            item_label = self.object_type.title() + " " + element_data["formatted_name"]
            item = QListWidgetItem(item_label, self.element_list)
            # item.setData(role_mapping["element_data"], element)
            interface_utils.set_list_widget_data(item, element_data)
            thumbnail_path = os.path.join(element_data["dir"], "thumbnail.png")
            # print("thumbnail path", thumbnail_path)
            item.setIcon(QIcon(thumbnail_path))

            if has_prev_selection and item_label == prev_selected_text:
                item.setSelected(True)

        if not has_prev_selection:
            self.element_list.setCurrentRow(0)

    def set_elements(self):
        print("set_elements method meant to be overloaded")

    def on_element_add(self):
        print("on_element_add method meant to be overloaded")

    def on_element_delete(self):
        print("element delete")
        quick_dialog(self, "Deleting elements isn't implemented yet")


class NewObjectInterface(QDialog):
    def __init__(self, parent=None, element_list=None, edit=False, element_data=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Window)
        self.setWindowTitle("New Object")
        self.resize(400, 600)
        self.element_list = element_list

        # edit mode stuff
        self.edit_mode = edit
        self.existing_element_data = element_data

        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # if(self.existing_element_data):
        #     self.fill_existing_values()

    # def fill_existing_values(self):
    #     self.fill_value(self.select_start_frame, "start_frame")
    #     self.fill_value(self.select_end_frame, "end_frame")
    #     self.fill_value(self.element_description_box, "description")
    #     self.fill_value(self.select_res_width, "res_width")
    #     self.fill_value(self.select_res_height, "res_height")
    #     self.fill_value(self.select_fps, "fps")
    #
    # def fill_value(self, widget, value):
    #     if(value in self.existing_element_data):
    #         if(isinstance(widget, QTextEdit)):
    #             widget.setPlainText(self.existing_element_data[value])
    #         elif(isinstance(widget, QSpinBox)):
    #             widget.setValue(self.existing_element_data[value])
    def create_bottom_buttons():
        # bottom buttons
        bottom_buttons_layout = QHBoxLayout()
        bottom_button_min_size = (50, 30)
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

    def on_element_add(self):
        print("on_element_add method meant to be overriden")

    def on_element_edit(self):
        print("on_element_edit method meant to be overriden")
