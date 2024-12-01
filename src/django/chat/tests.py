# Create your tests here.
from django.test import TestCase
from .models import Session, Message, CacheItem

class ChatgptModelTests(TestCase):
    def test_create_session(self):
        session = Session.objects.create(name="Test Session")
        self.assertIsNotNone(session.id)

    def test_add_message(self):
        session = Session.objects.create(name="Test Session")
        message = Message.objects.create(
            session_id=session.id,
            prompt="Hello, how are you?",
            prompt_tokens=5,
            completion="I'm fine, thank you!",
            completion_tokens=5
        )
        session.add_message(message)
        self.assertIn(message, session.messages.all())
