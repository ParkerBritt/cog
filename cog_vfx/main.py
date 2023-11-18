from PySide6.QtWidgets import QApplication

# Conditional import
if __name__ == "__main__":
    from interface import MainWindow  # Absolute import for direct script run
else:
    from .interface import MainWindow  # Relative import for package use

def main():
    app = QApplication([])
    mainWin = MainWindow()
    mainWin.show()
    app.exec()

if __name__ == '__main__':
    main()
