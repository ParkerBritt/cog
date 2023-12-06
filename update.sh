#!/bin/bash
# Set the file path
file_path="/home/parker/Perforce/y3-film/pipeline/packages/2AM/cog/dist/cog_vfx-0.1.tar.gz"

# Create a new changelist and get its number
change_list=$(p4 change -o | 
    sed "s/<enter description here>/user:parker asset:cog desc: update distribution/g" | 
    p4 change -i | awk '{print $2}')

# Add the file to the changelist
p4 edit -c $change_list $file_path

python setup.py sdist && cp dist/cog_vfx-0.1.tar.gz ~/Perforce/y3-film/pipeline/packages/2AM/cog/dist/cog_vfx-0.1.tar.gz

p4 submit -c $change_list

