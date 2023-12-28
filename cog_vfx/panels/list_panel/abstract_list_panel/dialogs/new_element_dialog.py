from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QFont, QIcon, QPixmap
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .....utils.interface_utils import get_list_widget_data


class NewElementDialog(QDialog):
    def __init__(
        self,
        element_list,
        edit=False,
        element_name="element",
        parent=None,
        info_widget=None,
    ):
        super().__init__(parent)
        self.info_widget = info_widget
        self.element_name = element_name
        self.setWindowTitle("New " + self.element_name)
        self.resize(400, 600)
        self.element_list = element_list
        self.input_fields = []

        # edit mode stuff
        self.edit_mode = edit
        self.existing_element_data = get_list_widget_data(element_list)

        self.initUI()

    def initUI(self):
        self.mainLayout = QVBoxLayout()
        self.setLayout(self.mainLayout)
        # add stretch
        self.mainLayout.addStretch()

        # bottom buttons
        bottom_buttons_layout = QHBoxLayout()
        bottom_button_min_size = (50, 30)
        ok_button = QPushButton("ok")
        cancel_button = QPushButton("cancel")
        ok_button.clicked.connect(self.on_ok_pressed)
        cancel_button.clicked.connect(self.on_cancel_pressed)
        ok_button.setMinimumSize(*bottom_button_min_size)
        cancel_button.setMinimumSize(*bottom_button_min_size)
        bottom_buttons_layout.addStretch()
        # add widgets
        bottom_buttons_layout.addWidget(ok_button)
        bottom_buttons_layout.addWidget(cancel_button)
        self.mainLayout.addLayout(bottom_buttons_layout)

    def exec(self):
        if self.existing_element_data:
            self.fill_existing_values()

        return super().exec()

    def add_spin_box(
        self, label, update_key, default_value=1, min_value=0, max_value=9999
    ):
        self.mainLayout.insertWidget(self.mainLayout.count() - 2, QLabel(label))
        spin_box = QSpinBox()
        self.mainLayout.insertWidget(self.mainLayout.count() - 2, spin_box)

        spin_box.setValue(default_value)
        if min_value:
            spin_box.setMinimum(min_value)
        if max_value:
            spin_box.setMaximum(max_value)
        self.input_fields.append(
            {
                "widget": spin_box,
                "update_key": update_key,
            }
        )
        return spin_box

    def add_edit_box(self, label, update_key):
        self.mainLayout.insertWidget(self.mainLayout.count() - 2, QLabel(label))
        edit_box = QTextEdit()
        self.mainLayout.insertWidget(self.mainLayout.count() - 2, edit_box)

        self.input_fields.append(
            {
                "widget": edit_box,
                "update_key": update_key,
            }
        )
        return edit_box

    def add_double_spin_box(
        self,
        label,
        update_keys,
        default_value1=1,
        default_value2=10,
        min_value=0,
        max_value=9999,
    ):
        self.mainLayout.insertWidget(self.mainLayout.count() - 2, QLabel(label))
        layout = QHBoxLayout()
        spin_box1 = QSpinBox()
        spin_box2 = QSpinBox()
        layout.addWidget(spin_box1)
        layout.addWidget(spin_box2)
        self.mainLayout.insertLayout(self.mainLayout.count() - 2, layout)

        if min_value:
            spin_box1.setMinimum(min_value)
        if min_value:
            spin_box2.setMinimum(min_value)
        if max_value:
            spin_box1.setMaximum(max_value)
        if max_value:
            spin_box2.setMaximum(max_value)

        spin_box1.setValue(default_value1)
        spin_box2.setValue(default_value2)
        self.input_fields.append(
            {
                "widget": spin_box1,
                "update_key": update_keys[0],
            }
        )
        self.input_fields.append(
            {
                "widget": spin_box2,
                "update_key": update_keys[1],
            }
        )
        return spin_box1, spin_box2

    def get_new_element_data(self):
        new_element_data = {}
        for field in self.input_fields:
            field_widget = field["widget"]
            field_key = field["update_key"]
            field_value = ""
            if isinstance(field_widget, QSpinBox):  # QSpinBox
                field_value = field_widget.text()
            elif isinstance(field_widget, QTextEdit):
                field_value = field_widget.toPlainText()
            new_element_data.update({field_key: field_value})

        #     print("FIELD", field)
        # print("New Element Data", new_element_data)
        return new_element_data

    def on_ok_pressed(self):
        self.finished_status = 0
        self.new_element_data = self.get_new_element_data()
        self.on_exit()
        self.close()

    def on_exit(self):
        print("on_exit method meant to be overwritten")

    def on_cancel_pressed(self):
        self.finished_status = 1
        self.close()

    def fill_existing_values(self):
        for field in self.input_fields:
            self.fill_value(field["widget"], field["update_key"])

    #
    # def fill_existing_values(self):
    #     self.fill_value(self.select_start_frame, "start_frame")
    #     self.fill_value(self.select_end_frame, "end_frame")
    #     self.fill_value(self.element_description_box, "description")
    #     self.fill_value(self.select_res_width, "res_width")
    #     self.fill_value(self.select_res_height, "res_height")
    #     self.fill_value(self.select_fps, "fps")

    def fill_value(self, widget, value):
        # check that existing element data is list rather than a non zero error return
        if value in self.existing_element_data and isinstance(
            self.existing_element_data, list
        ):
            if isinstance(widget, QTextEdit):
                widget.setPlainText(self.existing_element_data[value])
            elif isinstance(widget, QSpinBox):
                widget.setValue(self.existing_element_data[value])
