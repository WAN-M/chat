from django.test import TestCase

# Create your tests here.
from chat_models import OllamaModel

model = OllamaModel()
res = model.chat_response("what is the smallest prime number")
print(res)