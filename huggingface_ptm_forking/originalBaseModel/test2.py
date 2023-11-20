import json
import requests
import re
import markdown
from urllib.parse import urlparse
import os
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def getLink(fileContents: str):
    #parse content
    html = markdown.markdown(fileContents)

    match = re.search(r'<a\s+(?:[^>]*?\s+)?href="([^"]*)"', html)
    
    if match:
        URL = match.group(1)
        segments = urlparse(URL).path.split("/")
        baseModel = segments[-1] if segments else URL
        return baseModel
    else:
        return None



def traverse_directory(rootDirectory, outputFile):
    results = {}
    #models set up of PeatMOSS
    for folderName, subFolders, filenames in os.walk(rootDirectory):
        for file in filenames:
            if(file.endswith(".md")):
                filePath = os.path.join(folderName, file)

                with open(filePath, 'r') as file:
                    fileContents = file.read()
                result = getLink(fileContents)
                results[folderName] = result
                
    
    #place result in json file
    with open(outputFile, 'w') as jsonFile:
        json.dump(results, jsonFile, indent=2)

def main():
    # filePath = "/Users/karolinaryzka/Documents/huggingface-ptm-forking/huggingface-ptm-forking/huggingface_ptm_forking/originalBaseModel/README.md"
    # with open(filePath, 'r') as file:
    #     fileContents = file.read()
    # result = getLink(fileContents)
    # print(result)
    rootDirectory = "/Users/karolinaryzka/Documents/huggingface-ptm-forking/huggingface-ptm-forking/huggingface_ptm_forking/originalBaseModel/Dataset"
    outputFile = "output.json"
    traverse_directory(rootDirectory, outputFile)


if __name__ == "__main__":

    main()

    
    
    #rootDirectory = "Dataset"
    #outputFile = "output.json"

    #traverse_directory(rootDirectory, outputFile)
