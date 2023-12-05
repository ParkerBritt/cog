import os, json
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QStackedLayout, QListWidget, QSizePolicy, QMenu, QSplitter, QListWidgetItem, QSpinBox, QTextEdit, QDialog, QScrollArea, QProgressBar, QLineEdit, QSpacerItem
from PySide6.QtGui import QIcon, QFont, QPixmap
from PySide6.QtCore import QSize, Qt, QThread, Signal
import pkg_resources
from . import file_utils, utils
from .houdini_wrapper import launch_houdini, launch_hython
from .interface_utils import quick_dialog

role_mapping = {
    "asset_data": Qt.UserRole + 1,
}

PACKAGE_NAME = "cog_vfx"
def get_asset_path(path):
    return pkg_resources.resource_filename(PACKAGE_NAME, path)

def get_asset_data(asset_list=None, item=None):
    assets = utils.get_assets()
    if(item == None):
        selected_asset = asset_list.selectedItems()
        if(len(selected_asset)>0):
            selected_asset = selected_asset[0]
        else:
            return None
    else:
        selected_asset = item

    return selected_asset.data(role_mapping["asset_data"])



class RenderThread(QThread):
    progress_update = Signal(int)
    frame_update = Signal(str)
    finished = Signal()

    def __init__(self, scene_path, asset_data, render_node_path):
        super(RenderThread, self).__init__()
        self.scene_path = scene_path
        self.asset_data = asset_data
        self.node_path = render_node_path 

    def run(self):
        # prepare script to run
        script = "import sys; module_directory = '{module_directory}';sys.path.append(module_directory); import husk_render; husk_render.exec_render_node('{scene_path}', '{node_path}')"
        script = script.format(module_directory=get_asset_path(""), scene_path=self.scene_path, node_path=self.node_path)

        self.process = launch_hython(self.scene_path, self.asset_data, script=script, live_mode=True)
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
    def __init__(self, parent, scene_path, asset_data, render_node_path):
        super(RenderLoading, self).__init__(parent)
        self.scene_path = scene_path
        self.asset_data = asset_data
        # self.subprocess_thread = subprocess_thread

        self.initUI()
        self.subprocess_thread = RenderThread(self.scene_path, self.asset_data, render_node_path)
        self.subprocess_thread.progress_update.connect(self.updateProgressBar)
        self.subprocess_thread.frame_update.connect(self.updateFrame)
        self.subprocess_thread.finished.connect(self.closeDialog)
        self.subprocess_thread.start()

    def initUI(self):
        self.progressBar = QProgressBar(self)
        self.setMaximumSize(400, 50)
        layout = QVBoxLayout()
        # layout.addWidget(QLabel("Frame Progress"))
        self.frame_label = QLabel("Render Setup")
        layout.addWidget(self.frame_label)
        layout.addWidget(self.progressBar)
        self.setLayout(layout)
        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle("Render Progress")

    def updateProgressBar(self, value):
        self.progressBar.setValue(value)

    def updateFrame(self, value):
        self.frame_label.setText("Frame: " + value)

    def closeDialog(self):
        self.close()

    def closeEvent(self, event):
        self.subprocess_thread.terminate_process()
        event.accept()


# populate render list on a separate thread as to not hault the process
class PopulateListThread(QThread):
    finished = Signal(list)

    def __init__(self, scene_path, asset_data):
        QThread.__init__(self)
        self.scene_path = scene_path
        self.asset_data = asset_data

    def run(self):
        script = "import sys; module_directory = '{module_directory}';sys.path.append(module_directory); import husk_render; husk_render.get_render_nodes('{scene_path}')"
        script = script.format(module_directory=get_asset_path(""), scene_path = self.scene_path)
        # run script through hython
        self.get_render_nodes_process = launch_hython(self.scene_path, self.asset_data, script=script, set_vars=False)

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
    def __init__(self, parent=None, scene_path=None, asset_data=None):
        super(SelectRenderNodeDialog, self).__init__(parent)
        self.scene_path = scene_path
        self.asset_data = asset_data

        # start thread
        self.populate_list_thread = PopulateListThread(self.scene_path, self.asset_data)
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
        render_loading = RenderLoading(self, self.scene_path, self.asset_data, sel_layer_path)
        render_loading.show()




class AssetListWidget(QListWidget):
    def __init__(self, parent=None):
        super(AssetListWidget, self).__init__(parent)

    def contextMenuEvent(self, event):
        contextMenu = QMenu(self)

        # Check if right-click is on an item
        item = self.itemAt(event.pos())
        if item is not None:
            # Add "Open Asset" action only if clicked on an item
            action_open = contextMenu.addAction("Open Asset")
            action_render = contextMenu.addAction("Render Asset")
            action_delete = contextMenu.addAction("Delete Asset")
            asset_data = get_asset_data(item=item)

        action = contextMenu.exec_(self.mapToGlobal(event.pos()))


        if item is not None:
            if action == action_open:
                self.handle_action_open(asset_data)
            elif action == action_delete:
                self.handle_action_delete()
            elif action == action_render:
                self.handle_action_render(asset_data)

    def handle_action_open(self, asset_data):
        print("Opening Asset")
        look_path = os.path.join(asset_data["dir"],"look", "main", "look.hipnc")
        if(os.path.exists(look_path)):
            launch_houdini(look_path, asset_data)
        else:
            print("Error:", asset_data["file_name"],"has no look.hipnc file")


    def handle_action_delete(self):
        print("Deleting Asset")

    def handle_action_render(self, asset_data):
        print("Rendering Asset")
        scene_path = os.path.join(asset_data["dir"],"scene.hipnc")
        if(os.path.exists(scene_path)):
            select_render_node = SelectRenderNodeDialog(self, scene_path, asset_data)
            # select_render_node.exec()
            print("created window")

            
            return
            # launch_hython(scene_path, asset_data, get_asset_path("husk_render.py"))
        else:
            print("Error:", asset_data["file_name"],"has no scene.hipnc file")

class NewAssetInterface(QDialog):
    def __init__(self, parent=None, asset_list=None, edit=False, asset_data=None):
        super(NewAssetInterface, self).__init__(parent)
        self.setWindowFlags(Qt.Window)
        self.setWindowTitle("New Asset")
        self.resize(400,600)
        self.asset_list = asset_list

        # edit mode stuff
        self.edit_mode=edit
        self.existing_asset_data = asset_data

        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Asset Number
        self.layout.addWidget(QLabel("Asset Name"))
        self.select_asset_name = QLineEdit()
        if(self.edit_mode==True):
            print("asset_list", self.asset_list)
            asset_data = get_asset_data(self.asset_list)
            asset_name = asset_data["name"] if "name" in asset_data else ""
            self.select_asset_name.setText(asset_name)
        self.layout.addWidget(self.select_asset_name)

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

        # asset description
        self.layout.addWidget(QLabel("Asset Description"))
        self.asset_description_box = QTextEdit()
        self.layout.addWidget(self.asset_description_box)

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

        if(self.existing_asset_data):
            self.fill_existing_values()

    def fill_existing_values(self):
        self.fill_value(self.select_start_frame, "start_frame")
        self.fill_value(self.select_end_frame, "end_frame")
        self.fill_value(self.asset_description_box, "description")
        self.fill_value(self.select_res_width, "res_width")
        self.fill_value(self.select_res_height, "res_height")
        self.fill_value(self.select_fps, "fps")

    def fill_value(self, widget, value):
        if(value in self.existing_asset_data):
            if(isinstance(widget, QTextEdit)):
                widget.setPlainText(self.existing_asset_data[value])
            elif(isinstance(widget, QSpinBox)):
                widget.setValue(self.existing_asset_data[value])

    # ----- SIGNALS ------- 

    def on_ok_pressed(self):
        print("ok_pressed")
        # get asset data in variables from widgets
        self.finished_status = 0

        start_frame = self.select_start_frame.value()
        end_frame = self.select_end_frame.value()
        asset_name = self.select_asset_name.text()
        res_width = self.select_res_width.value()
        res_height = self.select_res_height.value()
        fps = self.select_fps.value()
        asset_desc = self.asset_description_box.toPlainText()
        self.asset_file_name = asset_name.replace(" ", "_").lower()

        # format asset data in dictionary
        self.new_asset_data = {
            "name":asset_name,
            "file_name":self.asset_file_name,
            "start_frame":start_frame,
            "end_frame":end_frame,
            "description":asset_desc,
            "res_width":res_width,
            "res_height":res_height,
            "fps":fps
        }


        self.close()

    def on_cancel_pressed(self):
        self.finished_status = 1
        self.close()

# ------------- SHOT PAGE -----------------

class AssetPage(QWidget):
    def __init__(self, parent=None):
        super(AssetPage, self).__init__(parent)

        # make font
        self.header_font = QFont()
        self.header_font.setPointSize(12)

        self.set_assets()
        self.create_asset_page()

    def set_assets(self):
        self.assets = utils.get_assets()


    def create_asset_page(self):
        # Create content for Tab 1
        self.asset_page_layout = QHBoxLayout(self)
        self.asset_central_layout = QVBoxLayout()

        self.asset_page_layout.addLayout(self.asset_central_layout)

        self.create_asset_side_panel()

        # Label
        self.asset_page_label = QLabel("Assets")
        self.asset_page_label.setFont(self.header_font)
        self.asset_central_layout.addWidget(self.asset_page_label)

        # Search Bar
        self.asset_search_bar = QLineEdit()
        self.asset_search_bar.setTextMargins(5, 1, 5, 1)
        search_bar_font = QFont()
        search_bar_font.setPointSize(12)
        self.asset_search_bar.setFont(search_bar_font)
        self.asset_search_bar.textChanged.connect(self.on_search_changed)
        self.asset_central_layout.addWidget(self.asset_search_bar)
        spacer = QSpacerItem(20, 10, QSizePolicy.Minimum, QSizePolicy.Preferred)
        self.asset_central_layout.addItem(spacer)

        # Asset list
        self.asset_list = AssetListWidget()
        self.asset_list.setSortingEnabled(True)
        self.asset_list.itemSelectionChanged.connect(self.update_asset_info)
        self.asset_list.setAlternatingRowColors(True)
        self.asset_list.setIconSize(QSize(500,50))
        self.populate_asset_list()
        self.asset_central_layout.addWidget(self.asset_list)

        # buttons
        bottom_buttons_layout = QHBoxLayout()
        bottom_buttons_layout.addStretch()


        self.asset_refresh_button = QPushButton("Refresh")
        # self.asset_refresh_button.setMaximumWidth(25)
        self.asset_refresh_button.clicked.connect(self.populate_asset_list)
        bottom_buttons_layout.addWidget(self.asset_refresh_button)

        self.asset_add_button = QPushButton("+")
        self.asset_add_button.setMaximumWidth(25)
        self.asset_add_button.clicked.connect(self.on_asset_add)
        bottom_buttons_layout.addWidget(self.asset_add_button)

        self.asset_delete_button = QPushButton("-")
        self.asset_delete_button.setMaximumWidth(25)
        self.asset_delete_button.clicked.connect(self.on_asset_delete)
        bottom_buttons_layout.addWidget(self.asset_delete_button)

        self.asset_central_layout.addLayout(bottom_buttons_layout)

    def on_search_changed(self, search_text):
        for asset_index in range(self.asset_list.count()):
            asset_item = self.asset_list.item(asset_index)
            if(not search_text.lower() in asset_item.text().lower()):
                asset_item.setHidden(True)
            else:
                asset_item.setHidden(False)

    def create_asset_side_panel(self):
        # self.asset_side_widget = QScrollArea()
        # self.asset_side_widget.setStyleSheet("QWidget {background-color: #1b1e20; border-radius: 15px;}")
        # self.asset_side_layout = QVBoxLayout(self.asset_side_widget)
        # self.asset_page_layout.addWidget(self.asset_side_widget)

        self.asset_side_widget = QScrollArea()
        # self.asset_side_widget.setStyleSheet("QScrollArea {background-color: #1b1e20; border-radius: 15px;}")
        self.asset_side_widget.setStyleSheet("""
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
        self.asset_side_layout = QVBoxLayout(content_widget)  # Set the layout to the content widget

        # Then set the content widget to the scroll area
        self.asset_side_widget.setWidget(content_widget)
        self.asset_side_widget.setWidgetResizable(True)  # Make the content widget resizable

        self.asset_page_layout.addWidget(self.asset_side_widget)


        # title
        section_title = QLabel("Asset Info")
        section_title.setFont(self.header_font)
        # section_title.setMinimumWidth(200)
        self.asset_side_layout.addWidget(section_title)



        # asset thumbnail
        self.asset_thumbnail = QLabel()
        self.asset_thumbnail_size = (192*1.3, 108*1.3)
        self.asset_thumbnail.setMaximumSize(*self.asset_thumbnail_size)
        self.asset_side_layout.addWidget(self.asset_thumbnail)

        # general asset data container
        self.asset_render_data_widget = QWidget()
        self.asset_render_data_widget.setStyleSheet("QWidget {background-color: #2a2e32; border-radius: 15px;}")
        asset_render_data_layout = QVBoxLayout(self.asset_render_data_widget)
        self.asset_side_layout.addWidget(self.asset_render_data_widget)
        general_asset_data_title = QLabel("Render Data")
        general_asset_data_title.setFont(self.header_font)
        asset_render_data_layout.addWidget(general_asset_data_title)

        # asset name
        self.asset_name_label = QLabel("SH")
        self.asset_name_label.hide()
        asset_render_data_layout.addWidget(self.asset_name_label)

        # poly_count 
        self.asset_poly_count_label = QLabel("Poly Count:")
        asset_render_data_layout.addWidget(self.asset_poly_count_label)

        # codec

        # date recorded

        # asset description
        self.asset_description_widget = QWidget()
        self.asset_description_widget.setStyleSheet("QWidget {background-color: #2a2e32; border-radius: 15px;}")
        asset_description_layout = QVBoxLayout(self.asset_description_widget)
        self.asset_side_layout.addWidget(self.asset_description_widget)

        description_title = QLabel("Asset Description")
        description_title.setFont(self.header_font)
        self.asset_description_title = description_title
        asset_description_layout.addWidget(self.asset_description_title)
        self.asset_description_label = QLabel("")
        asset_description_layout.addWidget(self.asset_description_label)

        self.asset_description_widget.hide()


        self.asset_side_layout.addStretch()

        self.asset_edit_button = QPushButton("Edit")
        self.asset_edit_button.clicked.connect(self.on_asset_edit)
        self.asset_edit_button.setStyleSheet(utils.get_style_sheet())
        self.asset_side_layout.addWidget(self.asset_edit_button)


    def update_asset_info(self):
        # setup
        selected_items = self.asset_list.selectedItems()
        if(len(selected_items)==0):
            return
        selected_asset = selected_items[0]
        sel_asset_data = get_asset_data(item=selected_asset) 
        print("sel_asset_data", sel_asset_data)

        # asset name
        self.asset_name_label.setText("Name: " + sel_asset_data["formatted_name"])
        self.asset_name_label.show()

        # asset thumbnail
        thumbnail_dir = os.path.join(sel_asset_data["dir"], "thumbnail.png")
        if(not os.path.exists(thumbnail_dir)):
            thumbnail_dir = get_asset_path("assets/icons/missing_asset_thumbnail.png")
        pixmap = QPixmap(os.path.join(thumbnail_dir))
        pixmap = pixmap.scaled(QSize(*self.asset_thumbnail_size), Qt.KeepAspectRatioByExpanding, Qt.FastTransformation)
        self.asset_thumbnail.setPixmap(pixmap)

        if("poly_count" in sel_asset_data):
            self.asset_poly_count_label.setText(f'Poly Count: {sel_asset_data["poly_count"]}')
            self.asset_poly_count_label.show()
        else:
            self.asset_poly_count_label.hide()


        # asset description
        if("description" in sel_asset_data and sel_asset_data["description"]!=""):
            self.asset_description_widget.show()
            self.asset_description_label.setText(sel_asset_data["description"])
        else:
            self.asset_description_widget.hide()



    # def update_asset_info_label(self, widget, text, check_values, sel_asset_data):
    #     set_visible = True
    #     if(not isinstance(check_values, list)):
    #         check_values = [check_values]
    #
    #     for value in check_values:
    #         if(not value in sel_asset_data):
    #             widget.hide()
    #             return
    #
    #     if(isinstance(widget, QLabel)):
    #         widget.setText(text)
    #     widget.show()

    def on_asset_add(self):
        # file_utils.new_asset("SH030")
        # self.populate_asset_list()
        print('asset add')
        self.new_asset = NewAssetInterface(self, self.asset_list)
        self.new_asset.finished.connect(self.on_asset_add_finished)
        # self.new_asset.show()
        self.new_asset.exec()


    def on_asset_edit(self):
        selected_items = self.asset_list.selectedItems()
        if(len(selected_items)==0):
            print("no asset selected for editing")
            return

        selected_asset_data = selected_items[0].data(role_mapping["asset_data"])

        self.edit_asset_window = NewAssetInterface(self, self.asset_list, edit=True, asset_data=selected_asset_data)
        self.edit_asset_window.finished.connect(self.on_asset_edit_finished)
        self.edit_asset_window.exec()

    def on_asset_edit_finished(self):
        # make sure user confirmed edit by pressing ok
        finished_stats = self.edit_asset_window.finished_status
        if(finished_stats != 0):
            return

        # setup variables
        selected_asset = self.asset_list.selectedItems()[0]
        old_asset_data = selected_asset.data(role_mapping["asset_data"])
        print("OLD SHOT DATA", old_asset_data)
        asset_dir = old_asset_data["dir"]
        asset_name = old_asset_data["file_name"]
        edit_asset_data = self.edit_asset_window.new_asset_data



        # move asset
        if(not "name" in old_asset_data or old_asset_data["name"] != edit_asset_data["name"]):
            print(old_asset_data["name"] +" != " + edit_asset_data["name"])
            print("asset name changed, moving asset")
            # print(f"old_asset_data: {old_asset_data} \nnew_asset_data: {new_asset_data}")
            dest_asset_name = str(edit_asset_data["name"])
            dest_dir = file_utils.move_asset(self, asset_name, dest_asset_name)
            # check if move was successful
            if(not dest_dir):
                edit_asset_data.pop("name")
                return

            # reformat list widget
            asset_dir = dest_dir
            asset_name = os.path.basename(dest_dir)
            new_asset_data = utils.get_assets(asset_name)[0]
            selected_asset.setText("Asset " + new_asset_data["formatted_name"])

        # edit json
        asset_file_name = os.path.join(asset_dir, "asset_data.json")
        new_asset_data = file_utils.edit_asset_json(asset_file_name, edit_asset_data)
        new_asset_data = utils.get_assets(asset_name)[0]

        # update list item data
        print("SETTING NEW SHOT DATA", new_asset_data)
        if(new_asset_data!=0):
            selected_asset.setData(role_mapping["asset_data"], new_asset_data)
        else:
            print("can't find asset")

        # update info pannel
        self.update_asset_info()
        print("edit finished")

    def on_asset_add_finished(self):
        finished_stats = self.new_asset.finished_status
        if(finished_stats != 0):
            return
        new_asset_data = self.new_asset.new_asset_data

        asset_file_name = self.new_asset.asset_file_name
        print("creating asset", asset_file_name)
        file_utils.new_asset(self, asset_file_name, new_asset_data)

        self.populate_asset_list()

    def on_asset_delete(self):
        print('asset delete')
        quick_dialog(self, "Deleting assets isn't implemented yet")

    def populate_asset_list(self):
        # check for previous selection
        prev_selected_items = self.asset_list.selectedItems()
        has_prev_selection = len(prev_selected_items)!=0
        if(has_prev_selection):
            prev_selected_text = prev_selected_items[0].text()

        # clear contents
        self.asset_list.clear()

        # create new assets
        self.set_assets()
        for asset in self.assets:
            item_label = "Shot " + asset["formatted_name"]
            item = QListWidgetItem(item_label, self.asset_list)
            item.setData(role_mapping["asset_data"], asset)
            thumbnail_path = os.path.join(asset["dir"],"thumbnail.png")
            item.setIcon(QIcon(thumbnail_path))

            if(has_prev_selection and item_label == prev_selected_text):
                item.setSelected(True)
            
        if(not has_prev_selection):
            self.asset_list.setCurrentRow(0)
