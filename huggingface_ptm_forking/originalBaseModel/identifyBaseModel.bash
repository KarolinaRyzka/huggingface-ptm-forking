#!/bin/bash

#source /Users/karolinaryzka/Documents/huggingface-ptm-forking/huggingface-ptm-forking/utils/optparse/optparse.bash
source ./optparse.bash

optparse.define short=m long=modelName variable=modelName desc="Specify the model name."
helpMessage = "Run ./identifyBaseModel.sh -h for command line arguments"
#optparse.parse "$@"

source $( optparse.build )

if [ -z $modelName ]
then
    echo "No input for -m | --modelName
    echo $helpMessage
    exit 1
fi


fullURL="https://huggingface.co/$modelName"

response=$(curl -s "$fullURL") 

targetString=$(echo "$response" | sed -n -E 's/.*<a rel="noopener nofollow" href="([^"]+)">[^<]+<\/a>.*/\1/p')

if [ -n "$targetString" ]; then
    nonURL=$(echo "$targetString" | awk -F 'https://huggingface.co/' '{print $2}')
    echo "Base model for $modelName:"
    echo "$nonURL"
else
    echo "Error: Target string not found in the model information for $modelName."
fi
