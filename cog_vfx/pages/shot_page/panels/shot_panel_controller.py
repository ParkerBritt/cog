from PySide6.QtCore import QObject, Signal

from ..utils import shot_utils


class ShotPanelController(QObject):
    on_element_selection_changed = Signal()

    def __init__(self):
        super().__init__()

        self.set_shots()
        # signals
        self.on_element_selection_changed.connect(
            lambda: print("\n\n\n\n\n\n\nELEMENT CHANGED TEST SUCCESSFULL!!!!")
        )

    def change_element_selection(self):
        self.on_element_selection_changed.emit()

    def set_shots(self):
        self.shots = shot_utils.get_shots()

    def get_shots(self):
        return self.shots

    def get_selected_shot_data(self):
        pass
