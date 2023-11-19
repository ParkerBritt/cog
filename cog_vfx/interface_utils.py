from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel

def quick_dialog(self=None, dialog_text=" ", title = " "):
    dialog = QDialog(self)
    dialog.setWindowTitle(title)
    dialog_layout = QVBoxLayout()
    dialog.setLayout(dialog_layout)
    dialog_layout.addWidget(QLabel(dialog_text))
    dialog.exec()

