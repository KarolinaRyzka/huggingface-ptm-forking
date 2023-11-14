import openai
from huggingface_hub import HfApi, ModelCard
import time
from pathlib import Path
import os
import tokenizer
import json
import asyncio
import key as key


#loads model card from given modelname string
def loadModelCard(modelName: str):
    card = ModelCard.load(modelName)
    return card.content

def formatCard(card):

    #empty dict
    sections = {}
    #split model card based on sections with the delimeter "##""
    subsection = card.split("## ")

    #traverse each subsection, return sections of each card in dict
    for section in subsection:
        section = sections[section.split("\n")[0]]
    return sections

def GPTresponse(modelName: str) -> list:
    chatlog: list = []
    tokenCount = 0
    card = loadModelCard(modelName)
    subsections = formatCard(card)
    chatlog.append({"role" : "system", "content" : "extract the fine-tuned base model from given PTM model card, if information not present return null. example: given Intel/albert-base-v2-sst2-int8-dynamic, return albert-base-v2 \n"})
    tokenCount += 58
    chatlog.append({"role": "user", "content" : "this model is"}) 
    tokenCount += 16
    chatlog.append({"role": "assistant", "content" : modelName + " on huggingface"})
    tokenCount += tokenizer.num_tokens_in_chat({"role": "assistant", "content" : modelName + " on huggingface"})
    for sectionHeaders in subsections:
            chatlog.append({"role": "user", "content" : "the model" + sectionHeaders})
            tokenCount += tokenizer.num_tokens_in_chat({"role": "user", "content" : "the model" + sectionHeaders})
            chatlog.append({"role" : "assistant", "content" : subsections[sectionHeaders]})
            tokenCount += tokenizer.num_tokens_in_chat({"role" : "assistant", "content" : subsections[sectionHeaders]})
            #remove last two messages if token count is at limit
            if tokenCount > 4096:
                temp = chatlog.pop()
                temp = chatlog.pop()
                break
    return chatlog

async def asyncChat(chatlog: list):
    chat = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo",
        messages = chatlog
    )
    return chat

async def getBaseModel(chatlog, TIMEOUT_ERROR_COUNT):
    chatlog.append({"role": "user", "content": "What model is this model fine-tuned on, do not return the dataset, if not fine-tuned on any model return null, answer with only the name of the base model"})

    output = []
    
    while True:
        try: 
            chat = await asyncio.wait_for(asyncChat(chatlog), timeout= 10)
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
    print(f"resoponse{1}: {chat['choices'][0]['message']['content']}")

    return output

def main()-> None:

    startTime = time.time()

    MAX_RETRIES = 1000
    TIMEOUT_ERROR_COUNT = 0


    hfAPI = HfApi(
    endpoint = "https://huggingface.co",
    token = "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",
    )

    openai.api_key = "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"

    retryCount = 0

    rootDirectory: Path = "/Users/karolinaryzka/Documents/huggingface-ptm-forking/huggingface-ptm-forking/huggingface_ptm_forking/originalBaseModel/Dataset"
    
    results = {}

    for user, dirs, files in os.walk(rootDirectory):
        for filename in files:
            model = f"{user}/{filename}"
            print(model)

            chatlog = GPTresponse(model)
            data = asyncio.run(getBaseModel(chatlog, TIMEOUT_ERROR_COUNT))

            results[model] = data

    with open("output.json", "w") as json_file:
        json.dump(results, json_file, indent=4)

    endTime = time.time()

    print(f"total elapsed time: {int(endTime - startTime)/3600} hours {int(endTime-startTime)/60%60} minutes {int(endTime-startTime)%60} seconds")

    


if __name__ == "__main__":
    main()



