#!/bin/bash

# Check if an argument is given
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <image_file>"
    exit 1
fi

# Get the image file name from the first argument
input_image="$1"
# offset=10
xoffset=10
yoffset=5
radius=20

# Extract file name components
filename=$(basename -- "$input_image")
extension="${filename##*.}"
filename="${filename%.*}"

# Output file name with '_submitted' suffix
output_image="${filename}_submitted.${extension}"

# Get the dimensions of the image
dimensions=$(identify -format "%wx%h" "$input_image")
width=$(echo $dimensions | cut -d'x' -f1)
height=$(echo $dimensions | cut -d'x' -f2)

# Coordinates for the bottom right corner
x=$((width - xoffset - radius))
y=$((height - yoffset - radius))

# Draw a green dot in the bottom-right corner
convert "$input_image" -fill green -draw "circle $x,$y $(($x + radius)),$y" "$output_image"

echo "Output generated: $output_image"

gwenview $output_image
