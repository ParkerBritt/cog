import sys

from PySide6.QtWidgets import QApplication

from .installers import environment_setup
from .interface import MainWindow
from .utils import file_utils


def launch_app():
    app = QApplication([])
    environment_window = (
        environment_setup.main()
    )  # assign window so it doesn't get garbage collected
    print("next hello world")
    # file_utils.software_update(app)
    # mainWin = MainWindow()
    # mainWin.show()
    app.exec()
    return app


def main():
    launch_app()


if __name__ == "__main__":
    main()
