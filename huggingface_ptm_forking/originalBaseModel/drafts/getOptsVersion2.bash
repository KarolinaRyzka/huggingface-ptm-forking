#!/bin/bash

jsonFile="bashOutput.json"
models=()

while getopts "d:" opt; do
  case $opt in
    d)
      directory="$OPTARG"
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      exit 1
      ;;
    :)
      echo "Option -$OPTARG requires an argument." >&2
      exit 1
      ;;
  esac
done

# Check on if root directory was provided
if [ -z "$directory" ]; then
  echo "Usage: $0 -d <directory_path>"
  exit 1
fi

# Check on if directory exists
if [ ! -d "$directory" ]; then
  echo "Directory not found: $directory"
  exit 1
fi

# Function to recursively generate strings for subdirectories
generateStrings() {
  local currentDir="$1"
  for subdir in "$currentDir"/*; do
    if [ -d "$subdir" ]; then
      subdirName="${subdir##*/}"
      modelName="$2"

      if [ -z "$modelName" ]; then
        modelName="$subdirName"
      else
        modelName="${modelName}/${subdirName}"
      }

      fullURL="https://huggingface.co/$modelName"
      response=$(curl -s "$fullURL")
      targetString=$(echo "$response" | sed -n -E 's/.*<a rel="noopener nofollow" href="([^"]+)">[^<]+<\/a>.*/\1/p')

      if [ -n "$targetString" ]; then
        nonURL=$(echo "$targetString" | awk -F '/' '{print $NF}')
        echo "Base model for $modelName:"
        echo "$nonURL"

        models+=("Model: $modelName, Base: $nonURL")
      else
        echo "Error: Target string not found in the model information for $modelName."
      fi

      # Recursively call the function for subdirectories
      generateStrings "$subdir" "$modelName"
    fi
  done
}

# Start the generation with the root directory
generateStrings "$directory"

# Append the results to the JSON file
if [ ${#models[@]} -gt 0 ]; then
  json='['
  for model in "${models[@]}"; do
    json+='{"'$model'"},'
  done
  json=${json%,}  # Remove the trailing comma
  json+=']'

  echo "$json" > "$jsonFile"
  echo "Results appended to $jsonFile"
else
  echo "No results to append to the JSON file."
fi
