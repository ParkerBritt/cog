import os, json
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QStackedLayout, QListWidget, QSizePolicy, QMenu, QSplitter, QListWidgetItem, QSpinBox, QTextEdit, QDialog, QScrollArea, QProgressBar, QLineEdit, QSpacerItem, QTreeWidget, QTreeWidgetItem, QButtonGroup
from PySide6.QtGui import QIcon, QFont, QPixmap
from PySide6.QtCore import QSize, Qt, QThread, Signal
import pkg_resources
from . import shot_utils, file_utils, utils
from .houdini_wrapper import launch_houdini, launch_hython
from .interface_utils import quick_dialog

style_sheet = utils.get_style_sheet()

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
        script = script.format(module_directory=get_asset_path(""), scene_path=self.scene_path, node_path=self.node_path)

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
        script = script.format(module_directory=get_asset_path(""), scene_path = self.scene_path)
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
            # launch_hython(scene_path, shot_data, get_asset_path("husk_render.py"))
        else:
            print("Error:", shot_data["file_name"],"has no scene.hipnc file")

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
        self.icon_file = QIcon(get_asset_path("assets/icons/file_white.png"))
        self.icon_dir_full = QIcon(get_asset_path("assets/icons/folder_open_white.png"))
        self.icon_dir_empty = QIcon(get_asset_path("assets/icons/folder_closed_white.png"))
        self.file_name_icon_mapping = {"anim.mb": QIcon(get_asset_path("assets/icons/animation_white.png")),
                        "scene.hipnc": QIcon(get_asset_path("assets/icons/scene_white.png")),
                        }
        self.file_type_icon_mapping = {"hipnc": QIcon(get_asset_path("assets/icons/houdini_white.png")),
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
        self.shot_list_widget = QWidget()
        self.shot_list_layout = QVBoxLayout(self.shot_list_widget)
        self.shot_list_layout_parent.addWidget(self.shot_list_widget)
        # self.shot_list_widget.setMaximumWidth(self.shot_list_widget.minimumSizeHint().width())
        self.shot_list_widget.setMinimumWidth(215)
        self.shot_list_widget.setMaximumWidth(280)
        print(" MAXIMUM SIZE:", self.shot_list_widget.minimumSizeHint().width())

        # Label
        self.shot_page_label = QLabel("Shots")
        self.shot_page_label.setFont(self.header_font)
        self.shot_list_layout.addWidget(self.shot_page_label)

        # Search Bar
        self.shot_search_bar = QLineEdit()
        # self.shot_search_bar.setMaximumWidth(self.shot_search_bar.minimumSizeHint().width())
        self.shot_search_bar.setTextMargins(5, 1, 5, 1)
        search_bar_font = QFont()
        search_bar_font.setPointSize(12)
        self.shot_search_bar.setFont(search_bar_font)
        self.shot_search_bar.textChanged.connect(self.on_search_changed)
        self.shot_list_layout.addWidget(self.shot_search_bar)
        spacer = QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Preferred)
        self.shot_list_layout.addItem(spacer)


        # Shot list
        self.shot_list = ShotListWidget()
        # self.shot_list.setMaximumWidth(self.shot_list.minimumSizeHint().width())
        self.shot_list.setSortingEnabled(True)
        self.shot_list.itemSelectionChanged.connect(self.on_shot_selection_changed)
        self.shot_list.setAlternatingRowColors(True)
        self.shot_list.setIconSize(QSize(500,50))
        self.populate_shot_list()
        self.shot_list_layout.addWidget(self.shot_list)

        # buttons
        bottom_buttons_layout = QHBoxLayout()
        bottom_buttons_layout.addStretch()


        self.shot_refresh_button = QPushButton("Refresh")
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

        self.shot_list_layout.addLayout(bottom_buttons_layout)

    def on_shot_selection_changed(self):
        self.update_shot_info()
        self.populate_file_tree()

    def on_search_changed(self, search_text):
        for shot_index in range(self.shot_list.count()):
            shot_item = self.shot_list.item(shot_index)
            if(not search_text.lower() in shot_item.text().lower()):
                shot_item.setHidden(True)
            else:
                shot_item.setHidden(False)

    def create_shot_side_panel(self):
        # self.shot_side_widget = QScrollArea()
        # self.shot_side_widget.setStyleSheet("QWidget {background-color: #1b1e20; border-radius: 15px;}")
        # self.shot_side_secondary_layout = QVBoxLayout(self.shot_side_widget)
        # self.shot_page_layout.addWidget(self.shot_side_widget)

        self.shot_side_widget = QScrollArea()
        # self.shot_side_widget.setStyleSheet("QScrollArea {background-color: #1b1e20; border-radius: 15px;}")
        self.shot_side_widget.setStyleSheet("""
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


        # Create a content widget and a layout for it
        content_widget = QWidget()
        self.shot_page_layout.addWidget(content_widget)
        self.shot_side_secondary_layout = QVBoxLayout(content_widget)  # Set the layout to the content widget

        # Then set the content widget to the scroll area
        self.shot_side_widget.setWidget(content_widget)
        self.shot_side_widget.setWidgetResizable(True)  # Make the content widget resizable

        self.shot_page_layout.addWidget(self.shot_side_widget)

        # title
        section_title = QLabel("Shot Info")
        section_title.setFont(self.header_font)
        # section_title.setMinimumWidth(200)
        self.shot_side_secondary_layout.addWidget(section_title)



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
        self.shot_edit_button.setStyleSheet(style_sheet)
        self.shot_side_secondary_layout.addWidget(self.shot_edit_button)


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

    def on_shot_add(self):
        # file_utils.new_shot("SH030")
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

    def on_shot_delete(self):
        print('shot delete')
        quick_dialog(self, "Deleting shots isn't implemented yet")

    def populate_shot_list(self):
        # check for previous selection
        prev_selected_items = self.shot_list.selectedItems()
        has_prev_selection = len(prev_selected_items)!=0
        if(has_prev_selection):
            prev_selected_text = prev_selected_items[0].text()

        # clear contents
        self.shot_list.clear()

        # create new shots
        self.set_shots()
        for shot in self.shots:
            item_label = "Shot " + shot["formatted_name"]
            item = QListWidgetItem(item_label, self.shot_list)
            item.setData(role_mapping["shot_data"], shot)
            thumbnail_path = os.path.join(shot["dir"],"thumbnail.png")
            # print("thumbnail path", thumbnail_path)
            item.setIcon(QIcon(thumbnail_path))

            if(has_prev_selection and item_label == prev_selected_text):
                item.setSelected(True)
            
        if(not has_prev_selection):
            self.shot_list.setCurrentRow(0)

            
