import os
import platform
import subprocess

env = {"SOME_VARIABLE": "value", "PROJECT_ROOT": os.getenv("film_root")}

linux_env = {
    "ANOTHER_VARIABLE": "linux",
}

windows_env = {"ANOTHER_VARIABLE": "windows"}


def set_environment_variables(additional_vars):
    # set additional environment variables
    if additional_vars:
        print("additional vars:", additional_vars)
        for key, value in additional_vars.items():
            env.update({key: value})

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


def launch_application(*args):
    print("Launching app:", args)
    subprocess.Popen(args)


def launch_houdini(file_path, additional_vars=None):
    # set additional render variables
    if additional_vars:
        set_environment_variables(additional_vars)

    # get path to houdini
    if platform.system() == "Windows":
        potential_app_paths = [
            r"C:\Program Files\Side Effects Software\Houdini 19.5.605\bin\houdini.exe",
            r"C:\Program Files\Side Effects Software\Houdini19.5.605\bin\houdini.exe",
        ]
        app_path = None
        for path in potential_app_paths:
            if os.path.exists(path):
                app_path = path
                break
        if app_path is None:
            raise Exception(
                "ERROR, houdini.exe could not be found in any of the expected paths:\n"
                + str(potential_app_paths)
            )
    else:
        app_path = "/opt/hfs19.5.605/bin/houdini"

    # launch houdini
    launch_application(app_path, "-n", file_path)


hython_path = (
    r"C:\Program Files\Side Effects Software\Houdini 19.5.605\bin\hython"
    if platform.system() == "Windows"
    else "/opt/hfs19.5.605/bin/hython"
)


def launch_hython(script_path=None, script=None, live_mode=False, additional_vars=None):
    # script path = path to script to execute
    # script = string of script to execute
    # live_mode = runs process continuously
    # set_vars = whether to set environment variables for hython process

    # set environment variables
    if additional_vars:
        set_environment_variables(additional_vars)

    # change arguments based on whether passing script path or a string
    if script_path:
        args = [hython_path, script_path]
    elif script:
        args = [hython_path, "-c", script]

    # start process as a live feed or sequential
    if live_mode:
        process = subprocess.Popen(args, stdout=subprocess.PIPE, text=True)
        return process
    else:
        return_val = subprocess.run(args, stdout=subprocess.PIPE, text=True)
        return return_val


if __name__ == "__main__":
    pass
