
import json
from ollamax2 import OllamaService
from detectKeyWords import DetectKWs, detectKW
from mongointerface import create_document, read_document, update_document, delete_document
# from goals import GoalManager
from newgoal import DocumentManager

# Initialize your service
o = OllamaService()
#activate new goal
crud = DocumentManager()

# goal_manager = GoalManager()
MainGoal = "LED SIGN TRUCK BUSINESS"
tasks=

system_message = {"role": "system", "content": ""}

messages = []

async def process_user_input(user_input):
    try:
        #call DetectKWs to detect keywords in the user input
        keywords = detectKW(user_input)
        print("Keywords detected: ",keywords)
        
        print("CRUD result: ",ai_response)
        return ai_response

    except  Exception as e:
        print("Error: The AI response could not be parsed as JSON.")
   
   

   
      

async def run_chat_loop():

    messages = [
      # System message to guide the conversation
    {"role": "user", "content": ""}  # Placeholder for user input
]
    messages.append(system_message)
    message={"role": "user", "content": ""}
    chat_on = True
    while True:
        if chat_on:
            user_input = input("Enter your message: ")
            #user_input = "create goal AI video generator"
            messages.append({"role": "user", "content": user_input})
            #first detect keywords on the user input if there are keywords then route the user input to the appropriate function
            data = await process_user_input(user_input)
          
            messages = o.chat_on_off(system_message=system_message, model_name='deepseek-r1:32b', messages=messages, user_input=user_input+data)
            print(messages)
         
        else:
            print("Chat is off. Press Enter to toggle chat on.")
            input()
        
        chat_on = not chat_on

import asyncio

if __name__ == "__main__":
    asyncio.run(run_chat_loop())
