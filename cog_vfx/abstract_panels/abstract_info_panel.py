import os
import re

from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QFont, QIcon, QPixmap
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpacerItem,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ..utils import file_utils, fonts, interface_utils


# -- info panel --
class AbstractInfoPanel(QScrollArea):
    def __init__(self, page_controller, parent=None):
        super().__init__(parent)
        self.page_controller = page_controller
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.width = 350
        self.setMaximumWidth(self.width)
        # init vars
        self.update_data = []
        self.update_data_mapping = None
        self.style_sheet = interface_utils.get_style_sheet()
        self.fonts = fonts.get_fonts()

        # init ui
        self.connect_signals()
        self.init_ui()

    def connect_signals(self):
        self.page_controller.on_element_selection_changed.connect(
            self.update_panel_info
        )
        self.page_controller.connect_shots_updated(self.update_panel_info)

    def init_ui(self):
        self.setStyleSheet(
            """
    QScrollArea {
        border-radius: 15px;
    }
    QScrollArea > QWidget > QWidget {
        border-radius: 15px;
        background-color: #1b1e20;
    }
    QScrollArea > QWidget > QWidget:disabled {
        background-color: #1b1e20;
    }
"""
        )

        # # Create a content widget and a layout for it
        content_widget = QWidget()
        # self.shot_page_layout.addWidget(content_widget)
        self.layout = QVBoxLayout(
            content_widget
        )  # Set the layout to the content widget

        # set the content widget to the scroll area
        self.setWidget(content_widget)
        # make the content widget resizable
        self.setWidgetResizable(True)

        self.sections = []

        # title
        self.title = QLabel("Info")
        self.title.setFont(self.fonts["header"])
        self.layout.addWidget(self.title)

        # general shot data container
        self.shot_render_data_widget = QWidget()
        self.shot_render_data_widget.setStyleSheet(
            "QWidget {background-color: #2a2e32; border-radius: 15px;}"
        )

    def update_sections(self, update_data):
        for section in self.sections:
            section.update_data(update_data)

    def new_thumbnail(self, thumbnail_path=None, thumbnail_size=None):
        # thumbnail = self.new_section()
        # thumbnail.
        # thumbnail = Thumbnail(thumbnail_path, thumbnail_size)
        # self.layout.addWidget(thumbnail)

        thumbnail_section = InfoSection(self)
        thumbnail = thumbnail_section.add_thumbnail(thumbnail_path, thumbnail_size)
        return thumbnail_section, thumbnail

    def new_section(self, section_title=None):
        # section_background.hide()
        new_section = InfoSection(self, section_title)
        self.sections.append(new_section)
        return new_section

    def on_object_edit(self):
        print("on_object_edit method meant to be overloaded")

    def create_bottom_buttons(self):
        self.layout.addStretch()

        # edit button
        self.object_edit_button = QPushButton("Edit")
        self.object_edit_button.clicked.connect(self.on_object_edit)
        self.object_edit_button.setStyleSheet(self.style_sheet)
        self.layout.addWidget(self.object_edit_button)

    def update_panel_info(self):
        # setup
        # selected_items = list_widget.selectedItems()
        # if(len(selected_items)==0):
        #     return
        # selected_item = selected_items[0]
        # sel_object_data =  selected_item.data(Qt.UserRole+1)
        # sel_object_data = interface_utils.get_list_widget_data(list_widget)
        # print("SEL OBJECT LIST", sel_object_data)
        # if isinstance(sel_object_data, int):
        #     return

        # sel_object_data = get_object_data(item=selected_object)
        # print("sel_object_data", sel_object_data)

        # if data exists in selected object then pair the placeholder and the new value
        # data = self.update_data
        selected_element = self.page_controller.get_selected_element()
        print("\n\n\nSELECTED ELEMENT:", selected_element)
        print("INFO PANEL UPDATED")
        mapped_data = selected_element.get_mapped_data()
        # data key would look something like "fps" or "asset_name". Then {fps} will be replaced in the label
        # for data_key in mapped_data:
        #     # print("data key", data_key)
        #     if not data_key in sel_object_data or sel_object_data[data_key] == "":
        #         continue
        #     mapped_data.update({"{" + data_key + "}": str(sel_object_data[data_key])})

        # allows additional data to be mapped by defining the self.update_data_mapping variable
        # for example a value of {"{test}":"hello"} will update labels with {test} to the mapped value
        # if self.update_data_mapping:
        #     mapped_data.update(self.update_data_mapping)

        self.update_sections(mapped_data)


class InfoSection:
    def __init__(self, info_panel, section_title=None, parent=None):
        # section
        section_background = QWidget()
        section_background.setStyleSheet(
            "QWidget {background-color: #2a2e32; border-radius: 15px;}"
        )
        section_layout = QVBoxLayout(section_background)
        # info_panel.layout.insertWidget(info_panel.layout.count()-2, section_background)
        info_panel.layout.addWidget(section_background)

        self.width = info_panel.width
        self.section_widgets = []

        if section_title:
            # section title
            self.section_title = QLabel(section_title)
            self.section_title.setFont(info_panel.fonts["header"])
            section_layout.addWidget(self.section_title)

        self.section_background = section_background
        self.section_layout = section_layout

    def update_data(self, update_data):
        # go through each widget and replace placeholders with mapped values
        has_visible_widgets = False
        for widget in self.section_widgets:
            # handle widget widgets
            if widget["type"] == "label":
                # get widget object
                widget_object = widget["object"]
                # make sure the widget has placeholders to replace
                if not widget["has_placeholder"]:
                    widget_object.hide()
                    continue
                widget_text = widget["text"]

                found_placeholder = False
                for placeholder in widget["placeholders"]:
                    placeholder_key = placeholder.strip("{}")
                    if not placeholder_key in update_data:
                        # print("placeholder_key:", placeholder, "not in", update_data)
                        continue
                    found_placeholder = True
                    # print(
                    #     "replacing",
                    #     placeholder_key,
                    #     "with",
                    #     update_data[placeholder_key],
                    # )
                    widget_text = widget_text.replace(
                        placeholder, str(update_data[placeholder_key])
                    )
                if not found_placeholder:
                    widget_object.hide()
                    continue
                has_visible_widgets = True
                widget_object.setText(widget_text)
                widget_object.show()

        if not has_visible_widgets:
            self.section_background.hide()
        else:
            self.section_background.show()

    def add_label(self, label_text=""):
        new_label = QLabel(label_text)
        self.section_layout.addWidget(new_label)
        placeholders = re.findall(r"\{.*?\}", label_text)
        has_placeholder = len(placeholders) != 0
        label_data = {
            "object": new_label,
            "text": label_text,
            "has_placeholder": has_placeholder,
            "type": "label",
        }
        if has_placeholder:
            label_data.update({"placeholders": placeholders})
        self.section_widgets.append(label_data)
        return new_label

    def add_thumbnail(self, thumbnail_path=None, thumbnail_size=None):
        # create widget
        aspect_ratio = (16, 9)
        if thumbnail_size == None:
            width = self.width - 35
            height = width / aspect_ratio[0] * aspect_ratio[1]
            thumbnail_size = (width, height)
        thumbnail = Thumbnail(thumbnail_path, thumbnail_size)
        self.section_layout.addWidget(thumbnail)

        return thumbnail


class Thumbnail(QLabel):
    def __init__(self, thumbnail_path=None, thumbnail_size=None):
        super().__init__()

        # thumbnail size
        if thumbnail_size is None:
            thumbnail_size = (192 * 1.3, 108 * 1.3)
        self.thumbnail_size = thumbnail_size

        # set thumbnail
        if thumbnail_path:
            self.set_image(thumbnail_path)

    def set_image(self, image_path):
        # convert list widget to image path
        if isinstance(image_path, QListWidget):
            object_data = interface_utils.get_list_widget_data(image_path)
            if isinstance(object_data, int):  # check for get_list_widget_data() error
                return
            if not "dir" in object_data:
                return
            image_path = os.path.join(object_data["dir"], "thumbnail.png")

        if not os.path.exists(image_path):
            print("thumbnail path does not exist:", image_path)
        pixmap = QPixmap(image_path)
        pixmap = pixmap.scaled(
            QSize(*self.thumbnail_size), Qt.KeepAspectRatio, Qt.FastTransformation
        )
        self.setPixmap(pixmap)
