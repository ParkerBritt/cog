from ....abstract_panels import AbstractWorkspacePanel


class ShotWorkspacePanel(AbstractWorkspacePanel):
    def __init__(self, shot_controller):
        super().__init__(shot_controller)
        self.shot_controller = shot_controller
        self.element_type = "shot"

    def init_role_buttons(self):
        self.create_role_button("FX", "fx")
        anim_button = self.create_role_button("Anim", "anim")
        self.create_role_button("Comp", "comp")
        # default button
        anim_button.click()
