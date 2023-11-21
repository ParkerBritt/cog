import os, pkg_resources

def get_project_root():
    return os.getenv("film_root")


PACKAGE_NAME = "cog_vfx"
def get_asset_path(path):
    asset_path = pkg_resources.resource_filename(PACKAGE_NAME, path)
    print("get asset path", asset_path)
    return asset_path

def get_style_sheet():
    stylesheet_path = get_asset_path("assets/style/style.css")
    with open(stylesheet_path, "r") as file:
        stylesheet = file.read()

    return stylesheet


