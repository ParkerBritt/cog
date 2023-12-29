import os

from ....dialogs import SelectRenderNodeDialog
from ....utils import filter_env_vars, shot_utils
from ....utils.file_utils import get_pkg_asset_path
from ....utils.houdini_wrapper import launch_houdini, launch_hython
from ....utils.interface_utils import get_list_widget_data
from ..abstract_list_panel.abstract_list_panel import AbstractListPanel
from .dialogs.new_shot_dialog import NewShotDialog


# handle actions
def handle_action_open(element_list):
    print("Opening Shot")
    shot_data = get_list_widget_data(element_list)
    scene_path = os.path.join(shot_data["dir"], "scene.hipnc")

    # filter shot data into valid environment variables for the scene to use
    additional_vars = filter_env_vars(shot_data, "shot")
    if os.path.exists(scene_path):
        launch_houdini(scene_path, additional_vars=additional_vars)
    else:
        print("Error:", shot_data["file_name"], "has no scene.hipnc file")


def handle_action_delete():
    print("Deleting Shot")


def handle_action_render(parent):
    element_list = parent.element_list
    print("Rendering Shot")
    shot_data = get_list_widget_data(element_list)
    scene_path = os.path.join(shot_data["dir"], "scene.hipnc")
    if os.path.exists(scene_path):
        select_render_node = SelectRenderNodeDialog(parent, scene_path, shot_data)
        # select_render_node.exec()
        print("created window")

        return
        # launch_hython(scene_path, shot_data, get_pkg_asset_path("husk_render.py"))
    else:
        print("Error:", shot_data["file_name"], "has no scene.hipnc file")


class ShotListPanel(AbstractListPanel):
    def __init__(self, tree_widget=None, info_widget=None, parent=None):
        super().__init__(tree_widget, info_widget, parent, object_type="shot")
        self.context_menu_actions()

    def context_menu_actions(self):
        self.context_menu.addAction(
            "Open Shot", lambda: handle_action_open(self.element_list)
        )
        self.context_menu.addAction("Edit Shot", lambda: self.on_element_edit())
        self.context_menu.addAction("Render Shot", lambda: handle_action_render(self))
        self.context_menu.addAction("Delete Shot", lambda: print("not yet implemented"))

    def set_elements(self):
        self.elements = shot_utils.get_shots()

    def on_element_add(self):
        self.new_shot_dialog = NewShotDialog(
            self.element_list, edit=False, info_widget=self.info_widget
        )
        self.new_shot_dialog.exec()

        finished_status = self.new_shot_dialog.finished_status
        if finished_status == 0:  # if new shot created
            self.populate_element_list()

    def on_element_edit(self):
        selected_items = self.element_list.selectedItems()
        if len(selected_items) == 0:
            print("no shot selected for editing")
            return

        element_list = self.element_list
        selected_shot_data = get_list_widget_data(element_list)

        self.edit_shot_window = NewShotDialog(
            self.element_list, edit=True, info_widget=self.info_widget
        )
        self.edit_shot_window.exec()
