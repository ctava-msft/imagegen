# This file is a reference example for Azure OpenAI.
# ITS NOT PART OF THE PROJECT
import os
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
      
completion = client.chat.completions.create(
    model=deployment,
    messages= [
    {
      "role": "user",
      "content": "What are the differences between Azure Machine Learning and Azure AI services?"
    }],
    max_tokens=800,
    temperature=0.7,
    top_p=0.95,
    frequency_penalty=0,
    presence_penalty=0,
    stop=None,
    stream=False
)
print(completion.to_json())






###### sevice.py
from azure.cosmos import CosmosClient
import openai
from .models import Message

# Set up CosmosDB client
client = CosmosClient('your-cosmosdb-endpoint', 'your-cosmosdb-key')
database = client.get_database_client('your-database-name')
container = database.get_container_client('your-container-name')

# OpenAI setup
openai.api_key = 'your-openai-api-key'

def check_cache_for_message(session_id, user_input):
    # Query CosmosDB to see if this message exists for the given session
    query = "SELECT * FROM c WHERE c.session_id=@session_id AND c.user_input=@user_input"
    parameters = [
        {"name": "@session_id", "value": session_id},
        {"name": "@user_input", "value": user_input}
    ]
    items = list(container.query_items(query, parameters=parameters, enable_cross_partition_query=True))

    if items:
        return items[0]  # Return the first cached response

    return None

def generate_chat_response(user_input):
    # Call the OpenAI API to generate a response
    response = openai.ChatCompletion.create(
        model="gpt-4",  # You can switch to "gpt-3.5-turbo" or another model if desired
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": user_input}
        ],
        max_tokens=150,
        temperature=0.7
    )
    return response['choices'][0]['message']['content']

def save_message_to_cache(session, user_input, gpt_response):
    # Save the new message to CosmosDB and Django's database
    container.create_item({
        'session_id': session.session_id,
        'user_input': user_input,
        'gpt_response': gpt_response
    })

    # Also save it in Django's DB
    Message.objects.create(session=session, user_input=user_input, gpt_response=gpt_response)


# views.py 
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Session, Message
from .services import generate_chat_response, check_cache_for_message, save_message_to_cache
import json

@csrf_exempt  # CSRF exemption for simplicity in dev, handle CSRF properly in production
def chatgpt_response(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            session_id = data.get('session_id')
            user_input = data.get('user_input')

            # Check if the session exists or create a new one
            session, created = Session.objects.get_or_create(session_id=session_id)

            # Check if the message is cached (i.e., check CosmosDB for a cached response)
            cached_message = check_cache_for_message(session_id, user_input)
            if cached_message:
                return JsonResponse({'response': cached_message.gpt_response})

            # No cached response, generate a new one using OpenAI
            gpt_response = generate_chat_response(user_input)

            # Save the new message to cache
            save_message_to_cache(session, user_input, gpt_response)

            # Return the new GPT response
            return JsonResponse({'response': gpt_response})

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


client = openai.AzureOpenAI(
  azure_endpoint=openai.api_base, 
  api_key=openai.api_key,  
  api_version=openai.api_version
)
response = client.chat.completions.create( 
    model=openai_deployment_completion,
    messages = [{'role':'system','content':prompt}],
    temperature=0, 
    max_tokens=600,
    stream=False)
print(response.choices[0].message.content)
