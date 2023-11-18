from setuptools import setup, find_packages
import os

# Collect asset files
assets = [(d, [os.path.join(d, f) for f in files]) 
          for d, directories, files in os.walk('assets')]

setup(
    name='cog_vfx',
    version='0.1',
    packages=find_packages(),
    description='A project management software for team 2AM',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    data_files=assets,
    install_requires=[
        'PySide6',
        'setuptools',
        # List your project dependencies here
        # e.g., 'requests>=2.25.1',
    ],
    entry_points={
        'console_scripts': [
            'cog=cog_vfx.main:main',  # Adjust accordingly
        ],
    },
)


