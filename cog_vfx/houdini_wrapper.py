import os, subprocess, platform

valid_vars = ["fps", "res_width", "res_height", "shot_num", "start_frame", "end_frame"]

env = {
        "SOME_VARIABLE":"value",
        "PROJECT_ROOT":os.getenv("film_root")
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
        key = key.upper()
        value = env[var]
        print(f"key: {key}, value: {value}")
        os.environ[key] = str(value)


def launch_application(app_path, file_path):
    print("Launching app:", app_path, "file:", file_path)
    subprocess.Popen([app_path, file_path])

def launch_houdini(file_path, shot_data):
    for key in shot_data:
        if(key in valid_vars):
            env[key] = shot_data[key]

    set_environment_variables()
    app_path = r'C:\Program Files\Side Effects Software\Houdini 19.5.605\bin\houdini.exe' if platform.system() == 'Windows' else '/opt/hfs19.5.605/bin/houdini'
    launch_application(app_path, file_path)

def launch_hython(file_path, shot_data=None, script_path=None, script=None, live_mode=False, set_vars=True):
    if(set_vars):
        for key in shot_data:
            if(key in valid_vars):
                env[key] = shot_data[key]

        set_environment_variables()

    app_path = r'C:\Program Files\Side Effects Software\Houdini 19.5.605\bin\hython' if platform.system() == 'Windows' else '/opt/hfs19.5.605/bin/hython'
    if(script_path):
        args = [app_path, script_path, file_path]
    elif(script):
        args = [app_path, "-c", script]
    if(live_mode):
        process = subprocess.Popen(args, stdout=subprocess.PIPE, text=True)
        return process
    else:
        return_val = subprocess.run(args, stdout=subprocess.PIPE, text=True)
        return return_val
    # launch_application(app_path, file_path)

if __name__ == '__main__':
    launch_houdini("/home/parker/Perforce/y3-film/shots/SH080/scene.hipnc")

