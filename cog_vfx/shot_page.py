import os
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QStackedLayout, QListWidget, QSizePolicy, QMenu, QSplitter, QListWidgetItem, QSpinBox
from PySide6.QtGui import QIcon, QFont, QPixmap
from PySide6.QtCore import QSize, Qt
import pkg_resources
from . import shot_utils, make_shot, utils
from .houdini_wrapper import launch_houdini

role_mapping = {
    "shot_data": Qt.UserRole + 1,
}

PACKAGE_NAME = "cog_vfx"
def get_asset_path(path):
    return pkg_resources.resource_filename(PACKAGE_NAME, path)

def get_shot_data(shot_list=None, item=None):
    shots = shot_utils.get_shots()
    if(item == None):
        selected_shot = shot_list.selectedItems()[0]
    else:
        selected_shot = item

    return selected_shot.data(role_mapping["shot_data"])

class ShotListWidget(QListWidget):
    def __init__(self, parent=None):
        super(ShotListWidget, self).__init__(parent)

    def contextMenuEvent(self, event):
        contextMenu = QMenu(self)

        # Check if right-click is on an item
        item = self.itemAt(event.pos())
        if item is not None:
            # Add "Open Shot" action only if clicked on an item
            action_open = contextMenu.addAction("Open Shot")
            action_delete = contextMenu.addAction("Delete Shot")
            shot_data = get_shot_data(item=item)

        action = contextMenu.exec_(self.mapToGlobal(event.pos()))


        if item is not None:
            if action == action_open:
                self.handle_action_open(shot_data)
            elif action == action_delete:
                self.handle_aciton_delete()

    def handle_action_open(self, shot_data):
        print("Opening Shot")
        scene_path = os.path.join(shot_data["dir"],"scene.hipnc")
        if(os.path.exists(scene_path)):
            launch_houdini(scene_path)
        else:
            print("Error:", shot_data["name"],"has no scene.hipnc file")


    def handle_aciton_delete(self):
        print("Deleting Shot")

class NewShotInterface(QWidget):
    def __init__(self, parent=None):
        super(NewShotInterface, self).__init__(parent)
        self.setWindowFlags(Qt.Window)
        self.setWindowTitle("New Shot")
        self.resize(400,600)

        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()

        # Shot Number
        self.layout.addWidget(QLabel("Shot Number"))
        self.select_shot_num = QSpinBox()
        self.select_shot_num.setRange(1, 9999)
        self.layout.addWidget(self.select_shot_num)

        # frame range title
        self.layout.addWidget(QLabel("Frame Range"))
        range_layout = QHBoxLayout()

        # frame start box one
        self.select_start_frame = QSpinBox()
        self.select_start_frame.setRange(1001, 9999)
        self.select_start_frame.setValue(1001)
        range_layout.addWidget(self.select_start_frame)

        # frame start box one
        self.select_end_frame = QSpinBox()
        self.select_end_frame.setRange(1001, 9999)
        self.select_end_frame.setValue(1100)
        range_layout.addWidget(self.select_end_frame)

        self.layout.addLayout(range_layout)
        self.layout.addStretch()

        self.setLayout(self.layout)
        

class ShotPage(QWidget):
    def __init__(self, parent=None):
        super(ShotPage, self).__init__(parent)
        self.shots = shot_utils.get_shots()
        self.create_shot_page()


    def create_shot_page(self):
        # Create content for Tab 1
        self.shot_page_layout = QHBoxLayout(self)
        self.shot_central_layout = QVBoxLayout()

        self.shot_page_layout.addLayout(self.shot_central_layout)

        self.create_shot_side_panel()

        self.shot_page_label = QLabel("Shots")
        self.shot_central_layout.addWidget(self.shot_page_label)

        # Shot list
        self.shot_list = ShotListWidget()
        self.shot_list.itemSelectionChanged.connect(self.update_shot_info)
        self.shot_list.setAlternatingRowColors(True)
        self.shot_list.setIconSize(QSize(500,50))
        self.add_to_shots_list()
        self.shot_central_layout.addWidget(self.shot_list)

        # buttons
        bottom_buttons_layout = QHBoxLayout()
        bottom_buttons_layout.addStretch()

        self.shot_refresh_button = QPushButton("Refresh")
        # self.shot_refresh_button.setMaximumWidth(25)
        self.shot_refresh_button.clicked.connect(self.add_to_shots_list)
        bottom_buttons_layout.addWidget(self.shot_refresh_button)

        self.shot_add_button = QPushButton("+")
        self.shot_add_button.setMaximumWidth(25)
        self.shot_add_button.clicked.connect(self.on_shot_add)
        bottom_buttons_layout.addWidget(self.shot_add_button)

        self.shot_delete_button = QPushButton("-")
        self.shot_delete_button.setMaximumWidth(25)
        bottom_buttons_layout.addWidget(self.shot_delete_button)

        self.shot_central_layout.addLayout(bottom_buttons_layout)

    def create_shot_side_panel(self):
        self.shot_side_layout = QVBoxLayout()

        # title
        section_title = QLabel("Shot Info")
        # section_title.setMinimumWidth(200)
        self.shot_side_layout.addWidget(section_title)

        # shot name
        self.shot_name_label = QLabel("SH")
        self.shot_side_layout.addWidget(self.shot_name_label)


        # shot thumbnail
        self.shot_thumbnail = QLabel()
        self.shot_thumbnail_size = (192*1.3, 108*1.3)
        print(*self.shot_thumbnail_size)
        self.shot_thumbnail.setMaximumSize(*self.shot_thumbnail_size)
        self.shot_side_layout.addWidget(self.shot_thumbnail)

        # frame range
        self.shot_frame_range_label = QLabel("")
        self.shot_side_layout.addWidget(self.shot_frame_range_label)


        self.shot_side_layout.addStretch()
        self.shot_page_layout.addLayout(self.shot_side_layout)


    def update_shot_info(self):
        # setup
        selected_shot = self.shot_list.selectedItems()[0]
        sel_shot_data = get_shot_data(item=selected_shot) 
        print("sel_shot_data", sel_shot_data)

        # shot name
        self.shot_name_label.setText(sel_shot_data["name"])

        # shot thumbnail
        thumbnail_dir = os.path.join(sel_shot_data["dir"], "thumbnail.png")
        if(not os.path.exists(thumbnail_dir)):
            thumbnail_dir = get_asset_path("assets/icons/missing_shot_thumbnail.png")
        pixmap = QPixmap(os.path.join(thumbnail_dir))
        pixmap = pixmap.scaled(QSize(*self.shot_thumbnail_size), Qt.KeepAspectRatioByExpanding, Qt.FastTransformation)
        self.shot_thumbnail.setPixmap(pixmap)

        # frame_range 
        if("start_frame" in sel_shot_data and "end_frame" in sel_shot_data):
            self.shot_frame_range_label.setText(f'Frame Range: {sel_shot_data["start_frame"]}-{sel_shot_data["end_frame"]}')
        else:
            self.shot_frame_range_label.setText("")


    def on_shot_add(self):
        # make_shot.new_shot("SH030")
        # self.add_to_shots_list()
        print('shot add')
        self.new_shot = NewShotInterface(self)
        self.new_shot.show()

    def add_to_shots_list(self):
        self.shot_list.clear()

        for shot in self.shots:
            # self.shot_list.addItem()
            item = QListWidgetItem(shot["formatted_name"], self.shot_list)
            item.setData(role_mapping["shot_data"], shot)
            thumbnail_path = os.path.join(shot["dir"],"thumbnail.png")
            print("thumbnail path", thumbnail_path)
            item.setIcon(QIcon(thumbnail_path))
            
            
        # print("shots", shots)
