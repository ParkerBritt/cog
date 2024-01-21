import os
import platform
import subprocess
import sys

from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


def main():
    print("\n\n\n--------- Starting Install -------------")
    main_window = install_dialog()
    return main_window


def install_sequence():
    print("\n\n-------- Installing Houdini Package --------")
    install_houdini_package()
    return

    print("\n\n------- Making Perforce Config File ---------")
    # make_p4_config()

    # Set Environment variables
    print("\n\n------- Setting Environment Variables --------")
    hip = hou.getenv("HIP")
    p4ignore_path = os.path.normpath(f"{hip}/../perforce/p4ignore")
    set_environment_variable("P4IGNORE", p4ignore_path)
    set_environment_variable("film_root", os.path.normpath(f"{hip}/../.."))

    # Show success message
    print("\n-- install finished successfully -- ")


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


class ErrorDialog(QDialog):
    def __init__(self, error_message):
        self.main_layout = QVBoxLayout()
        self.setMaximumSize(320, 120)
        self.setWindowTitle("Environment Setup Error")

        message = "An error occured while trying to setup your environment"
        message += error_message
        self.main_layout.addWidget(QLabel(message))


class InstallDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # -- setup window --
        self.main_layout = QVBoxLayout()
        self.setMaximumSize(320, 120)
        self.setWindowTitle("Environment Setup")
        self.setLayout(self.main_layout)

        # -- main text --
        self.main_layout.addWidget(
            QLabel(
                "Your environment is not properly configured\nwould you like to perform the setup now?"
            )
        )

        # -- make buttons --
        self.make_buttons()

    def make_buttons(self):
        # make button layout
        self.button_layout = QHBoxLayout()
        self.main_layout.addLayout(self.button_layout)
        # make button widgets
        self.ok_button = QPushButton("Ok")
        self.ok_button.clicked.connect(install_sequence)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.close)
        # add buttons to layout
        self.button_layout.addWidget(self.ok_button)
        self.button_layout.addWidget(self.cancel_button)


def install_dialog():
    dialog_window = InstallDialog()
    # dialog_window.exec()
    dialog_window.show()
    return dialog_window
    # node = kwargs["node"]
    # install_window_choice = hou.ui.displayMessage(
    #     "Install 2AM Houdini package?",
    #     buttons=("Install", "Cancel"),
    #     severity=hou.severityType.Message,
    #     default_choice=0,
    #     close_choice=1,
    #     title="2AM Install",
    # )
    # if install_window_choice != 0:
    #     print("install cancelled")
    #     exit()


def install_houdini_package():
    # assuming a uniform houdini install path for now
    # -- fetching paths --
    OS = platform.system()
    if OS == "Linux":
        HFS = "/opt/hfs19.5.605"

        home_path = os.getenv("HOME")
        if not home_path:
            raise Exception("environment variable 'HOME' is empty")
        project_root = home_path + "/Perforce/y3-film"
    elif OS == "Windows":
        HFS = r"C:/PROGRAM FILES/Side Effects Software/Houdini 19.5.603"

        home_path = os.getenv("USERPROFILE")
        if not home_path:
            raise Exception("environment variable 'HOME' is empty")
        project_root = home_path + r"\Perforce\y3-film"
    else:
        raise Exception("unknown OS: " + OS)

    # -- check for valid paths
    if not os.path.exists(HFS):
        raise Exception("file does not exits, expected HFS: " + HFS)
    if not os.path.exists(project_root):
        raise Exception("file does not exits, expected project root: " + project_root)

    # -- print new paths --
    print("OS:", OS)
    print("Houdini install path:", HFS)
    print("Project root:", project_root)

    # -- find package and subpackage path --
    package_path = project_root + "/packages/2AM/houdini"
    package_path = os.path.normpath(package_path)
    sub_package_path = f"{package_path}/packages"
    # print new paths
    print("package_path:", package_path)
    print("sub_package_path:", sub_package_path)

    # -- create package content --
    package_content = f"""{{
"path" : "{package_path}",
"package_path" : "{sub_package_path}"
}}"""
    print("package content", package_content)

    # -- get houdini env vars --
    # run hython command to get path
    hython_path = os.path.join(HFS, "bin/hython")
    hython_command = (
        "print('HOUDINI_USER_PREF_DIR=' + hou.getenv('HOUDINI_USER_PREF_DIR'))"
    )
    command_out = subprocess.run(
        [hython_path, "-c", hython_command], capture_output=True, text=True
    )
    cmd_out_split = command_out.stdout.strip().split("=")
    # form paths
    houdini_pref_path = cmd_out_split[1]
    houdini_package_path = os.path.join(houdini_pref_path, "packages")
    # verify paths exists
    if not os.path.exists(houdini_pref_path):
        raise Exception(
            "houdini preference path doesn't exist, expected: " + houdini_pref_path
        )
    if not os.path.exists(houdini_package_path):
        os.makedirs(houdini_package_path)
    # print paths
    print("houdini preferences path")
    print("houdini packgage path:", houdini_package_path)

    # Build the path to the package file. If the package file already exists set the action and color to updated
    module_filepath = os.path.join(houdini_package_path, "2AM.json")
    print("module_filepath", module_filepath)
    if os.path.exists(module_filepath):
        finished_status = "updated"

    # Write the package file
    with open(module_filepath, "w") as module_file:
        module_file.write(package_content)

    # Get the message template from the Extra Files section
    message = node.type().definition().sections()["SUCCESS_MESSAGE"].contents()
    message = message.replace("@___HOUDINI_PATH___@", package_path)
    message = message.replace("@___PACKAGE_PATH___@", sub_package_path)
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
