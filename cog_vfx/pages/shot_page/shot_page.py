from PySide6.QtGui import QFont

# import QT
from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget

# import utilities
from ...utils import file_utils, interface_utils, utils
from ...utils.file_utils import get_pkg_asset_path
from ...utils.houdini_wrapper import launch_houdini, launch_hython
from ...utils.interface_utils import quick_dialog
from .controller import ShotPanelController

# import panels
from .panels import ShotInfoPanel, ShotListPanel, ShotWorkspacePanel
from .utils import shot_utils

style_sheet = interface_utils.get_style_sheet()


# ------------- SHOT PAGE -----------------


class ShotPage(QWidget):
    def __init__(self, parent=None):
        super(ShotPage, self).__init__(parent)
        # make font
        self.header_font = QFont()
        self.header_font.setPointSize(12)

        self.set_shots()
        self.create_shot_page()

    def set_shots(self):
        self.shots = shot_utils.get_shots()

    def create_shot_page(self):
        # Create content for Tab 1
        self.shot_page_layout = QHBoxLayout(self)

        # Layout
        self.shot_list_layout_parent = QVBoxLayout()
        self.shot_page_layout.addLayout(self.shot_list_layout_parent)
        self.shot_side_layout = QVBoxLayout()
        self.shot_page_layout.addLayout(self.shot_side_layout)
        self.files_layout = QVBoxLayout()
        self.shot_page_layout.addLayout(self.files_layout)
        self.file_tree_layout_parent = QVBoxLayout()
        self.files_layout.addLayout(self.file_tree_layout_parent)

        # controller
        self.shot_controller = ShotPanelController()

        # self.create_shot_side_panel()
        self.create_shot_list_panel()
        # self.create_file_tree_panel()
        # connect widgets so selecting a new shot updates the tree
        # self.shot_list_widget.tree_widget = self.workspace_files

    def create_file_tree_panel(self):
        self.workspace_files = ShotWorkspacePanel(
            self.shot_controller, self.shot_list_widget
        )
        self.file_tree_layout_parent.addWidget(self.workspace_files)
        self.workspace_files.populate_file_tree()

    def create_shot_list_panel(self):
        self.shot_list_widget = ShotListPanel(self.shot_controller, parent=self)
        self.shot_list_layout_parent.addWidget(self.shot_list_widget)
        self.shot_list = self.shot_list_widget.element_list

    def create_shot_side_panel(self):
        self.shot_side_widget = ShotInfoPanel(self.shot_controller)

        # Create a content widget and a layout for it
        self.shot_page_layout.addWidget(self.shot_side_widget)
