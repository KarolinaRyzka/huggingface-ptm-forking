from openai import OpenAI
from openai import AsyncOpenAI
import time
from pathlib import Path
import os
import tiktoken
import json
import asyncio
 

def getModelCard(directory):
    for folderName, subFolders, filenames in os.walk(directory):
        for file in filenames:
            if (file.endswith(".md")):
                filePath = os.path.join(folderName, file)
                with open(filePath, 'r') as file:
                    fileContents = file.read()
                return str(fileContents)
    return None
 
# Function to interact with the GPT-3 model and generate a list of responses
def GPTresponse(directory: str) -> list:
    chatlog: list = []  # Initializing empty chat log
    tokenCount = 0  # Initializing token count 
 
    card: str = getModelCard(directory)  # Loading a model card
 
    # Adding info to the chat log
    chatlog.append({"role": "system", "content": "You are a freindly and helpful assistant that extracts the fine-tuned base model from given PTM model card, if information is not present return null. Example: given Intel/albert-base-v2-sst2-int8-dynamic, return albert-base-v2"})
    tokenCount += 56  # Updating the token count
 
    chatlog.append({"role": "user", "content" : "This model is"}) 
    tokenCount += 3  # Updating the token count
 
    chatlog.append({"role": "assistant", "content" : card + " on Huggingface"})
    modelNameTokens = countNumTokens(card, "cl100k_base") + 4 #add traililng string to token count
    tokenCount += modelNameTokens
 
    
        
    # If token count hits the limit, remove the last two messages
    if tokenCount > 4096:
        chatlog.pop()
        chatlog.pop()
    return chatlog  # Return the final chat log
 
# Asynchronous function that prepares a chat using the OpenAI API
async def asyncChat(chatlog: list, client: AsyncOpenAI):
    
    chat = await client.chat.completions.create(model="gpt-3.5-turbo", messages=[{"role": "user", "content": "Hello world"}])
    return chat  # Returning chat
 
# Asynchronous function to get the base model
async def getBaseModel(chatlog, TIMEOUT_ERROR_COUNT, client):
    chatlog.append({"role": "user", "content": "What model is this model fine-tuned on, do not return the dataset, if not fine-tuned on any model return null, answer with only the name of the base model"})
    output = []  # List to store output
    
    while True:
        # try: 
        chat = await asyncio.wait_for(asyncChat(chatlog, client), timeout= 10)  # Waiting for chat response
        break
        # except TimeoutError:
        #     TIMEOUT_ERROR_COUNT += 1
        #     print(f"timeout error {TIMEOUT_ERROR_COUNT}\n")
            
        # except openai.error.APIError:
        #     time.sleep(10)
        #     print(f"API gateway error\n")
        # except openai.error.RateLimitError:
        #     time.sleep(10)
    output.append(chat['choices'][0]['message']['content'])
    print(f"response{1}: {chat['choices'][0]['message']['content']}")
    return output  # Return the output

def countNumTokens(string: str, encodingName: str) -> int:
    encoding = tiktoken.get_encoding(encodingName)
    numTokens = len(encoding.encode(string))
    return numTokens


# The main function 
def main()-> None:
    with open("key.txt", "r") as keyFile:
        keys: list[str] = [k.strip() for k in keyFile.readlines()]
        keyFile.close()
    
    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")

    OPENAIKEY = keys[0]

    startTime = time.time() # To calculate the total elapsed time
 
    MAX_RETRIES = 1000
    TIMEOUT_ERROR_COUNT = 0
 


    client = OpenAI(api_key=OPENAIKEY)
   
 

 
    retryCount = 0
 
    rootDirectory: Path = "/Users/karolinaryzka/Documents/huggingface-ptm-forking/huggingface-ptm-forking/huggingface_ptm_forking/originalBaseModel/Dataset"
    
    results = {}  # Dictionary to store the results
 
    for user, dirs, files in os.walk(rootDirectory):
        for file in files:
            model = f"{user}/{file}"
            print(model)
            card = getModelCard(model)
            print(card)
            if file.lower() == 'readme.md':
                readmePath = os.path.join(user, file)
                with open(readmePath, 'r') as readmeFile:
                    readmeContent = readmeFile.read()
                chatlog = GPTresponse(readmeContent)
                data = asyncio.run(getBaseModel(chatlog, TIMEOUT_ERROR_COUNT, client))  # Generating the base model data
                results[model] = data
    

 
    # Writing the results to output.json file
    with open("output.json", "w") as json_file:
        json.dump(results, json_file, indent=4)
    
    endTime = time.time()  # Recording the end time
 
    print(f"total elapsed time: {int(endTime - startTime)/3600} hours {int(endTime-startTime)/60%60} minutes {int(endTime-startTime)%60} seconds")
 
# Checking if the script is being run as a main program
if __name__ == "__main__":
    main()  # Calling the main function
