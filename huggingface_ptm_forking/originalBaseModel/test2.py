import json
import requests
import re
import markdown
import os
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def getlinks(fileContents: str):
    #parse content
    html = markdown.markdown(fileContents)

    links = re.findall(r'<a\s+(?:[^>]*?\s+)?href="([^"]*)"', html)

    return links

def identifyBaseModel(links: list):
    
    return "fuck"

def traverse_directory(rootDirectory, outputFile):
    results = {}
    #models set up of PTMTorrent
    for folderName, subFolders, filenames in os.walk(rootDirectory):
        for file in filenames:
            if(file.endswith(".md")):
                filePath = os.path.join(folderName, file)

                with open(filePath, 'r') as file:
                    fileContents = file.read()

                #call function here
    
    #place result in json file
    with open(outputFile, 'w') as jsonFile:
        json.dump(results, jsonFile, indent=2)

if __name__ == "__main__":
    filePath = "/Users/karolinaryzka/Documents/huggingface-ptm-forking/huggingface-ptm-forking/huggingface_ptm_forking/originalBaseModel/README.md"
    with open(filePath, 'r') as file:
        fileContents = file.read()
    result = getLinks(fileContents)
    print("Extracted Links:")
    for link in result:
        print(link)
    
    
    #rootDirectory = "Dataset"
    #outputFile = "output.json"

    #traverse_directory(rootDirectory, outputFile)
