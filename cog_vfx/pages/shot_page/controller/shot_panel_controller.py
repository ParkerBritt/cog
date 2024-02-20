from PySide6.QtCore import QObject, Signal

from ..utils import shot_utils
from .shot_definition import ShotDefinition


class ShotPanelController(QObject):
    on_element_selection_changed = Signal(ShotDefinition)

    def __init__(self):
        super().__init__()

        self.shots = []
        self.elements = self.shots
        self.selected_elements = None
        self.set_shots()
        # signals
        self.new_get_shots()
        print(self.shots)

    def change_element_selection(self, shot=None):
        self.on_element_selection_changed.emit(shot)

    def set_shots(self):
        self.shots_old = shot_utils.get_shots()

    def get_shots(self):
        return self.shots_old

    def new_get_shots(self):
        print("Fetching shots")
        found_shots = shot_utils.get_shots()
        if not isinstance(found_shots, list):
            return
        for shot in found_shots:
            new_shot = ShotDefinition(**shot)
            self.shots.append(new_shot)

        # print(shot_utils.get_shots())

    def get_selected_shot_data(self):
        pass
