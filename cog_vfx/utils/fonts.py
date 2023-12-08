from PySide6.QtGui import QFont
def get_fonts():
    header_font = QFont()
    header_font.setPointSize(12)


    fonts = {"header":header_font}
    return fonts

