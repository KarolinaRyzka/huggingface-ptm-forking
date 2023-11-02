import requests
import re
import sys


def isGeneratedFromTrainer(fileURL):
    # Define the URL of the raw markdown file
    fileURL: str = fileURL

    # Send a GET request to the URL to retrieve the content
    getFile = requests.get(fileURL)

    # Check if the request was successful (status code 200)
    if getFile.status_code == 200:
        # Get the content of the markdown file
        content:str = getFile.text

        # Search for the specific string
        searchString = r'This model is a fine-tuned version of (.*?) on the (.*?) dataset'
        match: bool = re.search(searchString, content)

        if match:
            print("True, this model is generated by trainer")
        
        else:
            print("False")
    else:
        print("Failed to retrieve the markdown file. Status code:", getFile.status_code)

def main():
    if len(sys.argv) != 2:
        print("Usage: python identify.py <URL>")
        sys.exit(1)

    fileURL = sys.argv[1]
    #fileURL: str = "https://huggingface.co/nazirzhumakhan/finetuning-sentiment-model-3000-samples/raw/main/README.md"
    isGeneratedFromTrainer(fileURL)

if __name__ == "__main__":
    
    main()







