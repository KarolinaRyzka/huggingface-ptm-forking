import huggingface_hub
import openai
from huggingface_hub import HfApi, list_models, ModelCard
import time
import formatData
from Collections import Counter
import argparse
import os
import tokenizer
import json
import asyncio
import keys

startTime = time.time()
TIMEOUTERROR = 0;


parser = argparse.ArgumentParser(description="Pipeline for identifying base models from HF model cards")
parser.add_argument("--name", choices=["nameAndModel"], required=True, help="user and model name required")
args = parser.parse_args()

hfAPI = HfApi(
    endpoint = "https://huggingface.co"

)

openai.api_key = keys.OPENAI_API_KEY

#loads model card from given modelname string
def loadModelCard(modelName: str):
    card = ModelCard.load(modelName)
    return card.content

def GPTresponse(modelName: str) -> list:
    chatlog: list = []
    tokenCount = 0;
    card = loadModelCard(modelName)
    subsections = formatData.formatCard(card)
    chatlog.append({"role" : "system", "content" : "extract the fine-tuned base model from given PTM model card, if information not present return null. example: given Intel/albert-base-v2-sst2-int8-dynamic, return albert-base-v2 \n"})
    tokenCount += 26
    chatlog.append({"role": "user", "content" : "this model is"}) 
    tokenCount += 16
    chatlog.append({"role": "assistant", "content" : modelName + " on huggingface"})
    tokenCount += tokenizer.num_tokens_in_chat({"role": "assistant", "content" : modelName + " on huggingface"})
    for sectionHeaders in subsections:
            chatlog.append({"role": "user", "content" : "the model" + sectionHeaders})
            tokenCount += tokenizer.num_tokens_in_chat({"role": "user", "content" : "the model" + sectionHeaders})
            chatlog.append({"role" : "assistant", "content" : subsections[sectionHeaders]})
            tokenCount += tokenizer.num_tokens_in_chat({"role" : "assistant", "content" : subsections[sectionHeaders]})
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

async def getBaseModel(chatlog):
    chatlog.append({"role": "user", "content": "What model is this model fine-tuned on, do not return the dataset, if not fine-tuned on any model return null, answer with only the name of the base model"})

    output = []
    for i in range(5):
        while True:
            try: 
               chat = await asyncio.wait_for(asyncChat(chatlog), timeout= 10)
               break
            except TimeoutError:
                TIMEOUTERROR += 1
                print(f"timeout error {TIMEOUTERROR}\n")
            except openai.error.APIError:
                time.sleep(10)
                print(f"API gateway error\n")
            except openai.error.RateLimitError:
                time.sleep(10)
        output.append(chat['choices'][0]['message']['content'])
        print(f"resoponse{i+1}: {chat['choices'][0]['message']['content']}")

    return output



retryCount = 0

rootDirectory = " "
results = {}

for user, dirs, files in os.walk(rootDirectory):
    for filename in files:
        model = f"{user}/{filename}"

        chatlog = GPTresponse(model)
        data = asyncio.run(getBaseModel(chatlog))

        results[model] = data

with open("output.json", "w") as json_file:
    json.dump(results, json_file, indent=4)

endTime = time.time()

print(f"total elapsed time: {int(endTime - startTime)/3600} hours {int(endTime-startTime)/60%60} minutes {int(endTime-startTime)%60} seconds")





