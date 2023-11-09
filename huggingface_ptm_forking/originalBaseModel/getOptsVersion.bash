#!/bin/bash

modelName=""

while getopts ":d:" opt; do
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

if [ -z "$modelName" ]; then
  echo "Usage: $0 -m <modelName>"
  exit 1
fi

fullURL="https://huggingface.co/$modelName"

response=$(curl -s "$fullURL") 

targetString=$(echo "$response" | sed -n -E 's/.*<a rel="noopener nofollow" href="([^"]+)">[^<]+<\/a>.*/\1/p')

if [ -n "$targetString" ]; then
    #nonURL=$(echo "$targetString" | awk -F 'https://huggingface.co/' '{print $2}')
    nonURL=$(echo "$targetString" | awk -F '/' '{print $NF}')
    echo "Base model for $modelName:"
    echo "$nonURL"
else
    echo "Error: Target string not found in the model information for $modelName."
fi