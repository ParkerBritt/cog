#!/bin/bash

# Function to convert black PNG to white PNG
convert_to_white() {
    local input_file=$1
    local output_file=$2

    convert "$input_file" -fuzz 100% -fill white -opaque black "$output_file"
}

# Main script execution
if [ "$#" -eq 1 ]; then
    # One argument provided
    input_file=$1
    if [[ $input_file == *"black"* ]]; then
        output_file=${input_file//black/white}
    else
        output_file="${input_file%.*}_white.${input_file##*.}"
    fi
    convert_to_white "$input_file" "$output_file"
elif [ "$#" -eq 2 ]; then
    # Two arguments provided
    input_file=$1
    output_file=$2
    convert_to_white "$input_file" "$output_file"
else
    echo "Usage: $0 <input_file> [output_file]"
    exit 1
fi

