from PySide6.QtWidgets import QApplication
from . import file_utils
import sys

# Conditional import
if __name__ == "__main__":
    from interface import MainWindow  # Absolute import for direct script run
else:
    from .interface import MainWindow  # Relative import for package use


def launch_app():
    app = QApplication([])
    file_utils.software_update(app)
    mainWin = MainWindow()
    mainWin.show()
    app.exec()
    return app

def main():
    launch_app()

if __name__ == '__main__':
    main()
