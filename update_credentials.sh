#!/bin/bash

# Function to generate a unique filename
generate_unique_filename() {
    local base_filename="$1"
    local counter=1
    local new_filename="${base_filename%.*}_${counter}.${base_filename##*.}"

    # Check if the filename already exists, if so, increment the counter
    while [[ -e "$new_filename" ]]; do
        let counter++
        new_filename="${base_filename%.*}_${counter}.${base_filename##*.}"
    done

    echo "$new_filename"
}

# Renaming and moving "credentials.json" to "credentials_archive"
if [[ -e "credentials.json" ]]; then
    unique_filename=$(generate_unique_filename "credentials.json")
    mv "credentials.json" "credentials_archive/$unique_filename"
    echo "Renamed and moved credentials.json to credentials_archive/$unique_filename"
fi

# Renaming files starting with "client-secrets" and ending with ".json" to "credentials.json"
for file in client_secret*.json; do
    if [[ -e "$file" ]]; then
        mv "$file" "credentials.json"
        echo "Renamed $file to credentials.json"
    fi
done

# Deleting "token.json"
if [[ -e "token.json" ]]; then
    rm "token.json"
    echo "Deleted token.json"
fi
