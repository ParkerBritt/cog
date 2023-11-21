import os
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QStackedLayout, QListWidget, QSizePolicy, QMenu, QSplitter
from PySide6.QtGui import QIcon, QFont, QPixmap
from PySide6.QtCore import QSize, Qt
import pkg_resources
from . import shot_utils, utils
from .shot_page import ShotPage





class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        #stylesheet
        self.setStyleSheet(utils.get_style_sheet())

        self.resize(1200,600)
        self.initUI()
        self.setWindowTitle("Cog Manager")
        self.project_root = utils.get_project_root()

    def initUI(self):
        icon_path = utils.get_asset_path('assets/icons/main_icon.png')
        print("icon_path", icon_path)
        self.setWindowIcon(QIcon(icon_path))
        # Main layout
        self.layout = QHBoxLayout(self)

        # Sidebar layout for tab buttons
        self.sidebar_layout = QVBoxLayout()
        
        # Stacked layout for switching between central layouts
        self.central_stack = QStackedLayout()

        # Add sidebar and central stacked layout to main layout
        self.layout.addLayout(self.sidebar_layout)
        self.layout.addLayout(self.central_stack)

        # Create tabs and corresponding content
        self.create_tab("  Shots", 0,
                        utils.get_asset_path('assets/icons/shot_white.png'))
        self.create_tab("  Assets", 1,
                        utils.get_asset_path('assets/icons/sculpture_white.png'))
        # button padding
        self.sidebar_layout.addStretch()

        # new 
        self.shot_page_widget = ShotPage()

        # create central pages
        # self.create_shot_page()
        self.create_asset_page()


        # Add content widgets to the stacked layout
        self.central_stack.addWidget(self.shot_page_widget)
        self.central_stack.addWidget(self.asset_page_widget)

    def create_tab(self, name, index, icon_path):

        # set up button
        button = QPushButton(name)

        # button icon
        button.setIcon(QIcon(icon_path))
        button.setIconSize(QSize(35,35))

        button.setStyleSheet(
            """QPushButton {
                padding: 10px;
                border-radius: 15px;
            }
            QPushButton::text {
                padding-left: 10px;
            }
        """)

        font = QFont()
        font.setPointSize(12)
        button.setFont(font)

        #button size
        button.setMinimumSize(130, 50)
        button.setMaximumSize(230, 80)
        button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)


        button.clicked.connect(lambda: self.central_stack.setCurrentIndex(index))

        self.sidebar_layout.addWidget(button)



    def create_asset_page(self):
        # Create content for Tab 2
        self.asset_page_widget = QWidget()
        self.asset_page_layout = QVBoxLayout(self.asset_page_widget)

        self.asset_page_label = QLabel("Assets")
        self.asset_page_layout.addWidget(self.asset_page_label)



if __name__ == '__main__':
    app = QApplication([])
    mainWin = MainWindow()
    mainWin.show()
    app.exec()
