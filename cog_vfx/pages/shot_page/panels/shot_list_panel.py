import os

from ....abstract_panels import AbstractListPanel
from ....utils import filter_env_vars
from ....utils.file_utils import get_pkg_asset_path
from ....utils.houdini_wrapper import launch_houdini
from ....utils.interface_utils import get_list_widget_data
from ..dialogs import SelectRenderNodeDialog
from ..dialogs.new_shot_dialog import NewShotDialog
from ..utils import shot_utils


class ShotListPanel(AbstractListPanel):
    def __init__(
        self, shot_controller, tree_widget=None, info_widget=None, parent=None
    ):
        self.shot_controller = shot_controller
        super().__init__(
            self.shot_controller, tree_widget, info_widget, parent, object_type="shot"
        )
        self.context_menu_actions()

    def context_menu_actions(self):
        self.context_menu.addAction(
            "Open Shot", lambda: handle_action_open(self.element_list)
        )
        self.context_menu.addAction("Edit Shot", lambda: self.on_element_edit())
        self.context_menu.addAction("Render Shot", lambda: handle_action_render(self))
        self.context_menu.addAction("Delete Shot", lambda: print("not yet implemented"))

    def get_elements(self, element_name_filter):
        return shot_utils.get_shots(element_name_filter)

    def set_elements(self):
        self.elements = self.shot_controller.get_shots()

    def on_element_add(self):
        self.new_shot_dialog = NewShotDialog(
            self.element_list, edit=False, info_widget=self.info_widget, qt_parent=self
        )
        self.new_shot_dialog.exec()

        finished_status = self.new_shot_dialog.finished_status
        if finished_status == 0:  # if new shot created
            new_items = self.populate_element_list(self.new_shot_dialog.new_shot_dir)
            if len(new_items) > 0:
                self.element_list.setCurrentItem(new_items[0])

    def on_element_edit(self):
        selected_items = self.element_list.selectedItems()
        if len(selected_items) == 0:
            print("no shot selected for editing")
            return

        element_list = self.element_list
        selected_shot_data = get_list_widget_data(element_list)

        self.edit_shot_window = NewShotDialog(
            self.element_list, edit=True, info_widget=self.info_widget, qt_parent=self
        )
        self.edit_shot_window.exec()


# handle actions
def handle_action_open(element_list):
    print("Opening Shot")
    shot_data = get_list_widget_data(element_list)
    if not shot_data:
        print("not item selected")
        return
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
    if not shot_data:
        print("not item selected")
        return
    scene_path = os.path.join(shot_data["dir"], "scene.hipnc")
    if os.path.exists(scene_path):
        select_render_node = SelectRenderNodeDialog(parent, scene_path, shot_data)
        # select_render_node.exec()
        print("created window")

        return
        # launch_hython(scene_path, shot_data, get_pkg_asset_path("husk_render.py"))
    else:
        print("Error:", shot_data["file_name"], "has no scene.hipnc file")
