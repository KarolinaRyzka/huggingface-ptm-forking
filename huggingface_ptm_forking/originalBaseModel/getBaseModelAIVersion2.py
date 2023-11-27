from openai import AsyncOpenAI, OpenAI
import time
from pathlib import Path
import os
import tiktoken
import json

def countNumTokens(string: str, encodingName: str) -> int:
    encoding = tiktoken.get_encoding(encodingName)
    numTokens = len(encoding.encode(string))
    return numTokens


def numTokensFromMessages(chatLog: list, model="cl100k_base"):
    encoding = tiktoken.get_encoding(model)
    numTokens = 0
    for message in chatLog:
        numTokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
        for key,value in message.items():
            numTokens += len(encoding.encode(value))
            if key == "name":
                numToken -= 1 #role is required and always 1 token    
    numTokens += 2  # every reply is primed with <im_start>assistant
    return numTokens

def main()-> None:
    
    startTime = time.time()
    client = OpenAI()
    rootDirectory: Path = "/Users/karolinaryzka/Documents/huggingface-ptm-forking/huggingface-ptm-forking/huggingface_ptm_forking/originalBaseModel/Dataset"

    results = {}  # Dictionary to store the results
    maxTokens = 4096
    maxResponseTokens = 100
    tokenCount: int = 0
    chatLog = []

    for folderName, subFolders, filenames in os.walk(rootDirectory):
        for file in filenames:
            if(file.endswith(".md")):
                filePath = os.path.join(folderName, file)

                with open(filePath, 'r') as file:
                    fileContents = file.read()
                    #print(fileContents)
                    messageSys = {"role": "system", "content": "You are a helpful assistant that extracts the fine-tuned base model name from given PTM model card, if information is not present return the string: 'null'. Only respond with the name of the base model without any other text."}
                    messageUser = {"role": "user", "content": "Identify the name of the base model that this pre-trained model was finetuned on: " + fileContents}
                    messages = [
                        {"role": "system", "content": "You are a helpful assistant that extracts the fine-tuned base model name from given PTM model card, if information is not present return the string: 'null'. Only respond with the name of the base model without any other text."},
                        {"role": "user", "content": "Identify the name of the base model that this pre-trained model was finetuned on: " + fileContents}
                    ]
                
                    chatLog.append(messageSys)
                    chatLog.append(messageUser)
                    chatlogHistoryTokens = numTokensFromMessages(chatLog)

                    while (chatlogHistoryTokens+maxResponseTokens >= maxTokens):
                        del chatLog[1]
                        chatlogHistoryTokens = numTokensFromMessages(chatLog)

                    completion = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages= messages, 
                        max_tokens=maxResponseTokens
                    )   
                    
                    data = completion.choices[0].message.content
                    chatLog.append({"role": "assistant", "content": completion.choices[0].message.content})
                    print(str(filePath))

                    print(completion.choices[0].message)
                    sub = filePath.split('/')
                    modelName = '/'.join(sub[-3:-1])

                    results[str(modelName)] = data
                    time.sleep(5)
                    

    with open("outputAI.json", "w") as json_file:
        json.dump(results, json_file, indent=4)

 

if __name__ == "__main__":
    main()  # Calling the main function
