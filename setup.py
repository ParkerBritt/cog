from setuptools import find_packages, setup

setup(
    name="cog_vfx",
    version="0.1",
    packages=find_packages(),
    description="A project management software for team 2AM",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    package_data={
        "cog_vfx": ["assets/icons/*", "assets/style/*"],
    },
    include_package_data=True,
    install_requires=[
        "PySide6",
        "setuptools",
        "p4python",
        "Wand",
        # Other dependencies...
    ],
    entry_points={
        "console_scripts": [
            "cog=cog_vfx.main:main",  # Adjust as needed
        ],
    },
)
