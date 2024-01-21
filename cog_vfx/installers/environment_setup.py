import os
import platform
import subprocess
import sys

from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


def main():
    if not needs_install():
        print("environment setup check passed")
        return None
    main_window = install_dialog()
    return main_window


def needs_install():
    # return True  # for testing
    return not bool(os.getenv("film_root"))


def get_project_root():
    OS = platform.system()
    if OS == "Linux":
        home_path = os.getenv("HOME")
        if not home_path:
            raise Exception("environment variable 'HOME' is empty")
        project_root = home_path + "/Perforce/y3-film"
    elif OS == "Windows":
        home_path = os.getenv("USERPROFILE")
        if not home_path:
            raise Exception("environment variable 'USERPROFILE' is empty")
        project_root = home_path + r"\Perforce\y3-film"
    else:
        raise Exception("unknown OS: " + OS)

    return project_root


def install_sequence():
    print("\n\n\n--------- Starting Install -------------")
    project_root = get_project_root()

    print("\n\n-------- Installing Houdini Package --------")
    install_houdini_package(project_root)

    print("\n\n------- Making Perforce Config File ---------")
    make_p4_config()

    # Set Environment variables
    print("\n\n------- Setting Environment Variables --------")
    p4ignore_path = os.path.normpath(f"{project_root}/pipeline/perforce/p4ignore")
    set_environment_variable("P4IGNORE", p4ignore_path)
    set_environment_variable("film_root", project_root)

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
        self.ok_button.clicked.connect(self.on_ok_clicked)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.close)
        # add buttons to layout
        self.button_layout.addWidget(self.ok_button)
        self.button_layout.addWidget(self.cancel_button)

    def on_ok_clicked(self):
        self.close()
        install_sequence()


def install_dialog():
    dialog_window = InstallDialog()
    dialog_window.exec()
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


def install_houdini_package(project_root):
    # assuming a uniform houdini install path for now
    # -- fetching paths --
    OS = platform.system()
    if OS == "Linux":
        HFS = "/opt/hfs19.5.605"
    elif OS == "Windows":
        HFS = r"C:/PROGRAM FILES/Side Effects Software/Houdini 19.5.603"
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
    package_path = project_root + "/pipeline/packages/2AM/houdini"
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
    install_type = "updating" if os.path.exists(module_filepath) else "installing"

    # Write the package file
    with open(module_filepath, "w") as module_file:
        module_file.write(package_content)

    print(f"finished {install_type} houdini package".upper())


class P4_dialog(QDialog):
    def __init__(self):
        super().__init__()
        self.initUI()

    def make_buttons(self):
        # make button layout
        self.button_layout = QHBoxLayout()
        self.main_layout.addLayout(self.button_layout)
        # make button widgets
        self.ok_button = QPushButton("Ok")
        self.ok_button.clicked.connect(self.on_ok_clicked)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.on_cancel_clicked)
        # add buttons to layout
        self.button_layout.addWidget(self.ok_button)
        self.button_layout.addWidget(self.cancel_button)

    def on_ok_clicked(self):
        self.close_status = 1  # clicked ok
        self.password = self.password_widget.text()
        self.address = self.address_widget.text()
        self.close()

    def on_cancel_clicked(self):
        self.close_status = 0  # clicked cancel
        self.close()

    def initUI(self):
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        self.setWindowTitle("P4 Login")
        self.setMaximumSize(320, 120)

        self.close_status = 0
        self.main_layout.addWidget(QLabel("Enter P4 login. Make sure this is correct."))

        password_layout = QHBoxLayout()
        address_layout = QHBoxLayout()

        self.password_widget = QLineEdit()
        self.address_widget = QLineEdit()

        password_layout.addWidget(QLabel("P4 Password:"))
        password_layout.addWidget(self.password_widget)
        address_layout.addWidget(QLabel("P4 Address:   "))
        address_layout.addWidget(self.address_widget)

        self.main_layout.addLayout(password_layout)
        self.main_layout.addLayout(address_layout)

        self.make_buttons()


# Generate perforce config file containing info about:
# P4PORT, P4USER, and P4CLIENT
def make_p4_config():
    dialog = P4_dialog()
    dialog.exec()
    if dialog.close_status == 0:
        return
    P4PASSWD = dialog.password
    P4PORT = dialog.address

    os.environ["P4PASSWD"] = P4PASSWD
    os.environ["P4PORT"] = P4PORT

    print(P4PASSWD, P4PORT)

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
    else:
        raise Exception("unkown OS: " + OS)

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
    p4_clients_process = subprocess.run(
        ["p4", "clients"], capture_output=True, text=True
    )
    print("process:", p4_clients_process)
    clients = p4_clients_process.stdout

    if p4_clients_process.stderr:

        def on_err_button():
            err_dialog.close()
            make_p4_config()

        err_dialog = QDialog()
        err_dialog.setMaximumSize(300, 100)
        err_dialog.setWindowTitle("Error")
        err_dialog_layout = QVBoxLayout()
        err_dialog.setLayout(err_dialog_layout)
        err_dialog_layout.addWidget(
            QLabel("Error occured.\nMake sure you typed the correct login")
        )
        err_dialog_button = QPushButton("ok")
        err_dialog_button.clicked.connect(on_err_button)
        err_dialog_layout.addWidget(err_dialog_button)
        err_dialog.exec()
        return

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
        trial_host_name = ""
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

    print("\n-- Found valid client --")
    print("Client:", client_name)
    print("Root Path:", root_path)

    print("\nwriting contents:\n" + P4CONFIG_contents + "\nto:\n" + p4_config_path)
    with open(p4_config_path, "w") as file:
        file.write(P4CONFIG_contents)

    set_environment_variable("P4CONFIG", p4_config_path)
