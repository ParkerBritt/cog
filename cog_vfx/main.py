from PySide6.QtWidgets import QApplication
from .utils import file_utils
from .interface import MainWindow
import sys

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
