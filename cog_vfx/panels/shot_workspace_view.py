from .abstract_workspace_view import AbstractWorkspaceView

class ShotWorkspaceView(AbstractWorkspaceView):
    def __init__(self, list_panel):
        super().__init__(list_panel)

    def init_role_buttons(self):
        self.create_role_button("FX", "fx")
        anim_button = self.create_role_button("Anim", "anim")
        self.create_role_button("Comp", "comp")
        # default button
        anim_button.click()
