import os
from . import AbstractListPanel
from ..utils.file_utils import get_pkg_asset_path
from ..utils import shot_utils
from ..utils.houdini_wrapper import launch_houdini, launch_hython
from ..utils.interface_utils import get_list_widget_data
from ..dialogs import SelectRenderNodeDialog
from ..utils import filter_env_vars


# handle actions
def handle_action_open(element_list):
    print("Opening Shot")
    shot_data = get_list_widget_data(element_list)
    scene_path = os.path.join(shot_data["dir"],"scene.hipnc")

    # filter shot data into valid environment variables for the scene to use
    additional_vars = filter_env_vars(shot_data, "shot")
    if(os.path.exists(scene_path)):
        launch_houdini(scene_path, additional_vars=additional_vars)
    else:
        print("Error:", shot_data["file_name"],"has no scene.hipnc file")


def handle_action_delete():
    print("Deleting Shot")

def handle_action_render(parent):
    element_list = parent.element_list
    print("Rendering Shot")
    shot_data = get_list_widget_data(element_list)
    scene_path = os.path.join(shot_data["dir"],"scene.hipnc")
    if(os.path.exists(scene_path)):
        select_render_node = SelectRenderNodeDialog(parent, scene_path, shot_data)
        # select_render_node.exec()
        print("created window")

        
        return
        # launch_hython(scene_path, shot_data, get_pkg_asset_path("husk_render.py"))
    else:
        print("Error:", shot_data["file_name"],"has no scene.hipnc file")



class ShotListPanel(AbstractListPanel):
    def __init__(self, tree_widget=None, info_widget=None, parent=None):
        super().__init__(tree_widget, info_widget, parent)
        self.context_menu_actions()
        self.element_page_label.setText("Shots")

    def context_menu_actions(self):
        self.context_menu.addAction("Open Shot", lambda: handle_action_open(self.element_list))
        self.context_menu.addAction("Render Shot", lambda: handle_action_render(self))
        self.context_menu.addAction("Delete Shot", lambda: print("not yet implemented"))


    def set_elements(self):
        self.elements = shot_utils.get_shots()

    def on_element_add(self):
        print("shot add dialog")
        self.new_shot_dialog = NewElementDialog(self.element_list, edit=False, element_name="Shots")
        self.new_shot_dialog.add_spin_box("FPS", "fps", 10)
        self.new_shot_dialog.add_double_spin_box("Frame Range", ("start_frame", "end_frame"), 1001, 1100)
        self.new_shot_dialog.exec()

    def old_on_elemend_add(self):
        # file_utils.new_object("SH030")
        # self.populate_object_list()
        print('shot add')
        self.new_object = NewShotInterface(self, self.object_list)
        # self.new_object.finished.connect(self.on_object_add_finished)
        # self.new_object.show()
        self.new_object.exec()
