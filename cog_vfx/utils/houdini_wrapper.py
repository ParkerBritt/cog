import os, subprocess, platform

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

def set_environment_variables(additional_vars):
    # set additional environment variables
    if(additional_vars):
        for var in additional_vars:
            env.update(var)

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

def launch_houdini(file_path, additional_vars=None):

    if(additional_vars):
        set_environment_variables(additional_vars)
    app_path = r'C:\Program Files\Side Effects Software\Houdini 19.5.605\bin\houdini.exe' if platform.system() == 'Windows' else '/opt/hfs19.5.605/bin/houdini'
    launch_application(app_path, file_path)

hython_path = r'C:\Program Files\Side Effects Software\Houdini 19.5.605\bin\hython' if platform.system() == 'Windows' else '/opt/hfs19.5.605/bin/hython'

def launch_hython(script_path=None, script=None, live_mode=False, additional_vars=None):
    # script path = path to script to execute
    # script = string of script to execute
    # live_mode = runs process continuously
    # set_vars = whether to set environment variables for hython process

    # set environment variables
    if(additional_vars):
        set_environment_variables(additional_vars)

    # change arguments based on whether passing script path or a string
    if(script_path):
        args = [hython_path, script_path]
    elif(script):
        args = [hython_path, "-c", script]

    # start process as a live feed or sequential
    if(live_mode):
        process = subprocess.Popen(args, stdout=subprocess.PIPE, text=True)
        return process
    else:
        return_val = subprocess.run(args, stdout=subprocess.PIPE, text=True)
        return return_val

if __name__ == '__main__':
    pass

