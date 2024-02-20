from PySide6.QtCore import QObject, Signal

from ..utils import shot_utils
from .shot_definition import ShotDefinition


class ShotPanelController(QObject):
    # signals
    on_element_selection_changed = Signal(ShotDefinition)
    elements_updated_signal = Signal()

    def __init__(self):
        super().__init__()

        self.shots = []
        self.elements = self.shots
        self.selected_elements = None
        self.set_shots()
        # signals
        self.new_get_shots()
        print(self.shots)

    def get_selected_elements(self):
        return self.selected_elements

    def get_selected_element(self):
        if not self.selected_elements:
            return None
        return self.selected_elements[0]

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

    # wil add later
    def get_selected_shot_data(self):
        pass

    # -- Connect Signals --
    def connect_shots_updated(self, function):
        self.elements_updated_signal.connect(function)

    # -- Signal Triggers --
    def notify_shots_updated(self):
        self.elements_updated_signal.emit()

    def change_element_selection(self, selected_elements):
        print("setting selection to:", selected_elements)
        self.selected_elements = selected_elements
        self.on_element_selection_changed.emit(selected_elements)
