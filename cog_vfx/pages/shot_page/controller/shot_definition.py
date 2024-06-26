import os

from PySide6.QtGui import QIcon


class ShotDefinition:
    def __init__(self, **kwargs):
        self.element_type = "shot"
        self.shot_num = kwargs.get("shot_num", None)
        self.formatted_name = kwargs.get("formatted_name", str(self.shot_num).zfill(4))
        print("FORMATTED NAME:", self.formatted_name)

        self.set_mapped_data(kwargs)

        self.update_thumbnail()

    def get_mapped_data(self):
        return {
            "shot_num": self.shot_num,
            "formatted_name": self.formatted_name,
            "start_frame": self.start_frame,
            "end_frame": self.end_frame,
            "description": self.description,
            "res_width": self.res_width,
            "res_height": self.res_height,
            "output_fps": self.fps,
            "dir": self.dir,
            "file_name": self.file_name,
        }

    def get_env_vars(self):
        return {
            "shot_num": self.shot_num,
            "formatted_name": self.formatted_name,
            "start_frame": self.start_frame,
            "end_frame": self.end_frame,
            "description": self.description,
            "res_width": self.res_width,
            "res_height": self.res_height,
            "output_fps": self.fps,
            "dir": self.dir,
            "form_shot_num": self.file_name,
        }

    def set_mapped_data(self, kwargs):
        self.start_frame = kwargs.get("start_frame", None)
        self.end_frame = kwargs.get("end_frame", None)
        self.description = kwargs.get("description", "")
        self.res_width = kwargs.get("res_width", 1920)
        self.res_height = kwargs.get("res_height", 1080)
        self.fps = kwargs.get("fps", 24)
        self.dir = kwargs.get("dir", "")
        self.file_name = kwargs.get("file_name", "")
        self.thumbnail_path = os.path.join(self.dir, "thumbnail.png")

    def change_shot_number(self, new_shot_num):
        print("CHANGEING SHOT DEFINITION SHOT NUMBER TO:", new_shot_num)
        self.shot_num = new_shot_num
        self.formatted_name = str(self.shot_num).zfill(4)

    def change_shot_thumbnail(self, thumbnail_dir):
        self.thumbnail_path = thumbnail_dir
        self.update_thumbnail()

    def update_thumbnail(self):
        self.thumbnail = QIcon(self.thumbnail_path)

    def __repr__(self):
        return f"ShotDefinition: shot_num={self.shot_num}"
