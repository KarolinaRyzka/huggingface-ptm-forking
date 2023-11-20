import json
import requests
import markdown
import os
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def identifyBaseModel(user, modelName):
    fullURL = f"https://huggingface.co/{user}/{modelName}"

    try:
        response = requests.get(fullURL)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # get all links from model card
        links = soup.find_all('a', {'rel': 'noopener nofollow', 'href': True})

        if len(links) >= 2:
            # Extracting the href attribute from the second link (first link is the model itself, second in description is the base model)
            secondLink = links[1]
            hrefVal = secondLink.get('href', '')

            # get the path from the url
            path = urlparse(hrefVal).path

            # extract the model name from the path
            baseModelName = path.split('/')[-1]

            if(baseModelName == ""):
                print(f"Base model for {modelName}:\nnull")
            else:
                print(f"Base model for {modelName}:\n{baseModelName}")
        else:
            print(f"Error: Less than two links found in the model card for {modelName}.")

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")

    return baseModelName

def traverse_directory(rootDirectory, outputFile):
    results = {}
    #models set up of PTMTorrent
    for user, dirs, files in os.walk(rootDirectory):
        #exclude the root directory itself (Dataset) in the path
        if user != rootDirectory:
            # create path for huggingface link
            relativePath = os.path.relpath(user, rootDirectory)
            
            for modelName in dirs:
                constructedModelName = f"{relativePath}/{modelName}"
                print(constructedModelName)

                #search model card for base model
                baseModel = identifyBaseModel(relativePath, modelName)

                if(baseModel == ""):
                    results[constructedModelName] = "null"
                else:
                    results[constructedModelName] = baseModel
    
    #place result in json file
    with open(outputFile, 'w') as jsonFile:
        json.dump(results, jsonFile, indent=2)

if __name__ == "__main__":
    rootDirectory = "Dataset"
    outputFile = "output.json"

    traverse_directory(rootDirectory, outputFile)
