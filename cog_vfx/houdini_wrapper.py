import os
import subprocess
import platform

env = {
        "SOME_VARIABLE":"value",
}

linux_env = {
        "ANOTHER_VARIABLE":"linux",
}

windows_env = {
        "ANOTHER_VARIABLE":"windows"
}

def set_environment_variables():
    # Set common environment variables here

    if platform.system() == 'Windows':
        env.update(windows_env)
    elif platform.system() == 'Linux':
        env.update(linux_env)

    for var in env:
        key = var
        value = env[var]
        print(f"key: {key}, value: {value}")
        os.environ[key] = value


def launch_application(app_path, file_path):
    print("Launching app:", app_path, "file:", file_path)
    subprocess.Popen([app_path, file_path])

def launch_houdini(file_path):
    set_environment_variables()
    app_path = r'C:\Program Files\Side Effects Software\Houdini 19.5.605\bin\houdini.exe' if platform.system() == 'Windows' else '/opt/hfs19.5.605/bin/houdini'
    launch_application(app_path, file_path)


if __name__ == '__main__':
    launch_houdini("/home/parker/Perforce/y3-film/shots/SH080/scene.hipnc")

