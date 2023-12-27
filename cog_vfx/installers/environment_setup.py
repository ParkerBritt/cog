import os
import platform
import subprocess
import sys

import hou


def main(kwargs):
    print("\n\n\n--------- Starting Install -------------")
    installPrompt(kwargs)

    print("\n\n-------- Installing Houdini Package --------")
    installPackage(kwargs)

    print("\n\n------- Making Perforce Config File ---------")
    make_p4_config()

    # Set Environment variables
    print("\n\n------- Setting Environment Variables --------")
    hip = hou.getenv("HIP")
    p4ignore_path = os.path.normpath(f"{hip}/../perforce/p4ignore")
    set_environment_variable("P4IGNORE", p4ignore_path)
    set_environment_variable("film_root", os.path.normpath(f"{hip}/../.."))

    # Show success message
    print("\n-- install finished successfully -- ")


# def install_hython_package(package_name):
#     print("installing package:", package_name)
#
#     # Run the pip install command with the Python interpreter found by sys.executable
#     interpreter = hou.getenv("HFS")+"/bin/hython"
#     if platform.system() == 'Windows':
#         interpreter+=".exe"
#     if(not os.path.exists(interpreter)):
#         print(f"Interpreter not at path: {interpreter}")
#         return
#     cmd = [interpreter, '-m', 'pip', 'install', package_name]
#     print("running command:", cmd)
#     print(subprocess.check_call(cmd))


def set_environment_variable(key, value):
    if platform.system() == "Windows":
        # Forming the command
        command = f'setx {key} "{value}"'

        # Running the command
        result = subprocess.run(command, shell=True, text=True, capture_output=True)

        # Checking for errors
        if result.returncode != 0:
            print(f"Error: {result.stderr}")
        else:
            print(f"Successfully set {key} to {value}")
    else:
        print(
            f"setting environment variables are currently only implemented on windows\nIgnoring key: {key}\nvalue: {value}"
        )


def installPrompt(kwargs):
    node = kwargs["node"]
    install_window_choice = hou.ui.displayMessage(
        "Install 2AM Houdini package?",
        buttons=("Install", "Cancel"),
        severity=hou.severityType.Message,
        default_choice=0,
        close_choice=1,
        title="2AM Install",
    )
    if install_window_choice != 0:
        print("install cancelled")
        exit()


def installPackage(kwargs):
    # Set default node name, action (for pop up window) color, and shape
    node = kwargs["node"]
    node_name = "Installed"
    action = "Install"
    installed_node_color = hou.Color((0.18, 1, 0.34))
    updated_node_color = hou.Color((0.18, 1, 1))
    node.setColor(installed_node_color)
    # node.setUserData('nodeshape', 'light')

    # This is the path to this HDA
    # filepath = node.type().definition().libraryFilePath()
    hip = hou.getenv("HIP")

    # From that we know where the houdini root folder and the package folder we want to add is
    houdini_path = f"{hip}/../packages/2AM/houdini"
    houdini_path = os.path.normpath(houdini_path)
    package_path = "{houdini_path}/packages".format(houdini_path=houdini_path)
    print("houdini_path:", houdini_path)
    print("package_path:", package_path)

    # Get the json template from the Extra Files section
    package_content = node.type().definition().sections()["PACKAGE_TEMPLATE"].contents()
    package_content = package_content.replace("@___HOUDINI_PATH___@", houdini_path)
    package_content = package_content.replace("@___PACKAGE_PATH___@", package_path)
    # Set this HDA's string parms to show what the additions will be
    node.parm("houdini_path").set(houdini_path)
    node.parm("package_path").set(package_path)

    # Get the user prefs package directory and create the directory if it does not exist
    user_pref_dir = hou.getenv("HOUDINI_USER_PREF_DIR")
    package_directory = "{user_pref_dir}/packages".format(user_pref_dir=user_pref_dir)
    package_directory = os.path.normpath(package_directory)
    print("package_directory", package_directory)
    if not os.path.exists(package_directory):
        os.makedirs(package_directory)

    # Build the path to the package file. If the package file already exists set the action and color to updated
    module_filepath = os.path.join(package_directory, "2AM.json")
    print("module_filepath", module_filepath)
    if os.path.exists(module_filepath):
        node_name = "Updated"
        action = "Update"
        node.setColor(updated_node_color)

    # Write the package file
    with open(module_filepath, "w") as module_file:
        module_file.write(package_content)

    # Get the message template from the Extra Files section
    message = node.type().definition().sections()["SUCCESS_MESSAGE"].contents()
    message = message.replace("@___HOUDINI_PATH___@", houdini_path)
    message = message.replace("@___PACKAGE_PATH___@", package_path)
    message = message.replace("@__NODE_NAME__@", node_name)

    # Set the node name
    node.setName(node_name)


# Generate perforce config file containing info about:
# P4PORT, P4USER, and P4CLIENT
def make_p4_config():
    P4PASSWD = "***********"
    P4PORT = "***********"

    # set save path for P4CONFIG file based on OS
    OS = platform.system()
    if OS == "Linux":
        p4_config_path = os.path.normpath(
            os.path.expandvars("$HOME/.config/Perforce/test_p4config")
        )
    elif OS == "Windows":
        p4_config_path = os.path.normpath(
            os.path.expandvars("$USERPROFILE/Perforce/p4config.txt")
        )

    # set temp environment variables to be able to use p4 commands
    os.environ["P4PORT"] = P4PORT
    os.environ["P4USER"] = "core"
    os.environ["P4PASSWD"] = P4PASSWD

    # check system's host name
    host_name = subprocess.run(
        ["hostname"], stdout=subprocess.PIPE, text=True
    ).stdout.strip()
    print("target hostname:", host_name)
    target_path = os.getenv("film_root")
    print("target path:", target_path)

    # grab a list of perforce clients
    clients = subprocess.run(
        ["p4", "clients"], stdout=subprocess.PIPE, text=True
    ).stdout
    clients_list = clients.strip().split("\n")

    # create environment variables above loop scope
    client_name = ""
    root_path = ""
    client_owner = ""
    has_found_client = False

    # Search for client that aligns with user's environment
    for client in clients_list:
        # split client short description into client_parts
        client_parts = client.split(" ")
        # extract root path from client short description
        trial_root_path = client_parts[4]
        # extract client name from client short description
        trial_client_name = client_parts[1]

        # fetch detailed client description
        client_info = subprocess.run(
            ["p4", "client", "-o", trial_client_name], stdout=subprocess.PIPE, text=True
        ).stdout

        # find host name in detailed client description
        trail_host_name = ""
        for line in client_info.split("\n"):
            if line.startswith("Host:"):
                trial_host_name = line.split("\t")[1].strip()
            elif line.startswith("Owner:"):
                trial_client_owner = line.split("\t")[1].strip()

        # compare host name and path of current client against systems values
        is_valid_host_name = trial_host_name == host_name
        is_valid_path = target_path == trial_root_path
        # debug statement
        print(
            f"[checking] client: {trial_client_name}, is_valid_host_name: {is_valid_host_name}, is_valid_path: {is_valid_path}, host_name, {trial_host_name}"
        )
        print(f"{trial_host_name} != {host_name}")
        print(f"{target_path} != {trial_root_path}")

        # if found exit for loop,
        if is_valid_host_name and is_valid_path:
            client_name = trial_client_name
            root_path = trial_root_path
            client_owner = trial_client_owner
            has_found_client = True
            break

    # Exit if client not found
    if not has_found_client:
        print(
            "CLIENT NOT FOUND\nmake sure to properly set up perforce before running this script"
        )
        return

    P4CONFIG_contents = f"""P4PORT={P4PORT}
P4USER=core
P4CLIENT={client_name}"""
    if client_owner == "core":
        P4CONFIG_contents += f"\nP4PASSWD={P4PASSWD}"

    with open(p4_config_path, "w") as file:
        file.write(P4CONFIG_contents)

    print("\n-- Found valid client --")
    print("Client:", client_name)
    print("Root Path:", root_path)
    set_environment_variable("P4CONFIG", p4_config_path)
