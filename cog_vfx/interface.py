from PySide6.QtCore import QSize
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QHBoxLayout,
    QPushButton,
    QSizePolicy,
    QStackedLayout,
    QVBoxLayout,
    QWidget,
)

from .pages import AssetPage, ConfigPage, ShotPage
from .utils import interface_utils, utils
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
            "Shots", 0, get_pkg_asset_path("assets/icons/shot_white.png")
        )
        self.asset_tab = self.create_tab(
            "Assets", 1, get_pkg_asset_path("assets/icons/sculpture_white.png")
        )
        self.config_tab = self.create_tab(
            "Config", 2, get_pkg_asset_path("assets/icons/description_white.png")
        )
        self.config_tab = self.create_tab(
            "Pipeline", 2, get_pkg_asset_path("assets/icons/gear_white.png")
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
        default_tab.click()

    def on_tab_hide_button_clicked(self):
        buttons = self.tab_group.buttons()
        for button in buttons:
            button.collapse_toggle()

        # if self.sidebar_widget.isHidden():
        #     self.sidebar_widget.show()
        #     self.tab_hide_button.setIcon(self.tab_hide_icon_open)
        # else:
        #     self.sidebar_widget.hide()
        #     self.tab_hide_button.setIcon(self.tab_hide_icon_closed)

    def create_tab(self, label, page_index, icon_path):
        new_tab = SideTab(label, page_index, icon_path, self.central_stack)
        self.tab_group.addButton(new_tab)
        self.sidebar_layout.addWidget(new_tab)
        return new_tab


class SideTab(QPushButton):
    def __init__(self, label, page_index, icon_path, central_stack):
        super().__init__(label)
        self.label = label
        self.page_index = page_index
        self.icon_path = icon_path
        self.central_stack = central_stack

        self.initUI()

    def initUI(self):
        # set up button
        button = self
        button.setCheckable(True)
        self.collapsed = False

        # button icon
        button.setIcon(QIcon(self.icon_path))
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
        self.min_size_uncollapsed = (130, 50)
        self.size_collapsed = (50, 50)
        # button.setMaximumSize(150, 50)
        self.uncollapse()

        button.clicked.connect(
            lambda: self.central_stack.setCurrentIndex(self.page_index)
        )

    def collapse(self):
        print("collapsing")
        self.setText("")
        self.setFixedSize(*self.size_collapsed)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.collapsed = True

    def uncollapse(self):
        print("uncollapsing")
        self.setText(self.label)
        self.setMinimumSize(*self.min_size_uncollapsed)
        self.setMaximumWidth(10000)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.collapsed = False

    def collapse_toggle(self):
        if self.collapsed == True:
            self.uncollapse()
        else:
            self.collapse()


if __name__ == "__main__":
    app = QApplication([])
    mainWin = MainWindow()
    mainWin.show()
    app.exec()
