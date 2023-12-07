import os, json
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QStackedLayout, QListWidget, QSizePolicy, QMenu, QSplitter, QListWidgetItem, QSpinBox, QTextEdit, QDialog, QScrollArea, QProgressBar, QLineEdit, QSpacerItem, QTreeWidget, QTreeWidgetItem, QButtonGroup
from PySide6.QtGui import QIcon, QFont, QPixmap
from PySide6.QtCore import QSize, Qt, QThread, Signal
import pkg_resources
from . import shot_utils, file_utils, utils, interface_utils
from .houdini_wrapper import launch_houdini, launch_hython
from .interface_utils import quick_dialog
from .file_utils import get_pkg_asset_path
from .info_panel import InfoPanel

style_sheet = interface_utils.get_style_sheet()

role_mapping = {
    "shot_data": Qt.UserRole + 1,
}

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



class RenderThread(QThread):
    progress_update = Signal(int)
    frame_update = Signal(str)
    finished = Signal()

    def __init__(self, scene_path, shot_data, render_node_path):
        super(RenderThread, self).__init__()
        self.scene_path = scene_path
        self.shot_data = shot_data
        self.node_path = render_node_path 

    def run(self):
        # prepare script to run
        script = "import sys; module_directory = '{module_directory}';sys.path.append(module_directory); import husk_render; husk_render.exec_render_node('{scene_path}', '{node_path}')"
        script = script.format(module_directory=get_pkg_asset_path(""), scene_path=self.scene_path, node_path=self.node_path)

        self.process = launch_hython(self.scene_path, self.shot_data, script=script, live_mode=True)
        while True:
            output = self.process.stdout.readline()
            # print("output", output)
            if output == '' and self.process.poll() is not None:
                break
            if output.startswith('ALF_PROGRESS'):
                progress = int(output.strip().split(' ')[1].rstrip('%'))
                self.progress_update.emit(progress)
            elif ">>> Render" in output:
                frame_num = output[-9:-5]
                print("CURRENT FRAME:", frame_num)
                self.frame_update.emit(frame_num)

    def terminate_process(self):
        if self.process:
            self.process.terminate()

class RenderLoading(QDialog):
    def __init__(self, parent, scene_path, shot_data, render_node_path):
        super(RenderLoading, self).__init__(parent)
        self.scene_path = scene_path
        self.shot_data = shot_data
        # self.subprocess_thread = subprocess_thread

        self.initUI()
        self.subprocess_thread = RenderThread(self.scene_path, self.shot_data, render_node_path)
        self.subprocess_thread.progress_update.connect(self.updateProgressBar)
        self.subprocess_thread.frame_update.connect(self.updateFrame)
        self.subprocess_thread.finished.connect(self.closeDialog)
        self.subprocess_thread.start()

    def initUI(self):
        self.progressBar = QProgressBar(self)
        self.setMaximumSize(400, 50)
        self.layout = QVBoxLayout()

        # Shot Label
        print(" \n\n\nSHOT DATA", self.shot_data)
        self.shot_label = QLabel("Shot: "+self.shot_data['formatted_name'])
        self.layout.addWidget(self.shot_label)

        self.frame_label = QLabel("Render Setup")
        self.layout.addWidget(self.frame_label)
        self.layout.addWidget(self.progressBar)
        self.setLayout(self.layout)
        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle("Render Progress")

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.on_cancel_button)
        self.layout.addWidget(self.cancel_button)

    def on_cancel_button(self):
        self.close()

    def updateProgressBar(self, value):
        self.progressBar.setValue(value)

    def updateFrame(self, value):
        self.frame_label.setText("Frame: " + value)

    def closeDialog(self):
        self.close()

    def closeEvent(self, event):
        self.subprocess_thread.terminate_process()
        event.accept()


class PopulateListThread(QThread):
    finished = Signal(list)

    def __init__(self, scene_path, shot_data):
        QThread.__init__(self)
        self.scene_path = scene_path
        self.shot_data = shot_data

    def run(self):
        script = "import sys; module_directory = '{module_directory}';sys.path.append(module_directory); import husk_render; husk_render.get_render_nodes('{scene_path}')"
        script = script.format(module_directory=get_pkg_asset_path(""), scene_path = self.scene_path)
        # run script through hython
        self.get_render_nodes_process = launch_hython(self.scene_path, self.shot_data, script=script, set_vars=False)

        # extract data from stdout
        render_nodes = []
        for stdout_line in self.get_render_nodes_process.stdout.split("\n"):
            if(stdout_line.startswith("__RETURN_RENDER_NODE:")):
                stdout_line_split = stdout_line.split(":")
                node_name = stdout_line_split[1]
                node_path = stdout_line_split[2]
                render_nodes.append({"name":node_name, "node_path":node_path})
        print("emmiting", render_nodes)
        self.finished.emit(render_nodes)

class SelectRenderNodeDialog(QDialog):
    def __init__(self, parent=None, scene_path=None, shot_data=None):
        super(SelectRenderNodeDialog, self).__init__(parent)
        self.scene_path = scene_path
        self.shot_data = shot_data

        # start thread
        self.populate_list_thread = PopulateListThread(self.scene_path, self.shot_data)
        self.populate_list_thread.finished.connect(self.populate_list)
        self.populate_list_thread.start()

        self.initUI()

        self.setWindowTitle("Select Render Layer")

    def initUI(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.instruction_label = QLabel("Loading...")
        self.layout.addWidget(self.instruction_label)

        # create layer list
        self.render_node_list = QListWidget()
        self.layout.addWidget(self.render_node_list)

        self.render_button = QPushButton("render")
        self.render_button.hide()
        self.render_button.clicked.connect(self.on_render_button)
        self.layout.addWidget(self.render_button)
        self.setModal(True)
        self.show()

    def populate_list(self, render_nodes):
        print("populating list with", render_nodes)
        self.render_nodes = render_nodes
        self.layer_data_role = Qt.UserRole + 1
        for render_node in self.render_nodes:
            list_item = QListWidgetItem(render_node["name"])
            list_item.setData(self.layer_data_role, render_node)
            self.render_node_list.addItem(list_item)

        self.instruction_label.setText("Please select the layer you'd like to render")
        self.render_button.show()

    def on_render_button(self):
        print("render button clicked")
        selected_items = self.render_node_list.selectedItems()
        if(len(selected_items)==0):
            return
        sel_layer_path = selected_items[0].data(self.layer_data_role)["node_path"]
        self.close()
        render_loading = RenderLoading(self, self.scene_path, self.shot_data, sel_layer_path)
        render_loading.show()




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
            action_render = contextMenu.addAction("Render Shot")
            action_delete = contextMenu.addAction("Delete Shot")
            shot_data = get_shot_data(item=item)

        action = contextMenu.exec_(self.mapToGlobal(event.pos()))


        if item is not None:
            if action == action_open:
                self.handle_action_open(shot_data)
            elif action == action_delete:
                self.handle_action_delete()
            elif action == action_render:
                self.handle_action_render(shot_data)

    def handle_action_open(self, shot_data):
        print("Opening Shot")
        scene_path = os.path.join(shot_data["dir"],"scene.hipnc")
        if(os.path.exists(scene_path)):
            launch_houdini(scene_path, shot_data, "shot")
        else:
            print("Error:", shot_data["file_name"],"has no scene.hipnc file")


    def handle_action_delete(self):
        print("Deleting Shot")

    def handle_action_render(self, shot_data):
        print("Rendering Shot")
        scene_path = os.path.join(shot_data["dir"],"scene.hipnc")
        if(os.path.exists(scene_path)):
            select_render_node = SelectRenderNodeDialog(self, scene_path, shot_data)
            # select_render_node.exec()
            print("created window")

            
            return
            # launch_hython(scene_path, shot_data, get_pkg_asset_path("husk_render.py"))
        else:
            print("Error:", shot_data["file_name"],"has no scene.hipnc file")

class NewShotInterface(QDialog):
    def __init__(self, parent=None, shot_list=None, edit=False, shot_data=None):
        super().__init__(parent)
        self.setWindowTitle("New Shot")
        self.resize(400,600)
        self.shot_list = shot_list

        # edit mode stuff
        self.edit_mode=edit
        self.existing_shot_data = shot_data

        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Shot Number
        self.layout.addWidget(QLabel("Shot Number"))
        self.select_shot_num = QSpinBox()
        shot_num = 10
        if(self.shot_list and len(self.shot_list.selectedItems())>0):
            print("shot_list", self.shot_list)
            shot_data = get_shot_data(self.shot_list)
            shot_num = shot_data["shot_num"] if "shot_num" in shot_data else 10
            if(not self.edit_mode):
                shot_num+=10
        self.select_shot_num.setRange(1, 9999)
        self.select_shot_num.setValue(shot_num)
        self.layout.addWidget(self.select_shot_num)

        # frame range title
        self.layout.addWidget(QLabel("Frame Range"))
        frame_range_layout = QHBoxLayout()
        self.layout.addLayout(frame_range_layout)

        # frame start box one
        self.select_start_frame = QSpinBox()
        self.select_start_frame.setRange(1001, 9999)
        self.select_start_frame.setValue(1001)
        frame_range_layout.addWidget(self.select_start_frame)

        # frame start box one
        self.select_end_frame = QSpinBox()
        self.select_end_frame.setRange(1001, 9999)
        self.select_end_frame.setValue(1100)
        frame_range_layout.addWidget(self.select_end_frame)

        # resolution title
        self.layout.addWidget(QLabel("Resolution"))
        res_layout = QHBoxLayout()
        self.layout.addLayout(res_layout)

        # resolution width
        self.select_res_width = QSpinBox()
        self.select_res_width.setRange(1, 9999)
        self.select_res_width.setValue(1920)
        res_layout.addWidget(self.select_res_width)

        # resolution height
        self.select_res_height = QSpinBox()
        self.select_res_height.setRange(1, 9999)
        self.select_res_height.setValue(1080)
        res_layout.addWidget(self.select_res_height)

        # fps
        self.layout.addWidget(QLabel("FPS"))
        self.select_fps = QSpinBox()
        self.select_fps.setRange(1, 9999)
        self.select_fps.setValue(24)
        self.layout.addWidget(self.select_fps)

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

        if(self.existing_shot_data):
            self.fill_existing_values()

    def fill_existing_values(self):
        self.fill_value(self.select_start_frame, "start_frame")
        self.fill_value(self.select_end_frame, "end_frame")
        self.fill_value(self.shot_description_box, "description")
        self.fill_value(self.select_res_width, "res_width")
        self.fill_value(self.select_res_height, "res_height")
        self.fill_value(self.select_fps, "fps")

    def fill_value(self, widget, value):
        if(value in self.existing_shot_data):
            if(isinstance(widget, QTextEdit)):
                widget.setPlainText(self.existing_shot_data[value])
            elif(isinstance(widget, QSpinBox)):
                widget.setValue(self.existing_shot_data[value])

    # ----- SIGNALS ------- 

    def on_ok_pressed(self):
        print("ok_pressed")
        # get shot data in variables from widgets
        self.finished_status = 0

        start_frame = self.select_start_frame.value()
        end_frame = self.select_end_frame.value()
        shot_num = self.select_shot_num.value()
        res_width = self.select_res_width.value()
        res_height = self.select_res_height.value()
        fps = self.select_fps.value()
        shot_desc = self.shot_description_box.toPlainText()

        # format shot data in dictionary
        self.new_shot_data = {
            "shot_num":shot_num,
            "start_frame":start_frame,
            "end_frame":end_frame,
            "description":shot_desc,
            "res_width":res_width,
            "res_height":res_height,
            "fps":fps
        }


        self.shot_file_name = "SH"+str(shot_num).zfill(4)
        self.close()

    def on_cancel_pressed(self):
        self.finished_status = 1
        self.close()

# ------------- SHOT PAGE -----------------
class ShotListWidget(interface_utils.ObjectSelector):
    def __init__(self, parent=None):
        super().__init__(parent)


    def on_object_add(self):
        # file_utils.new_object("SH030")
        # self.populate_object_list()
        print('shot add')
        self.new_object = NewShotInterface(self, self.object_list)
        # self.new_object.finished.connect(self.on_object_add_finished)
        # self.new_object.show()
        self.new_object.exec()

    def update_object_info(self):
        # setup
        selected_items = self.object_list.selectedItems()
        if(len(selected_items)==0):
            return
        selected_shot = selected_items[0]
        sel_shot_data = get_shot_data(item=selected_shot) 
        print("sel_shot_data", sel_shot_data)
        return

        # shot name
        self.shot_name_label.setText("Shot: " + sel_shot_data["formatted_name"])
        self.shot_name_label.show()

        # shot thumbnail
        thumbnail_dir = os.path.join(sel_shot_data["dir"], "thumbnail.png")
        if(not os.path.exists(thumbnail_dir)):
            thumbnail_dir = get_pkg_asset_path("assets/icons/missing_shot_thumbnail.png")
        pixmap = QPixmap(os.path.join(thumbnail_dir))
        pixmap = pixmap.scaled(QSize(*self.shot_thumbnail_size), Qt.KeepAspectRatioByExpanding, Qt.FastTransformation)
        self.shot_thumbnail.setPixmap(pixmap)

        # frame_range 
        if("start_frame" in sel_shot_data and "end_frame" in sel_shot_data):
            self.shot_frame_range_label.show()
            self.shot_frame_range_label.setText(f'Frame Range: {sel_shot_data["start_frame"]}-{sel_shot_data["end_frame"]}')
        else:
            self.shot_frame_range_label.hide()

        if("res_height" in sel_shot_data and "res_width" in sel_shot_data):
            self.shot_render_res_label.setText(f'Resolution: {sel_shot_data["res_width"]}x{sel_shot_data["res_height"]}')
            self.shot_render_res_label.show()
        else:
            self.shot_render_res_label.hide()

        if("fps" in sel_shot_data):
            self.shot_render_fps_label.setText(f'Fps: {sel_shot_data["fps"]}')
            self.shot_render_fps_label.show()
        else:
            self.shot_render_fps_label.hide()


        # shot description
        if("description" in sel_shot_data and sel_shot_data["description"]!=""):
            self.shot_description_widget.show()
            self.shot_description_label.setText(sel_shot_data["description"])
        else:
            self.shot_description_widget.hide()

class ShotInfoPanel(InfoPanel):
    def __init__(self, parent=None):
        super().__init__(parent)
        # title
        self.title.setText("Shot Info")

        # create sections
        self.create_sections()
        self.create_bottom_buttons()

    def create_sections(self):
        # thumbnail
        thumbnail_dir = get_pkg_asset_path("assets/icons/missing_shot_thumbnail.png")
        self.new_thumbnail(thumbnail_dir)

        # render data section
        self.render_data_section = self.new_section("Render Data")
        self.shot_num = self.render_data_section.add_label("SH: 0000")
        self.frame_range = self.render_data_section.add_label("Frame Range: 1001 - 1100")
        self.render_res = self.render_data_section.add_label("Resolution: 1920x1080")
        self.render_fps = self.render_data_section.add_label("FPS: 24")

        # description section
        self.description_section = self.new_section("Description")
        self.description_label = self.description_section.add_label("my test description")

class ShotPage(QWidget):
    def __init__(self, parent=None):
        super(ShotPage, self).__init__(parent)
        self.init_icons()
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
        # self.role_list_layout_parent = QVBoxLayout()
        # self.files_layout.addLayout(self.role_list_layout_parent)
        self.file_tree_layout_parent = QVBoxLayout()
        self.files_layout.addLayout(self.file_tree_layout_parent)

        self.create_shot_side_panel()
        self.create_shot_list_panel()
        self.create_role_list_panel()
        self.create_file_tree_panel()
        self.populate_file_tree()

    def create_file_tree_panel(self):
        self.file_tree_widget = QWidget()
        self.file_tree_layout_parent.addWidget(self.file_tree_widget)
        self.file_tree_layout = QVBoxLayout(self.file_tree_widget)
        self.file_tree_widget.setStyleSheet("""
    QWidget {
        border-radius: 15px;
        background-color: #1b1e20;
    }
""")

        # Label
        self.files_page_label = QLabel("Files")
        self.files_page_label.setFont(self.header_font)
        self.file_tree_layout.addWidget(self.files_page_label)

        self.role_layout = QHBoxLayout()
        self.file_tree_layout.addLayout(self.role_layout)
        self.role_button_group = QButtonGroup()
        self.create_role_button("FX", "fx")
        anim_button = self.create_role_button("Anim", "anim")
        self.create_role_button("Comp", "comp")
        # default button
        anim_button.click()

        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderLabel("")
        self.file_tree_layout.addWidget(self.file_tree)

    def create_role_button(self, label, role_name):
        role_button = QPushButton(label)
        role_button.setStyleSheet(style_sheet)
        role_button.setCheckable(True)
        self.role_button_group.addButton(role_button)
        role_button.clicked.connect(lambda: self.set_selected_role(role_name))
        self.role_layout.addWidget(role_button)
        return role_button
    
    def set_selected_role(self, role_name):
        self.selected_role = role_name
        self.populate_file_tree()

    def init_icons(self):
        #icons
        self.icon_file = QIcon(get_pkg_asset_path("assets/icons/file_white.png"))
        self.icon_dir_full = QIcon(get_pkg_asset_path("assets/icons/folder_open_white.png"))
        self.icon_dir_empty = QIcon(get_pkg_asset_path("assets/icons/folder_closed_white.png"))
        self.file_name_icon_mapping = {"anim.mb": QIcon(get_pkg_asset_path("assets/icons/animation_white.png")),
                        "scene.hipnc": QIcon(get_pkg_asset_path("assets/icons/scene_white.png")),
                        }
        self.file_type_icon_mapping = {"hipnc": QIcon(get_pkg_asset_path("assets/icons/houdini_white.png")),
                          }

    def populate_file_tree(self):
        self.file_tree.clear()

        # Font
        tree_font = QFont()
        tree_font.setPointSize(12)

        # fetch directory path
        selected_items = self.shot_list.selectedItems()
        if(len(selected_items)==0):
            return
        selected_shot = selected_items[0]
        sel_shot_data = get_shot_data(item=selected_shot) 
        directory_path = sel_shot_data["dir"]
        directory_path += "/"+self.selected_role
        if(not os.path.exists(directory_path)):
            raise Exception("ERROR: directory does not exist: "+directory_path)
            return
        # whitelist_dirs = ["comp", "fx", "anim"]
        # whitelist_files = ["scene.hipnc"]

        # walk through files
        path_to_item = {}
        for (root, dirs, files) in os.walk(directory_path):
            # filter top level directories
            # if(root == directory_path):
            #     dirs[:] = [d for d in dirs if d in whitelist_dirs]
            #     files[:] = [f for f in files if f in whitelist_files]

            parent_item = path_to_item.get(root, self.file_tree)

            # handle directories
            for dir_name in dirs:
                dir_item = QTreeWidgetItem(parent_item, [dir_name])
                dir_path = os.path.join(root, dir_name)
                path_to_item[dir_path] = dir_item

                # font
                dir_item.setFont(0, tree_font)
                #icons
                if(len(os.listdir(dir_path)) == 0):
                    dir_item.setIcon(0, self.icon_dir_empty)
                else:
                    dir_item.setIcon(0, self.icon_dir_full)

            # handle files
            for file_name in files:
                file_item = QTreeWidgetItem(parent_item, [file_name])

                # font
                file_item.setFont(0, tree_font)
                # icons
                file_name_split = file_name.split(".")
                file_type = file_name_split[-1].lower() if len(file_name_split)!=0 else ""
                if file_name.lower() in self.file_name_icon_mapping:
                    icon = self.file_name_icon_mapping[file_name.lower()]
                elif(file_type in self.file_type_icon_mapping):
                    icon = self.file_type_icon_mapping[file_type]
                else:
                    icon = self.icon_file
                file_item.setIcon(0, icon)
            # print("root:",root)
            # print("dirs:", dirs)
            # print("files:", files)


    def create_role_list_panel(self):
        # Label
        self.role_list_widget = QWidget()
        self.role_list_layout = QVBoxLayout(self.role_list_widget)
        self.role_page_label = QLabel("Roles")
        self.role_page_label.setFont(self.header_font)
        self.role_list_layout.addWidget(self.role_page_label)


        # Role list
        self.role_list = QListWidget()
        self.role_list.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        self.role_list.setMaximumHeight(self.role_list.minimumSizeHint().height())
        self.role_list.setSortingEnabled(True)
        self.role_list.addItem("Anim")
        self.role_list.addItem("FX")
        self.role_list.addItem("Stage")
        # self.role_list.itemSelectionChanged.connect(self.update_role_info)
        self.role_list.setAlternatingRowColors(True)
        self.role_list.setIconSize(QSize(500,50))
        # self.populate_role_list()
        self.role_list_layout.addWidget(self.role_list)

    def create_shot_list_panel(self):
        self.shot_list_widget = ShotListWidget()
        self.shot_list_layout_parent.addWidget(self.shot_list_widget)
        self.shot_list = self.shot_list_widget.object_list



    def create_shot_side_panel(self):
        self.shot_side_widget = ShotInfoPanel()

        # Create a content widget and a layout for it
        self.shot_page_layout.addWidget(self.shot_side_widget)



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
        if(not "shot_num" in old_shot_data or old_shot_data["shot_num"] != edit_shot_data["shot_num"]):
            print("\n\nSHOT NUMBER CHANGED!!!!")
            # print(f"old_shot_data: {old_shot_data} \nnew_shot_data: {new_shot_data}")
            dest_shot_name = "SH"+str(edit_shot_data["shot_num"]).zfill(4)
            dest_dir = file_utils.move_shot(self, shot_name, dest_shot_name)
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
        new_shot_data = file_utils.edit_shot_json(shot_file_name, edit_shot_data)
        new_shot_data = shot_utils.get_shots(shot_name)[0]

        # update list item data
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
        file_utils.new_shot(self, shot_file_name, new_shot_data)

        self.populate_shot_list()



            
