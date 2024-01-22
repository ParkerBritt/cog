from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

from ....installers import environment_setup


class EnvironmentTab(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def make_settings(self):
        # environment setup button
        self.env_setup_button = QPushButton("Setup Environment")
        self.main_layout.addWidget(self.env_setup_button)
        self.env_setup_button.clicked.connect(environment_setup.install_sequence)

    def initUI(self):
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        self.main_layout.addWidget(QLabel("Environment Tab"))

        self.make_settings()
