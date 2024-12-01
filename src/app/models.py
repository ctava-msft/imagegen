from datetime import datetime, timezone
import uuid
from azure.cosmos import CosmosClient, exceptions
from config import Config

# Initialize Cosmos DB Client
client = CosmosClient(Config.COSMOS_ENDPOINT, credential=Config.COSMOS_KEY)
database = client.get_database_client(Config.COSMOS_DATABASE)
container = database.get_container_client(Config.COSMOS_CONTAINER)

# CacheItem Model
class CacheItem:
    def __init__(self, id, vectors, prompts, completion):
        self.id = id
        self.vectors = vectors
        self.prompts = prompts
        self.completion = completion
        self.created_at = datetime.now(timezone.utc).isoformat() # Timestamp for cache invalidation purposes

    def save(self):
        item = {
            'id': self.id,
            'vectors': self.vectors,
            'prompts': self.prompts,
            'completion': self.completion,
            'created_at': self.created_at
        }
        # Save to Cosmos DB
        try:
            container.upsert_item(item)
            print(f"CacheItem {self.id} saved to Cosmos DB.")
        except Exception as e:
            print(f"Error saving CacheItem {self.id}: {e}")


    def __str__(self):
        return f'CacheItem {self.id} - Prompt: {self.prompts[:50]}'


# Message Model
class Message:
    def __init__(self, session_id, prompt, prompt_tokens=0, completion='', completion_tokens=0):
        self.id = str(uuid.uuid4())
        self.session_id = session_id
        self.timestamp = datetime.now(timezone.utc).isoformat()
        self.prompt = prompt
        self.prompt_tokens = prompt_tokens
        self.completion = completion
        self.completion_tokens = completion_tokens

    def __str__(self):
        return f'Message {self.id} in Session {self.session.id} - Prompt: {self.prompt[:50]}'
    
    def save(self):
        item = {
            'id': self.id,
            'session_id': self.session_id,
            'timestamp': self.timestamp,
            'prompt': self.prompt,
            'prompt_tokens': self.prompt_tokens,
            'completion': self.completion,
            'completion_tokens': self.completion_tokens
        }
               # Save to Cosmos DB
        try:
            container.upsert_item(item)
            print(f"Message {self.id} saved to Cosmos DB.")
        except Exception as e:
            print(f"Error saving Message {self.id}: {e}")

    def generate_completion(self):
        from services import AIService
        ai_service = AIService()
        self.completion = ai_service.get_completion(self.prompt)
        self.completion_tokens = len(self.completion.split())  # Set completion tokens based on generated completion
    

# Session Model
class Session:
    def __init__(self, session_id=None, tokens=None, name='New Chat'):
        self.session_id = session_id or str(uuid.uuid4())
        self.tokens = tokens or 0
        self.name = name

    def __str__(self):
        return f'Session {self.session_id} - {self.name}'

    def add_message(self, prompt, prompt_tokens, completion='', completion_tokens=0):
        # Create and save the message
        message = Message(
            session_id=self.session_id,
            prompt=prompt,
            prompt_tokens=prompt_tokens,
            completion=completion,
            completion_tokens=completion_tokens
        )
        message.save()

        # Update session tokens
        self.tokens += prompt_tokens + completion_tokens
        self.save()  # Save the session after updating tokens

    def save(self):
        # Create a session item to save
        session_item = {
            "id": self.session_id,
            "tokens": self.tokens,
            "name": self.name
        }

        # Insert or update the session item in the container
        try:
            container.create_item(session_item)  # Create a new session item
        except exceptions.CosmosHttpResponseError as e:
            # If the item already exists, you might want to update it
            if e.status_code == 409:  # Conflict
                container.upsert_item(session_item)  # Upsert (insert or update)   
