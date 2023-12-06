import os
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QWidget, QHBoxLayout, QPushButton, QLineEdit, QSpacerItem, QSizePolicy, QListWidget, QListWidgetItem, QSpinBox, QTextEdit, QScrollArea
from PySide6.QtGui import QIcon, QFont
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
        self.shot_side_secondary_layout = QVBoxLayout(content_widget)  # Set the layout to the content widget

        # set the content widget to the scroll area
        self.setWidget(content_widget)
        # make the content widget resizable
        self.setWidgetResizable(True)


        # title
        self.section_title = QLabel("Info")
        self.section_title.setFont(self.header_font)
        self.shot_side_secondary_layout.addWidget(self.section_title)



        # shot thumbnail
        self.shot_thumbnail = QLabel()
        self.shot_thumbnail_size = (192*1.3, 108*1.3)
        print(*self.shot_thumbnail_size)
        self.shot_thumbnail.setMaximumSize(*self.shot_thumbnail_size)
        self.shot_side_secondary_layout.addWidget(self.shot_thumbnail)

        # general shot data container
        self.shot_render_data_widget = QWidget()
        self.shot_render_data_widget.setStyleSheet("QWidget {background-color: #2a2e32; border-radius: 15px;}")
        shot_render_data_layout = QVBoxLayout(self.shot_render_data_widget)
        self.shot_side_secondary_layout.addWidget(self.shot_render_data_widget)
        general_shot_data_title = QLabel("Render Data")
        general_shot_data_title.setFont(self.header_font)
        shot_render_data_layout.addWidget(general_shot_data_title)

        # shot name
        self.shot_name_label = QLabel("SH")
        self.shot_name_label.hide()
        shot_render_data_layout.addWidget(self.shot_name_label)

        # frame range
        self.shot_frame_range_label = QLabel("")
        shot_render_data_layout.addWidget(self.shot_frame_range_label)

        # render res
        self.shot_render_res_label = QLabel("Resolution: 1920x1080")
        shot_render_data_layout.addWidget(self.shot_render_res_label)

        # render fps
        self.shot_render_fps_label = QLabel("FPS: 24")
        shot_render_data_layout.addWidget(self.shot_render_fps_label)

        # codec

        # date recorded

        # shot description
        self.shot_description_widget = QWidget()
        self.shot_description_widget.setStyleSheet("QWidget {background-color: #2a2e32; border-radius: 15px;}")
        shot_description_layout = QVBoxLayout(self.shot_description_widget)
        self.shot_side_secondary_layout.addWidget(self.shot_description_widget)

        description_title = QLabel("Shot Description")
        description_title.setFont(self.header_font)
        self.shot_description_title = description_title
        shot_description_layout.addWidget(self.shot_description_title)
        self.shot_description_label = QLabel("")
        shot_description_layout.addWidget(self.shot_description_label)

        self.shot_description_widget.hide()


        self.shot_side_secondary_layout.addStretch()

        self.shot_edit_button = QPushButton("Edit")
        self.shot_edit_button.clicked.connect(self.on_shot_edit)
        self.shot_edit_button.setStyleSheet(self.style_sheet)
        self.shot_side_secondary_layout.addWidget(self.shot_edit_button)

    def on_shot_edit(self):
        pass

