import os, json
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QStackedLayout, QListWidget, QSizePolicy, QMenu, QSplitter, QListWidgetItem, QSpinBox, QTextEdit, QDialog
from PySide6.QtGui import QIcon, QFont, QPixmap
from PySide6.QtCore import QSize, Qt
import pkg_resources
from . import shot_utils, make_shot, utils
from .houdini_wrapper import launch_houdini
from .interface_utils import quick_dialog

role_mapping = {
    "shot_data": Qt.UserRole + 1,
}

PACKAGE_NAME = "cog_vfx"
def get_asset_path(path):
    return pkg_resources.resource_filename(PACKAGE_NAME, path)

def get_shot_data(shot_list=None, item=None):
    shots = shot_utils.get_shots()
    if(item == None):
        selected_shot = shot_list.selectedItems()
        if(len(selected_shot)>0):
            selected_shot = selected_shot[0]
        else:
            return None
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
            print("Error:", shot_data["file_name"],"has no scene.hipnc file")


    def handle_aciton_delete(self):
        print("Deleting Shot")

class NewShotInterface(QDialog):
    def __init__(self, parent=None, shot_list=None, edit=False, shot_data=None):
        super(NewShotInterface, self).__init__(parent)
        self.setWindowFlags(Qt.Window)
        self.setWindowTitle("New Shot")
        self.resize(400,600)
        self.shot_list = shot_list

        # edit mode stuff
        self.edit_mode=edit
        self.existing_shot_data = shot_data

        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()

        # Shot Number
        self.layout.addWidget(QLabel("Shot Number"))
        self.select_shot_num = QSpinBox()
        shot_num = 10
        if(self.shot_list and len(self.shot_list.selectedItems())>0):
            print("shot_list", self.shot_list)
            shot_data = get_shot_data(self.shot_list)
            shot_num = shot_data["shot_num"]
            if(not self.edit_mode):
                shot_num+=10
        self.select_shot_num.setRange(1, 9999)
        self.select_shot_num.setValue(shot_num)
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

        # shot description
        self.layout.addWidget(QLabel("Shot Description"))
        self.shot_description_box = QTextEdit()
        self.layout.addWidget(self.shot_description_box)

        # add stretch
        self.layout.addStretch()

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

        self.setLayout(self.layout)

        if(self.existing_shot_data):
            self.fill_existing_values()

    def fill_existing_values(self):
        self.fill_value(self.select_start_frame, "start_frame")
        self.fill_value(self.select_end_frame, "end_frame")
        self.fill_value(self.shot_description_box, "description")

    def fill_value(self, widget, value):
        if(self.existing_shot_data[value]):
            if(isinstance(widget, QTextEdit)):
                widget.setPlainText(self.existing_shot_data[value])
            elif(isinstance(widget, QSpinBox)):
                widget.setValue(self.existing_shot_data[value])

    def on_ok_pressed(self):
        print("ok_pressed")
        # get shot data in variables from widgets
        self.finished_status = 0

        start_frame = self.select_start_frame.value()
        end_frame = self.select_end_frame.value()
        shot_num = self.select_shot_num.value()
        shot_desc = self.shot_description_box.toPlainText()

        # format shot data in dictionary
        self.new_shot_data = {
            "shot_num":shot_num,
            "start_frame":start_frame,
            "end_frame":end_frame,
            "description":shot_desc,
        }


        self.shot_file_name = "SH"+str(shot_num).zfill(4)
        self.close()

    def on_cancel_pressed(self):
        self.finished_status = 1
        self.close()

# ------------- SHOT PAGE -----------------

class ShotPage(QWidget):
    def __init__(self, parent=None):
        super(ShotPage, self).__init__(parent)
        self.set_shots()
        self.create_shot_page()

    def set_shots(self):
        self.shots = shot_utils.get_shots()


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
        self.shot_list.setSortingEnabled(True)
        self.shot_list.itemSelectionChanged.connect(self.update_shot_info)
        self.shot_list.setAlternatingRowColors(True)
        self.shot_list.setIconSize(QSize(500,50))
        self.populate_shot_list()
        self.shot_central_layout.addWidget(self.shot_list)

        # buttons
        bottom_buttons_layout = QHBoxLayout()
        bottom_buttons_layout.addStretch()


        self.shot_refresh_button = QPushButton("Refresh")
        # self.shot_refresh_button.setMaximumWidth(25)
        self.shot_refresh_button.clicked.connect(self.populate_shot_list)
        bottom_buttons_layout.addWidget(self.shot_refresh_button)

        self.shot_add_button = QPushButton("+")
        self.shot_add_button.setMaximumWidth(25)
        self.shot_add_button.clicked.connect(self.on_shot_add)
        bottom_buttons_layout.addWidget(self.shot_add_button)

        self.shot_delete_button = QPushButton("-")
        self.shot_delete_button.setMaximumWidth(25)
        self.shot_delete_button.clicked.connect(self.on_shot_delete)
        bottom_buttons_layout.addWidget(self.shot_delete_button)

        self.shot_central_layout.addLayout(bottom_buttons_layout)

    def create_shot_side_panel(self):
        self.shot_side_widget = QWidget()
        self.shot_side_widget.setStyleSheet("QWidget {background-color: #1b1e20; border-radius: 15px;}")
        self.shot_side_layout = QVBoxLayout(self.shot_side_widget)
        self.shot_page_layout.addWidget(self.shot_side_widget)

        # make font
        header_font = QFont()
        header_font.setPointSize(12)

        # title
        section_title = QLabel("Shot Info")
        section_title.setFont(header_font)
        # section_title.setMinimumWidth(200)
        self.shot_side_layout.addWidget(section_title)



        # shot thumbnail
        self.shot_thumbnail = QLabel()
        self.shot_thumbnail_size = (192*1.3, 108*1.3)
        print(*self.shot_thumbnail_size)
        self.shot_thumbnail.setMaximumSize(*self.shot_thumbnail_size)
        self.shot_side_layout.addWidget(self.shot_thumbnail)

        # general shot data container
        self.shot_misc_data_widget = QWidget()
        self.shot_misc_data_widget.setStyleSheet("QWidget {background-color: #2a2e32; border-radius: 15px;}")
        shot_misc_data_layout = QVBoxLayout(self.shot_misc_data_widget)
        self.shot_side_layout.addWidget(self.shot_misc_data_widget)
        general_shot_data_title = QLabel("Misc Data")
        general_shot_data_title.setFont(header_font)
        shot_misc_data_layout.addWidget(general_shot_data_title)

        # shot name
        self.shot_name_label = QLabel("SH")
        self.shot_name_label.hide()
        shot_misc_data_layout.addWidget(self.shot_name_label)

        # frame range
        self.shot_frame_range_label = QLabel("")
        shot_misc_data_layout.addWidget(self.shot_frame_range_label)

        # shot description
        self.shot_description_widget = QWidget()
        self.shot_description_widget.setStyleSheet("QWidget {background-color: #2a2e32; border-radius: 15px;}")
        shot_description_layout = QVBoxLayout(self.shot_description_widget)
        self.shot_side_layout.addWidget(self.shot_description_widget)

        description_title = QLabel("Shot Description")
        description_title.setFont(header_font)
        self.shot_description_title = description_title
        shot_description_layout.addWidget(self.shot_description_title)
        self.shot_description_label = QLabel("")
        shot_description_layout.addWidget(self.shot_description_label)

        self.shot_description_widget.hide()


        self.shot_side_layout.addStretch()

        self.shot_edit_button = QPushButton("Edit")
        self.shot_edit_button.clicked.connect(self.on_shot_edit)
        self.shot_edit_button.setStyleSheet(utils.get_style_sheet())
        self.shot_side_layout.addWidget(self.shot_edit_button)


    def update_shot_info(self):
        # setup
        selected_items = self.shot_list.selectedItems()
        if(len(selected_items)==0):
            return
        selected_shot = selected_items[0]
        sel_shot_data = get_shot_data(item=selected_shot) 
        print("sel_shot_data", sel_shot_data)

        # shot name
        self.shot_name_label.setText("Shot: " + sel_shot_data["formatted_name"])
        self.shot_name_label.show()

        # shot thumbnail
        thumbnail_dir = os.path.join(sel_shot_data["dir"], "thumbnail.png")
        if(not os.path.exists(thumbnail_dir)):
            thumbnail_dir = get_asset_path("assets/icons/missing_shot_thumbnail.png")
        pixmap = QPixmap(os.path.join(thumbnail_dir))
        pixmap = pixmap.scaled(QSize(*self.shot_thumbnail_size), Qt.KeepAspectRatioByExpanding, Qt.FastTransformation)
        self.shot_thumbnail.setPixmap(pixmap)

        # frame_range 
        if("start_frame" in sel_shot_data and "end_frame" in sel_shot_data):
            self.shot_frame_range_label.show()
            self.shot_frame_range_label.setText(f'Frame Range: {sel_shot_data["start_frame"]}-{sel_shot_data["end_frame"]}')
        else:
            self.shot_frame_range_label.hide()

        # shot description
        if("description" in sel_shot_data):
            self.shot_description_widget.show()
            self.shot_description_label.setText(sel_shot_data["description"])
        else:
            self.shot_description_widget.hide()

    def on_shot_add(self):
        # make_shot.new_shot("SH030")
        # self.populate_shot_list()
        print('shot add')
        self.new_shot = NewShotInterface(self, self.shot_list)
        self.new_shot.finished.connect(self.on_shot_add_finished)
        # self.new_shot.show()
        self.new_shot.exec()


    def on_shot_edit(self):
        selected_items = self.shot_list.selectedItems()
        if(len(selected_items)==0):
            print("no shot selected for editing")
            return

        selected_shot_data = selected_items[0].data(role_mapping["shot_data"])

        self.edit_shot_window = NewShotInterface(self, self.shot_list, edit=True, shot_data=selected_shot_data)
        self.edit_shot_window.finished.connect(self.on_shot_edit_finished)
        self.edit_shot_window.exec()

    def on_shot_edit_finished(self):
        # make sure user confirmed edit by pressing ok
        finished_stats = self.edit_shot_window.finished_status
        if(finished_stats != 0):
            return

        # setup variables
        selected_shot = self.shot_list.selectedItems()[0]
        old_shot_data = selected_shot.data(role_mapping["shot_data"])
        print("OLD SHOT DATA", old_shot_data)
        shot_dir = old_shot_data["dir"]
        shot_name = old_shot_data["file_name"]
        edit_shot_data = self.edit_shot_window.new_shot_data



        # move shot
        if(old_shot_data["shot_num"] != edit_shot_data["shot_num"]):
            print("\n\nSHOT NUMBER CHANGED!!!!")
            # print(f"old_shot_data: {old_shot_data} \nnew_shot_data: {new_shot_data}")
            dest_shot_name = "SH"+str(edit_shot_data["shot_num"]).zfill(4)
            dest_dir = make_shot.move_shot(self, shot_name, dest_shot_name)
            # check if move was successful
            if(not dest_dir):
                edit_shot_data.pop("shot_num")
                return

            # reformat list widget
            shot_dir = dest_dir
            shot_name = os.path.basename(dest_dir)
            new_shot_data = shot_utils.get_shots(shot_name)[0]
            selected_shot.setText("Shot " + new_shot_data["formatted_name"])

        # edit json
        shot_file_name = os.path.join(shot_dir, "shot_data.json")
        new_shot_data = make_shot.edit_shot_json(shot_file_name, edit_shot_data)
        new_shot_data = shot_utils.get_shots(shot_name)[0]

        # update list item data
        # self.populate_shot_list()
        print("SETTING NEW SHOT DATA", new_shot_data)
        if(new_shot_data!=0):
            selected_shot.setData(role_mapping["shot_data"], new_shot_data)
        else:
            print("can't find shot")

        # update info pannel
        self.update_shot_info()
        print("edit finished")

    def on_shot_add_finished(self):
        finished_stats = self.new_shot.finished_status
        if(finished_stats != 0):
            return
        new_shot_data = self.new_shot.new_shot_data

        shot_file_name = self.new_shot.shot_file_name
        print("creating shot", shot_file_name)
        make_shot.new_shot(self, shot_file_name, new_shot_data)

        self.populate_shot_list()

    def on_shot_delete(self):
        print('shot delete')
        quick_dialog(self, "Deleting shots isn't implemented yet")

    def populate_shot_list(self):
        # check for previous selection
        prev_selected_items = self.shot_list.selectedItems()
        has_prev_selection = False
        if(len(prev_selected_items)!=0):
            prev_selected_text = prev_selected_items[0].text()
            has_prev_selection = True

        # clear contents
        self.shot_list.clear()

        # create new shots
        self.set_shots()
        for shot in self.shots:
            item_label = "Shot " + shot["formatted_name"]
            item = QListWidgetItem(item_label, self.shot_list)
            item.setData(role_mapping["shot_data"], shot)
            thumbnail_path = os.path.join(shot["dir"],"thumbnail.png")
            print("thumbnail path", thumbnail_path)
            item.setIcon(QIcon(thumbnail_path))

            if(has_prev_selection and item_label == prev_selected_text):
                # print(f"{item_label} == {prev_selected_text}")
                item.setSelected(True)
            # elif(has_prev_selection):
            #     print(f"{item_label} != {prev_selected_text}")
            
            
        # print("shots", shots)
