from .models import CacheItem
from azure.cosmos import CosmosClient, PartitionKey, exceptions
from openai import AzureOpenAI
from flask import current_app

import os

# os.environ.get("NAME")

from dotenv import load_dotenv

config = load_dotenv()
AOAI_COMPLETION_DEPLOYMENT = current_app.config['AOAI_COMPLETION_DEPLOYMENT']
AOAI_KEY = current_app.config['AOAI_KEY']
AOAI_ENDPOINT = current_app.config['AOAI_ENDPOINT']
API_VERSION = '2024-02-01'

class AIService:
    def __init__(self):
        self.endpoint = os.environ.get('AOAI_ENDPOINT')  # Use os.getenv
        self.key = os.environ.get('AOAI_KEY')  # Use os.getenv
        self.client = AzureOpenAI(
            azure_endpoint=self.endpoint,
            api_key=self.key,
            api_version=API_VERSION
        )
        
    def get_completion(self, prompt):
        try:
            completion = self.client.chat.completions.create(
            model=AOAI_COMPLETION_DEPLOYMENT,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=800,
                temperature=0.7,
                top_p=0.95,
                frequency_penalty=0,
                presence_penalty=0,
                stop=None,
                stream=False
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(f"Error getting completion: {e}")
            return "An error occurred while generating a response."
    
def check_cache(prompt):
    return CacheItem.objects.filter(prompts=prompt).first()

def save_to_cache(vectors, prompt, completion):
    cache_item = CacheItem(vectors=vectors, prompts=prompt, completion=completion)
    cache_item.save()
    return cache_item