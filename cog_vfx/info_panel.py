import os, re
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QWidget, QHBoxLayout, QPushButton, QLineEdit, QSpacerItem, QSizePolicy, QListWidget, QListWidgetItem, QSpinBox, QTextEdit, QScrollArea
from PySide6.QtGui import QIcon, QFont, QPixmap
from PySide6.QtCore import QSize, Qt
from . import shot_utils, file_utils, interface_utils

# -- info panel --
class InfoPanel(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        # make font
        self.style_sheet = interface_utils.get_style_sheet()
        self.header_font = QFont()
        self.header_font.setPointSize(12)
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("""
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
""")


        # # Create a content widget and a layout for it
        content_widget = QWidget()
        # self.shot_page_layout.addWidget(content_widget)
        self.layout = QVBoxLayout(content_widget)  # Set the layout to the content widget

        # set the content widget to the scroll area
        self.setWidget(content_widget)
        # make the content widget resizable
        self.setWidgetResizable(True)

        self.sections = []


        # title
        self.title = QLabel("Info")
        self.title.setFont(self.header_font)
        self.layout.addWidget(self.title)

        # general shot data container
        self.shot_render_data_widget = QWidget()
        self.shot_render_data_widget.setStyleSheet("QWidget {background-color: #2a2e32; border-radius: 15px;}")

    def update_sections(self, update_data):
        for section in self.sections:
            section.update_data(update_data)

    def new_thumbnail(self, thumbnail_path=None, thumbnail_size=None):
        # thumbnail = self.new_section()
        # thumbnail.
        # thumbnail = Thumbnail(thumbnail_path, thumbnail_size)
        # self.layout.addWidget(thumbnail)

        thumbnail_section = InfoSection(self)
        thumbnail_section.add_thumbnail(thumbnail_path, thumbnail_size) 
        return thumbnail_section


    def new_section(self, section_title=None):
        # section_background.hide()
        new_section = InfoSection(self, section_title)
        self.sections.append(new_section)
        return new_section

    def on_shot_edit(self):
        pass

    def create_bottom_buttons(self):            
        self.layout.addStretch()

        # edit button
        self.shot_edit_button = QPushButton("Edit")
        self.shot_edit_button.clicked.connect(self.on_shot_edit)
        self.shot_edit_button.setStyleSheet(self.style_sheet)
        self.layout.addWidget(self.shot_edit_button)

class Thumbnail(QLabel):
    def __init__(self, thumbnail_path=None, thumbnail_size=None, parent=None):
        super().__init__(parent)
        if(thumbnail_size is None):
            thumbnail_size = (192*1.3, 108*1.3)
        # shot thumbnail
        self.label = self
        # self.layout = QVBoxLayout(self)
        #
        # self.label = QLabel()
        # self.layout.addWidget(self.label)
        self.thumbnail_size = thumbnail_size
        self.label.setMaximumSize(*self.thumbnail_size)

        if(thumbnail_path):
            self.set_thumbnail(thumbnail_path)
    
    def set_thumbnail(self, image_path):
        pixmap = QPixmap(image_path)
        pixmap = pixmap.scaled(QSize(*self.thumbnail_size), Qt.KeepAspectRatioByExpanding, Qt.FastTransformation)
        self.label.setPixmap(pixmap)


class InfoSection():
    def __init__(self, info_panel, section_title=None, parent=None):
            # section
            section_background = QWidget()
            section_background.setStyleSheet("QWidget {background-color: #2a2e32; border-radius: 15px;}")
            section_layout = QVBoxLayout(section_background)
            # info_panel.layout.insertWidget(info_panel.layout.count()-2, section_background)
            info_panel.layout.addWidget(section_background)
            
            self.labels = []

            if(section_title):
                # section title
                self.section_title = QLabel(section_title)
                self.section_title.setFont(info_panel.header_font)
                section_layout.addWidget(self.section_title)

            self.section_background = section_background
            self.section_layout = section_layout

    def update_data(self, update_data):
        # go through each label and replace placeholders with mapped values
        has_visible_labels = False
        for label in self.labels:
            # get label object
            label_object = label["object"]
            # make sure the label has placeholders to replace
            if(not label["has_placeholder"]):
                label_object.hide()
                continue
            label_text = label["text"]

            found_placeholder = False
            for placeholder in label["placeholders"]:
                if(not placeholder in update_data):
                    continue
                found_placeholder = True
                print("replacing", placeholder, "with", update_data[placeholder])
                label_text = label_text.replace(placeholder, update_data[placeholder])
            if(not found_placeholder):
                label_object.hide()
                continue
            has_visible_labels = True
            label_object.setText(label_text)
            label_object.show()
        if(not has_visible_labels):
            self.section_background.hide()
        else:
            self.section_background.show()


    def add_label(self, label_text=""):
           new_label = QLabel(label_text)
           self.section_layout.addWidget(new_label)
           placeholders = re.findall(r"\{.*?\}", label_text)
           has_placeholder = len(placeholders)!=0
           label_data = {"object":new_label,
                               "text":label_text,
                               "has_placeholder":has_placeholder,
                               }
           if has_placeholder: label_data.update({"placeholders":placeholders})
           self.labels.append(label_data)
           return new_label

    def add_thumbnail(self, thumbnail_path=None, thumbnail_size=None):
        thumbnail = self.add_label()
        if(thumbnail_size is None):
            thumbnail_size = (192*1.3, 108*1.3)
        self.thumbnail_size = thumbnail_size

        self.thumbnail = thumbnail

        if(thumbnail_path):
            self.set_thumbnail(thumbnail_path)

    def set_thumbnail(self, image_path):
        pixmap = QPixmap(image_path)
        pixmap = pixmap.scaled(QSize(*self.thumbnail_size), Qt.KeepAspectRatioByExpanding, Qt.FastTransformation)
        self.thumbnail.setPixmap(pixmap)
