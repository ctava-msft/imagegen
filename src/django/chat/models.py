# from django.db import models
# from django.utils import timezone
import uuid

# CacheItem Model
class CacheItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vectors = models.JSONField(null=True)  # Cache vectors
    prompts = models.TextField(null=True)
    completion = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp for cache invalidation purposes


    def __str__(self):
        return f'CacheItem {self.id} - Prompt: {self.prompts[:50]}'


# Message Model
# This model stores individual user prompts and OpenAI-generated responses within a session.
class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey('Session', related_name='messages', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now)
    prompt = models.TextField()  # User input
    prompt_tokens = models.IntegerField()  # Tokens used for the prompt
    completion = models.TextField(blank=True, null=True)  # GPT-generated response
    completion_tokens = models.IntegerField(default=0)  # Tokens used for the completion

    def __str__(self):
        return f'Message {self.id} in Session {self.session.id} - Prompt: {self.prompt[:50]}'
    
    def generate_completion(self):
        from .services import AIService
        ai_service = AIService()
        completion = self.completion = ai_service.get_completion(self.prompt)
        return completion
    

# Session Model
class Session(models.Model):
    session_id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True)
    tokens = models.IntegerField(default=0, null=True, blank=True)  # Total tokens used in the session
    name = models.CharField(max_length=100, default='New Chat')  # Name of the session

    def __str__(self):
        return f'Session {self.session_id} - {self.name}'

    def add_message(self, prompt, prompt_tokens, completion='', completion_tokens=0):
        # Create and save the message
        message = Message(
            session=self,
            prompt=prompt,
            prompt_tokens=prompt_tokens,
            completion=completion,
            completion_tokens=completion_tokens
        )
        message.save()

        # Update session tokens
        self.tokens = (self.tokens or 0) + prompt_tokens + completion_tokens
        self.save()

    def update_message(self, message_id, prompt=None, completion=None, completion_tokens=None):
        message = self.messages.get(id=message_id)
        if prompt is not None:
            message.prompt = prompt
        if completion is not None:
            message.completion = completion
        if completion_tokens is not None:
            self.tokens = (self.tokens or 0) + completion_tokens - message.completion_tokens
            message.completion_tokens = completion_tokens
        message.save()
        self.save()
