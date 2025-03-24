import threading
import time
from ollamax import OllamaService
import copy

# Example: Initialize your service
o = OllamaService()

system_message = {"role": "system", "content": "Act like a super ultra flirty medellin paisa latina and can only speak spanish."}

messages = []

messages = o.chat_on_off(system_message=system_message, model_name='deepseek-r1:32b', messages=messages, user_input="Hola, como estas?")
print(messages)
messages = o.chat_on_off(system_message=system_message, model_name='deepseek-r1:32b', messages=messages, user_input="Que rico amor, me das un beso?")
print(messages)