import os

import pkg_resources
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QFont, QIcon, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMenu,
    QPushButton,
    QSizePolicy,
    QSplitter,
    QStackedLayout,
    QVBoxLayout,
    QWidget,
)

from .pages import AssetPage, ConfigPage, ShotPage
from .utils import interface_utils, shot_utils, utils
from .utils.file_utils import get_pkg_asset_path


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        # stylesheet
        self.setStyleSheet(interface_utils.get_style_sheet())

        self.resize(1200, 600)
        self.initUI()
        self.setWindowTitle("Cog Manager")
        self.project_root = utils.get_project_root()

    def initUI(self):
        icon_path = get_pkg_asset_path("assets/icons/main_icon.png")
        print("icon_path", icon_path)
        self.setWindowIcon(QIcon(icon_path))
        # Main layout
        self.layout = QHBoxLayout(self)

        # Sidebar layout for tab buttons
        self.sidebar_widget = QWidget()
        self.sidebar_widget.setMaximumWidth(250)
        self.sidebar_layout = QVBoxLayout(self.sidebar_widget)
        # self.layout.addLayout(self.sidebar_layout)
        self.layout.addWidget(self.sidebar_widget)

        # Sidebar hide button
        self.tab_hide_button = QPushButton()
        self.tab_hide_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.tab_hide_button.setMaximumWidth(8)
        self.tab_hide_button.setStyleSheet("QPushButton {border-radius: 4px};")
        self.tab_hide_button.clicked.connect(self.on_tab_hide_button_clicked)
        self.tab_hide_icon_open = QIcon(
            get_pkg_asset_path("assets/icons/left_arrow_simple_white.png")
        )
        self.tab_hide_icon_closed = QIcon(
            get_pkg_asset_path("assets/icons/right_arrow_simple_white.png")
        )
        self.tab_hide_button.setIconSize(QSize(7, 7))
        self.tab_hide_button.setIcon(self.tab_hide_icon_open)
        self.layout.addWidget(self.tab_hide_button)

        # Stacked layout for switching between central layouts
        self.central_stack = QStackedLayout()

        # Add sidebar and central stacked layout to main layout
        self.layout.addLayout(self.central_stack)

        self.tab_group = QButtonGroup(self)
        self.tab_group.setExclusive(True)

        # Create tabs and corresponding content
        self.shot_tab = self.create_tab(
            "  Shots", 0, get_pkg_asset_path("assets/icons/shot_white.png")
        )
        self.asset_tab = self.create_tab(
            "  Assets", 1, get_pkg_asset_path("assets/icons/sculpture_white.png")
        )
        self.config_tab = self.create_tab(
            "  Config", 2, get_pkg_asset_path("assets/icons/description_white.png")
        )

        # button padding
        self.sidebar_layout.addStretch()

        # new
        self.shot_page_widget = ShotPage()
        self.asset_page_widget = AssetPage()
        self.config_page_widget = ConfigPage()

        # create central pages
        # self.create_shot_page()
        # self.create_asset_page()

        # Add content widgets to the stacked layout
        self.central_stack.addWidget(self.shot_page_widget)
        self.central_stack.addWidget(self.asset_page_widget)
        self.central_stack.addWidget(self.config_page_widget)

        # Default selection
        default_tab = self.shot_tab
        default_tab["button"].click()

    def on_tab_hide_button_clicked(self):
        if self.sidebar_widget.isHidden():
            self.sidebar_widget.show()
            self.tab_hide_button.setIcon(self.tab_hide_icon_open)
        else:
            self.sidebar_widget.hide()
            self.tab_hide_button.setIcon(self.tab_hide_icon_closed)

    def create_tab(self, name, index, icon_path):
        # set up button
        button = QPushButton(name)
        button.setCheckable(True)

        # button icon
        button.setIcon(QIcon(icon_path))
        button.setIconSize(QSize(35, 35))

        button.setStyleSheet(
            """QPushButton {
                padding: 10px;
                border-radius: 15px;
                text-align: left;
            }
            QPushButton::text {
                padding-left: 10px;
            }
        """
        )

        font = QFont()
        font.setPointSize(12)
        button.setFont(font)

        # button size
        button.setMinimumSize(130, 50)
        # button.setMaximumSize(230, 80)
        button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        button.clicked.connect(lambda: self.central_stack.setCurrentIndex(index))

        self.tab_group.addButton(button)
        self.sidebar_layout.addWidget(button)

        return {"button": button, "index": index}

    # def create_asset_page(self):
    #     # Create content for Tab 2
    #     self.asset_page_widget = QWidget()
    #     self.asset_page_layout = QVBoxLayout(self.asset_page_widget)
    #
    #     self.asset_page_label = QLabel("Assets")
    #     self.asset_page_layout.addWidget(self.asset_page_label)


if __name__ == "__main__":
    app = QApplication([])
    mainWin = MainWindow()
    mainWin.show()
    app.exec()
