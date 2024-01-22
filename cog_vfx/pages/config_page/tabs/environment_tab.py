from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class EnvironmentTab(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        self.main_layout.addWidget(QLabel("Environment Tab"))


#         self.setStyleSheet(
#             """QWidget {
#     background-color: #1d2023;
# }
# """
#         )
