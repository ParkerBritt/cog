<p align="center">
<a href="https://github.com/bluejamm/cog">
  <img height="150em" src="cog_vfx/assets/icons/main_icon.png"/>

</a>
</p>

<h1 align="center">Cog VFX</h1>
<p align="center"}>
  <img src="https://img.shields.io/badge/Qt-41CD52?style=for-the-badge&logo=qt&logoColor=white">
  <img src="https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue">
  <img src="https://img.shields.io/badge/PIP-3776AB?style=for-the-badge&logo=python&logoColor=FFD43B">
  <img src="https://img.shields.io/badge/Houdini-FF4713?style=for-the-badge&logo=houdini&logoColor=white">
  <img src="https://img.shields.io/badge/Perforce-20a9dc?style=for-the-badge&logo=perforce&logoColor=404040">
</p>

Cog is a **pipeline interface for VFX** and animation specifically designed for the needs of the team of the **Rebirth** student film.  
Because Cog is tailoured to our team's specific needs and built around other tools, it may not fit all use cases or environments.

![image](https://github.com/bluejamm/cog/assets/77124738/306567c5-e39f-4c3d-baf3-2b00e628af1c)


## Features
- **Cross platform**
  - Cog was built to work across **Windows and Linux**. Mac is not supported.
  - Packaged with PIP
  - Interface built with Qt for Python
- **Rendering**  
  - Local rendering using headless Houdini instances
  - Remote distributed rendering planned
  - Select individual layers to render
- **Project Environment Variables**
  - Environment envariables are set when opening project files (Houdini, Maya, Nuke, etc.)
  - Frame range, shot number, fps, description, etc.
- **Search**
  - Users are able to search for specific assets or shots
- **Shot Management**
  - Shots can be created, edited, or deleted through the interface
- **Auto Update**
  - Cog will automatically check for new package versions on your perforce repository and install the latest version

## Installation
### Requirements
- Perforce P4
- Sidefx Houdini

First **clone** and **cd** into the repository  
```bash
git clone https://github.com/bluejamm/cog
cd cog
```
### (Option 1) Interactive installation
Run the **install** command
```bash
pip install -e .
```
### (Option 2) Regular installation
**Build and install** the tar.gz package
```bash
python setup.py sdist
pip install dist/cog_vfx-0.1.tar.gz
```
### Launch Cog
**Run** the cog **command*** in the terminal
```bash
cog
```
You can also create **.desktop** file or **Windows shortcut** to make accessing cog easier


