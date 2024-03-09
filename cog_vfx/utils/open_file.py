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
        env.update(additional_vars)

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


def open_houdini(file_path: str,
              env_vars: dict | None=None,
              kwargs: dict | None=None) -> None:
    launch_houdini(file_path)


def open_maya(file_path: str,
              env_vars: dict | None=None,
              kwargs: dict | None=None) -> None:

    # find maya executable
    if platform.system() == "Windows":
        maya_path = r"C:\Program Files\Autodesk\Maya2024\bin\maya.exe"
        # os.startfile(file_path)
    else:
        maya_path = "/usr/local/bin/maya"

    # load shelf tools
    if env_vars:
        project_root = os.getenv("film_root")
        shelf_tools_path = os.path.join(project_root, r"pipeline/packages/2AM/maya/shelves/")
        print("adding  maya shelf path:", shelf_tools_path)
        os.environ["MAYA_SHELF_PATH"] = shelf_tools_path

    subprocess.Popen((maya_path, file_path))


def open_file(
        file_path: str,
        env_vars: dict[str, str] | list[dict] | None = None,
        kwargs: dict | None = None,
        ) -> None:

    # idk why env_vars comes in as a list, but whatever I'll fix it later
    if isinstance(env_vars, list): # unpacks list to the dict inside
        temp_vars = {}
        for var_pair in env_vars:
            temp_vars.update(var_pair)
        env_vars = temp_vars 

    path_mapping = {
        ".mb": open_maya,
        ".hipnc": open_houdini,
    }
    file_type = os.path.splitext(file_path)[1]
    if not file_type in path_mapping:
        print("Unknown file type:", file_type, "Path:", file_path)
        return
    # if file type recognized
    print("Opening file:", file_path)
    if env_vars:
        set_env_vars(env_vars)

    path_mapping[file_type](file_path, env_vars, kwargs)
