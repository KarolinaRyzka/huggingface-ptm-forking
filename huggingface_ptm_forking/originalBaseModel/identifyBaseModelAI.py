import huggingface_hub
import openai
from huggingface_hub import HfApi, list_models, ModelCard
import time
import formatData
import argparse
import tokenizer
import json
import asyncio
import keys

startTime = time.time()

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
            token_count += tokenizer.num_tokens_in_chat({"role": "user", "content" : "the model" + sectionHeaders})
            chatlog.append({"role" : "assistant", "content" : subsections[sectionHeaders]})
            token_count += tokenizer.num_tokens_in_chat({"role" : "assistant", "content" : subsections[sectionHeaders]})
            if token_count > 4096:
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



