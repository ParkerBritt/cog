from PySide6.QtWidgets import (
    QLabel,
    QLineEdit,
    QTabBar,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from .tabs import EnvironmentTab, SettingsTab


class ConfigPage(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        self.tab_bar = QTabWidget()
        environment_tab = EnvironmentTab()
        settings_tab = SettingsTab()
        self.tab_bar.addTab(environment_tab, "Environment")
        self.tab_bar.addTab(settings_tab, "Settings")
        # self.tab_bar.addTab("world")
        self.main_layout.addWidget(self.tab_bar)
