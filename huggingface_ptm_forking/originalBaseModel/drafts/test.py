import requests
from bs4 import BeautifulSoup
import openai


openai.api_key = "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"

def getModelCardInfo(modelName):
    try:
        # get model card page
        modelURL = f"https://huggingface.co/{modelName}"
        response = requests.get(modelURL)
        modelCard = response.text

        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(modelCard, 'html.parser')

        # Extract information from the model card
        baseModel = soup.find('div', {'class': 'relative group flex items-center'})  # Adjust class name based on the actual HTML structure

        # Extract base model information
        if baseModel:
            base_model_tag = baseModel.find('span', {'class': 'relative group flex items-center'})  # Adjust class name based on the actual HTML structure
            return base_model_tag.text.strip() if base_model_tag else None
        else:
            return None

    except Exception as e:
        print(f"Error: {e}")

    return None

def ask_chatgpt(question, model_name):
    try:
        # Use the ChatGPT API to ask a question
        response = openai.Completion.create(
            model=model_name,
            prompt=f"Model card: {question}",
            temperature=0,
            max_tokens=200,
            stop=None
        )

        # Extract the answer from the response
        answer = response['choices'][0]['text']

        return answer

    except Exception as e:
        print(f"Error: {e}")

    return None

def main():
    modelName = input("Enter the fine-tuned model name: ")
    
    # Get base model information from the Hugging Face Model Hub
    base_model_from_hub = getModelCardInfo(modelName)

    if base_model_from_hub:
        print(f"The base model of {modelName} according to the Model Hub is: {base_model_from_hub}")

        # Ask ChatGPT for additional information
        question = "What is the base model of this fine-tuned model?"
        answer_from_chatgpt = ask_chatgpt(question, modelName)

        if answer_from_chatgpt:
            print(f"ChatGPT says: {answer_from_chatgpt}")

    else:
        print(f"Failed to retrieve information for {modelName}.")

if __name__ == "__main__":
    main()
