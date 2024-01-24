from P4 import os, platform
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
)

from ..utils.interface_utils import get_icon, get_list_widget_data


class NewElementDialog(QDialog):
    def __init__(
        self,
        element_list,
        edit=False,
        element_name="element",
        qt_parent=None,
        info_widget=None,
    ):
        super().__init__(qt_parent)
        self.qt_parent = qt_parent
        self.finished_status = 1
        self.info_widget = info_widget
        print("\n\n\n\nINFO WIDGET", info_widget)
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
        if self.existing_element_data and self.edit_mode is True:
            self.fill_existing_values()

        return super().exec()

    def add_file_selector(self, label, update_key):
        file_selector = FileSelector(parent=self, label=label)
        self.input_fields.append(
            {
                "widget": file_selector,
                "update_key": update_key,
            }
        )
        return file_selector

    def add_spin_box(
        self, label, update_key, default_value=1, min_value=0, max_value=9999
    ):
        self.mainLayout.insertWidget(self.mainLayout.count() - 2, QLabel(label))
        spin_box = QSpinBox()
        self.mainLayout.insertWidget(self.mainLayout.count() - 2, spin_box)

        if min_value:
            spin_box.setMinimum(min_value)
        if max_value:
            spin_box.setMaximum(max_value)
        spin_box.setValue(default_value)
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
            spin_box2.setMinimum(min_value)
        if max_value:
            spin_box1.setMaximum(max_value)
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
                field_value = int(field_widget.text())
            elif isinstance(field_widget, QTextEdit):
                field_value = field_widget.toPlainText()
            elif isinstance(field_widget, FileSelector):
                field_value = field_widget.get_thumbnail()
            new_element_data.update({field_key: field_value})

        #     print("FIELD", field)
        # print("New Element Data", new_element_data)
        print("NEW ELEMENT DATA", new_element_data)
        return new_element_data

    def on_ok_pressed(self):
        self.close()
        self.finished_status = 0
        self.new_element_data = self.get_new_element_data()
        self.on_exit()

    def on_exit(self):
        print("on_exit method meant to be overwritten")

    def on_cancel_pressed(self):
        self.finished_status = 1
        self.close()

    def fill_existing_values(self):
        for field in self.input_fields:
            if not "update_key" in field:
                continue
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
            self.existing_element_data, dict
        ):
            field_value = self.existing_element_data[value]
            print("setting", widget, "to value:", field_value, "update_key:", value)
            if isinstance(widget, QTextEdit):
                widget.setPlainText(field_value)
            elif isinstance(widget, QSpinBox):
                widget.setValue(int(field_value))
            else:
                print("ERROR: filling edit box, type:", type(widget), "not handled")
        else:
            print("ERROR: Failed to fill existing values of dialog")
            print(
                "value",
                value,
                "in list",
                self.existing_element_data,
                ":",
                value in self.existing_element_data,
            )


class FileSelector:
    def __init__(self, parent, label):
        self.parent = parent
        self.label = label
        self.selected_file = None
        self.initUI()

    def initUI(self):
        self.main_layout = QHBoxLayout()
        self.file_dialog = QFileDialog(self.parent)
        self.file_dialog.setNameFilter("Images (*.png *.jpg)")
        OS = platform.system()
        start_dir = os.getenv("HOME") if OS == "Linux" else os.getenv("USERPROFILE")
        if not start_dir:
            start_dir = ""
        self.file_dialog.setDirectory(start_dir)

        # dialog button
        dialog_button = QPushButton("Select " + self.label)
        dialog_button.setIcon(get_icon("folder_open_white.png"))
        dialog_button.clicked.connect(self.select_file)
        self.open_file_dialog_button = dialog_button
        self.main_layout.addWidget(dialog_button)

        file_path_line = QLineEdit()
        file_path_line.editingFinished.connect(self.on_file_path_updated)
        file_path_line.setPlaceholderText(self.label + " Path...")
        self.file_path_line = file_path_line
        self.main_layout.addWidget(file_path_line)
        # self.file_dialog.setFileMode(QFileDialog.AnyFile)
        # set working directory

        self.parent.mainLayout.insertLayout(
            self.parent.mainLayout.count() - 2, self.main_layout
        )

    def on_file_path_updated(self):
        file_path = self.file_path_line.text().strip()
        self.file_path_line.setText(file_path)
        if not os.path.exists(file_path):
            print("path doesn't exist")
            self.file_path_line.setObjectName("invalidLine")
            self.file_path_line.setStyleSheet(self.file_path_line.styleSheet())
        else:
            self.file_path_line.setObjectName("validLine")
            self.file_path_line.setStyleSheet(self.file_path_line.styleSheet())

    def get_thumbnail(self):
        thumbnail_text = self.file_path_line.text()
        if thumbnail_text.strip() == "":
            return None
        return thumbnail_text

    def select_file(self):
        print("button presed")
        self.result = self.file_dialog.exec()
        self.selected_files = self.file_dialog.selectedFiles()
        print("RETURN", self.result)
        print("SELECTED FILES", self.selected_files)

        if self.result:
            self.file_path_line.setText(self.selected_files[0])
            self.file_path_line.editingFinished.emit()
