import os
import platform
import subprocess

from .houdini_wrapper import launch_houdini


def set_env_vars(additional_vars):
    env = {"PROJECT_ROOT": os.getenv("film_root")}

    linux_env = {
        "system_os": "linux",
    }

    windows_env = {"system_os": "windows"}

    if additional_vars:
        for var in additional_vars:
            env.update(var)

    if platform.system() == "Windows":
        env.update(windows_env)
    elif platform.system() == "Linux":
        env.update(linux_env)

    for var in env:
        key = var
        key = key.upper()
        value = env[var]
        print(f"key: {key}, value: {value}")
        os.environ[key] = str(value)


def open_houdini(file_path):
    launch_houdini(file_path)


def open_maya(file_path):
    if platform.system() == "Windows":
        os.startfile(file_path)
    else:
        maya_path = "/usr/local/bin/maya"
        subprocess.Popen((maya_path, file_path))


def open_file(file_path, env_vars=None):
    path_mapping = {
        ".mb": open_maya,
        ".hipnc": open_houdini,
    }
    file_type = os.path.splitext(file_path)[1]
    if not file_type in path_mapping:
        print("Uknown file type:", file_type, "Path:", file_path)
        return
    # if file type recognized
    print("Opening file:", file_path)
    if env_vars:
        set_env_vars(env_vars)

    path_mapping[file_type](file_path)
