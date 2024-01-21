from PySide6.QtWidgets import QLabel, QLineEdit, QTabBar, QVBoxLayout, QWidget


class ConfigPage(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        self.tab_bar = QTabBar()
        self.tab_bar.addTab("hello")
        self.tab_bar.addTab("world")
        self.main_layout.addWidget(self.tab_bar)
