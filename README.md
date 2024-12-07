<p align="center">
<a href="https://github.com/bluejamm/cog">
  <img height="150em" src="cog_vfx/assets/icons/main_icon.png"/>

</a>
</p>

<h1 align="center">Cog Pipeline</h1>
<p align="center"}>
  <img src="https://img.shields.io/badge/Qt-41CD52?style=for-the-badge&logo=qt&logoColor=white">
  <img src="https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue">
  <img src="https://img.shields.io/badge/PIP-3776AB?style=for-the-badge&logo=python&logoColor=FFD43B">
  <img src="https://img.shields.io/badge/Houdini-FF4713?style=for-the-badge&logo=houdini&logoColor=white">
  <img src="https://img.shields.io/badge/Perforce-20a9dc?style=for-the-badge&logo=perforce&logoColor=404040">
</p>

Cog is a **pipeline interface for VFX** and animation specifically designed for the needs of the team of the **[Rebirth](https://www.therookies.co/entries/28123)** student film.  
Because Cog is tailoured to our team's specific needs and built around other tools, it will not fit all use cases or environments.

![image](screenshots/main_interface.jpg)
> **Warning**  
> Cog is in a very early stage of development. It likely will never be in a state to be used publicly.

## Features
- **Cross platform**
  - Cog was built to work across **Windows and Linux**. Mac is not supported.
  - Packaged with PIP
  - Interface built with Qt for Python
- **Rendering**  
  - Local rendering using headless Houdini instances
  - Select individual layers to render  
![image](screenshots/render_demo.gif)
- **Project Environment Variables**
  - Environment envariables are set when opening project files (Houdini, Maya, Nuke, etc.)
  - Frame range, shot number, fps, description, etc.
- **Search**
  - Users are able to search for specific assets or shots
- **Shot Management**
  - Shots can be created, edited, or deleted through the interface
- **Auto Update**
  - Cog will automatically check for new package versions on your perforce repository and install the latest version
- **Environment Setup**
  - On the first launch Cog will setup the user's envrionment to enable the rest of the pipeline:
    - creating config files, installing houdini packages, setting environment variables, installing python modules for the houdini python interpreter, etc.

## Installation
### Requirements
- Perforce P4
- Sidefx Houdini

First **clone** and **cd** into the repository  
```bash
git clone https://github.com/parkerbritt/cog
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
