import os
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QListWidget, QPushButton, QListWidgetItem, QProgressBar
from PySide6.QtCore import Qt, QThread, Signal
from ..utils.file_utils import get_pkg_asset_path
from ..utils.houdini_wrapper import launch_houdini, launch_hython
from ..utils import filter_env_vars

class RenderThread(QThread):
    progress_update = Signal(int)
    frame_update = Signal(str)
    finished = Signal()

    def __init__(self, scene_path, shot_data, render_node_path):
        super(RenderThread, self).__init__()
        self.scene_path = scene_path
        self.shot_data = shot_data
        self.node_path = render_node_path 
        self.process = None

    def run(self):
        # prepare script to run
        script = "import sys; module_directory = '{module_directory}';sys.path.append(module_directory); import husk_render; husk_render.exec_render_node('{scene_path}', '{node_path}')"
        module_directory = os.path.join(get_pkg_asset_path(""), "utils")
        script = script.format(module_directory=module_directory, scene_path=self.scene_path, node_path=self.node_path)

        additional_vars = filter_env_vars(self.shot_data, "shot")
        self.process = launch_hython(script=script, live_mode=True, additional_vars=additional_vars)
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
        module_directory = os.path.join(get_pkg_asset_path(""), "utils")
        script = script.format(module_directory=module_directory, scene_path = self.scene_path)

        # filter shot data into valid environment variables for the scene to use
        additional_vars = filter_env_vars(self.shot_data, "shot")
        # run script through hython
        self.get_render_nodes_process = launch_hython(script=script, additional_vars=additional_vars)

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





