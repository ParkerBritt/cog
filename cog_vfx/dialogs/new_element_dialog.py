from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QWidget, QTextEdit, QSpinBox, QPushButton
from PySide6.QtGui import QIcon, QFont, QPixmap
from PySide6.QtCore import QSize, Qt
from ..utils.interface_utils import get_list_widget_data

class NewElementDialog(QDialog):
    def __init__(self, element_list, edit=False, element_name="element", parent=None):
        super().__init__(parent)
        self.element_name = element_name
        self.setWindowTitle("New "+self.element_name)
        self.resize(400,600)
        self.element_list = element_list
        self.input_fields = []

        # edit mode stuff
        self.edit_mode=edit
        self.existing_element_data = get_list_widget_data(element_list)

        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        # add stretch
        self.layout.addStretch()

        # bottom buttons
        bottom_buttons_layout = QHBoxLayout()
        bottom_button_min_size = (50,30)
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
        self.layout.addLayout(bottom_buttons_layout)

        return

        # Element Number
        self.layout.addWidget(QLabel(self.element_name + " Number"))

        self.select_element_num = QSpinBox()
        element_num = 10
        if(self.element_list and len(self.element_list.selectedItems())>0):
            print("element_list", self.element_list)
            element_data = interface_utils.get_list_widget_data(self.element_list)
            element_num = element_data["element_num"] if "element_num" in element_data else 10
            if(not self.edit_mode):
                element_num+=10
        self.select_element_num.setRange(1, 9999)
        self.select_element_num.setValue(element_num)
        self.layout.addWidget(self.select_element_num)

        # frame range title
        self.layout.addWidget(QLabel("Frame Range"))
        frame_range_layout = QHBoxLayout()
        self.layout.addLayout(frame_range_layout)

        # frame start box one
        self.select_start_frame = QSpinBox()
        self.select_start_frame.setRange(1001, 9999)
        self.select_start_frame.setValue(1001)
        frame_range_layout.addWidget(self.select_start_frame)

        # frame start box one
        self.select_end_frame = QSpinBox()
        self.select_end_frame.setRange(1001, 9999)
        self.select_end_frame.setValue(1100)
        frame_range_layout.addWidget(self.select_end_frame)

        # resolution title
        self.layout.addWidget(QLabel("Resolution"))
        res_layout = QHBoxLayout()
        self.layout.addLayout(res_layout)

        # resolution width
        self.select_res_width = QSpinBox()
        self.select_res_width.setRange(1, 9999)
        self.select_res_width.setValue(1920)
        res_layout.addWidget(self.select_res_width)

        # resolution height
        self.select_res_height = QSpinBox()
        self.select_res_height.setRange(1, 9999)
        self.select_res_height.setValue(1080)
        res_layout.addWidget(self.select_res_height)

        # fps
        self.layout.addWidget(QLabel("FPS"))
        self.select_fps = QSpinBox()
        self.select_fps.setRange(1, 9999)
        self.select_fps.setValue(24)
        self.layout.addWidget(self.select_fps)

        # element description
        self.layout.addWidget(QLabel("Element Description"))
        self.element_description_box = QTextEdit()
        self.layout.addWidget(self.element_description_box)


    def exec(self):
        if(self.existing_element_data):
            self.fill_existing_values()

        return super().exec()

    def add_spin_box(self, label, update_key, default_value=1, min_value=0, max_value=9999):
        self.layout.insertWidget(self.layout.count()-2, QLabel(label))
        spin_box = QSpinBox()
        self.layout.insertWidget(self.layout.count()-2, spin_box)

        spin_box.setValue(default_value)
        if(min_value): spin_box.setMinimum(min_value)
        if(max_value): spin_box.setMaximum(max_value)
        self.input_fields.append({"widget":spin_box, "update_key":update_key,})
        return spin_box

    def add_double_spin_box(self, label, update_keys, default_value1=1, default_value2=10, min_value=0, max_value=9999):
        self.layout.insertWidget(self.layout.count()-2, QLabel(label))
        layout = QHBoxLayout()
        spin_box1 = QSpinBox()
        spin_box2 = QSpinBox()
        layout.addWidget(spin_box1)
        layout.addWidget(spin_box2)
        self.layout.insertLayout(self.layout.count()-2, layout)

        if(min_value): spin_box1.setMinimum(min_value)
        if(min_value): spin_box2.setMinimum(min_value)
        if(max_value): spin_box1.setMaximum(max_value)
        if(max_value): spin_box2.setMaximum(max_value)

        spin_box1.setValue(default_value1)
        spin_box2.setValue(default_value2)
        self.input_fields.append({"widget":spin_box1, "update_key":update_keys[0][0],})
        self.input_fields.append({"widget":spin_box2, "update_key":update_keys[0][0],})
        return spin_box1, spin_box2

    def on_ok_pressed(self):
        print("on_ok_pressed method meant to be overwritten")

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
        if(value in self.existing_element_data):
            if(isinstance(widget, QTextEdit)):
                widget.setPlainText(self.existing_element_data[value])
            elif(isinstance(widget, QSpinBox)):
                widget.setValue(self.existing_element_data[value])
