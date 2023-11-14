from openai import OpenAI
from huggingface_hub import HfApi, ModelCard
import time
from pathlib import Path
import os
import tokenizer
import json
import asyncio
 
# Function to load model card from given model name string
def loadModelCard(modelName: str):
    card = ModelCard.load(modelName)
    return card.content  # Returning the content of the ModelCard
 
# Function to format the model card
def formatCard(card):
    # Initialising an empty dictionary
    sections = {}
    
    # Splitting model card based on sections with the delimeter "##""
    subsection = card.split("## ")
 
    for section in subsection:
        # Adding each section to the sections dictionary
        sections[section.split("\n")[0]] = section.split("\n")[1:]
    return sections  # Returning sections of each card in dict form
 
# Function to interact with the GPT-3 model and generate a list of responses
def GPTresponse(modelName: str) -> list:
    chatlog: list = []  # Initializing empty chat log
    tokenCount = 0  # Initializing token count 
 
    card = loadModelCard(modelName)  # Loading a model card
    subsections = formatCard(card)  # Formatting the model card
 
    # Adding info to the chat log
    chatlog.append({"role": "system", "content": "Extract the fine-tuned base model from given PTM model card, if information not present return null. Example: given Intel/albert-base-v2-sst2-int8-dynamic, return albert-base-v2 "})
    tokenCount += 58  # Updating the token count
 
    chatlog.append({"role": "user", "content" : "This model is"}) 
    tokenCount += 16  # Updating the token count
 
    chatlog.append({"role": "assistant", "content" : modelName + " on Huggingface"})
    tokenCount += tokenizer.num_tokens_in_chat({"role": "assistant", "content" : modelName + " on Huggingface"})
 
    # Interacting with the subsections in the model card and adding them to the chat log
    for sectionHeaders in subsections:
        chatlog.append({"role": "user", "content" : "the model " + sectionHeaders})
        tokenCount += tokenizer.num_tokens_in_chat({"role": "user", "content" : "the model " + sectionHeaders})
        chatlog.append({"role" : "assistant", "content" : subsections[sectionHeaders]})
        tokenCount += tokenizer.num_tokens_in_chat({"role" : "assistant", "content" : subsections[sectionHeaders]})
        
        # If token count hits the limit, remove the last two messages
        if tokenCount > 4096:
            chatlog.pop()
            chatlog.pop()
            break
    return chatlog  # Return the final chat log
 
# Asynchronous function that prepares a chat using the OpenAI API
async def asyncChat(chatlog: list):
    chat = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo",
        messages = chatlog
    )
    return chat  # Returning chat
 
# Asynchronous function to get the base model
async def getBaseModel(chatlog, TIMEOUT_ERROR_COUNT):
    chatlog.append({"role": "user", "content": "What model is this model fine-tuned on, do not return the dataset, if not fine-tuned on any model return null, answer with only the name of the base model"})
    output = []  # List to store output
    
    while True:
        try: 
            chat = await asyncio.wait_for(asyncChat(chatlog), timeout= 10)  # Waiting for chat response
            break
        except TimeoutError:
            TIMEOUT_ERROR_COUNT += 1
            print(f"timeout error {TIMEOUT_ERROR_COUNT}\n")
        except openai.error.APIError:
            time.sleep(10)
            print(f"API gateway error\n")
        except openai.error.RateLimitError:
            time.sleep(10)
    output.append(chat['choices'][0]['message']['content'])
    print(f"response{1}: {chat['choices'][0]['message']['content']}")
    return output  # Return the output
 
# The main function 
def main()-> None:
    with open("key.txt", "r") as keyFile:
        keys: list[str] = [k.strip() for k in keyFile.readlines()]
        keyFile.close()
    
    OPENAIKEY = keys[0]
    HFKEY = keys[1]
    startTime = time.time() # To calculate the total elapsed time
 
    MAX_RETRIES = 1000
    TIMEOUT_ERROR_COUNT = 0
 
    hfAPI = HfApi(
    endpoint = "https://huggingface.co",
    token = HFKEY,
    )
 
    openai.api_key = OPENAIKEY
 
    retryCount = 0
 
    rootDirectory: Path = "/Users/karolinaryzka/Documents/huggingface-ptm-forking/huggingface-ptm-forking/huggingface_ptm_forking/originalBaseModel/Dataset"
    
    results = {}  # Dictionary to store the results
 
    for user, dirs, files in os.walk(rootDirectory):
        for filename in files:
            model = f"{user}/{filename}"
            print(model)
 
            chatlog = GPTresponse(model)
            
            data = asyncio.run(getBaseModel(chatlog, TIMEOUT_ERROR_COUNT))  # Generating the base model data
 
            results[model] = data
 
    # Writing the results to output.json file
    with open("output.json", "w") as json_file:
        json.dump(results, json_file, indent=4)
    
    endTime = time.time()  # Recording the end time
 
    print(f"total elapsed time: {int(endTime - startTime)/3600} hours {int(endTime-startTime)/60%60} minutes {int(endTime-startTime)%60} seconds")
 
# Checking if the script is being run as a main program
if __name__ == "__main__":
    main()  # Calling the main function
