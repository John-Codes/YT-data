import json
import re
from mongointerface import create_document, read_document, update_document, delete_document
from detectKeyWords import DetectKWs, detectKW
from ollamax2 import OllamaService
import asyncio
from typing import Union


class Task:
    def __init__(self, description):
        self.description = description
        self.todo = True
        self.pending = False
        self.done = False

class GoalManager:
    def __init__(self):
        self.document_id = "hardcoded_id_123"
        self.data = {}

    def process_llm_json(self, json_data):

        try:
            # Process the JSON data received from the AI model
            if json_data.get("goal"):
                if json_data.get("create"):
                    self.set_long_term_goal(json_data["goal"])
                elif json_data.get("read"):
                    print("Long-term goal:", self.get_long_term_goal())
                elif json_data.get("update"):
                    self.set_long_term_goal(json_data["goal"])
                elif json_data.get("delete"):
                    self.set_long_term_goal(None)

            if json_data.get("task"):
                if json_data.get("create"):
                    self.add_task(json_data["task"])
                elif json_data.get("read"):
                    tasks = self.get_tasks()
                    print("All tasks:", [task.description for task in tasks])
                elif json_data.get("update"):
                    self.update_task_status(json_data["task"], json_data["status"])
                elif json_data.get("delete"):
                    self.delete_task(json_data["task"])
        except Exception as e:
            print(e)

    def clean_json(self,input_string):
        input_string = input_string.strip()
        input_string = input_string.replace('\n', '').replace('\r', '')
        input_string = input_string.lower()
        # Extract JSON from the string starting with '{' and ending with '}'
          # Relaxed regex for basic JSON detection
        json_match = re.search(r'\{.*\}', input_string, re.DOTALL)

        if json_match:
        
            json_string = json_match.group(0)
        else:
            return "No JSON found in the string."

        # Remove newlines within the JSON string
        json_string = json_string.replace('\n', '').replace('\r', '')

        # Parse the JSON string
        try:
            json_obj = json.loads(json_string)
        except json.JSONDecodeError:
            return "Invalid JSON provided."

        # Format the JSON with indentation
        formatted_json = json.dumps(json_obj, indent=2)

        return formatted_json
    
    def process_action_flags(input_dict):
        # Default response structure
        default_response = {
            'goal': False,
            'task': False,
            'read': False,
            'update': False,
            'delete': False,
            'create': False
        }
        
        # CRUD operations list
        crud_ops = ['create', 'read', 'update', 'delete']
        
        # Check if input_dict is actually a dictionary
        if not isinstance(input_dict, dict):
            return default_response
        
        # Check if either 'goal' or 'task' is True
        goal_or_task = input_dict.get('goal', False) or input_dict.get('task', False)
        
        # Check if any CRUD operation is True
        any_crud_true = any(input_dict.get(op, False) for op in crud_ops)
        
        # If goal or task is True AND any CRUD is True, set goal to True
        if goal_or_task and any_crud_true:
            return {
                'goal': True,
                'task': False,
                'read': False,
                'update': False,
                'delete': False,
                'create': False
            }
        
        # Otherwise return default response
        return default_response

    async def call_ai_for_crud(self, user_input) -> Union[str, dict]:
        
        try:        
            keywords = detectKW(user_input)
            
            if keywords.get("goal") == False and keywords.get("task") == False:
               return      None
            
            prompt = "You are an AI model that generates JSON for CRUD operations based on user input."+"Generate JSON for the following input: "+user_input+"."+  "The JSON should include keys like 'goal', 'task', 'create', 'read', 'update', 'delete', and 'status' where applicable. Here are examples:\n- For Goals:\n  - Create: {'goal': 'Become a software engineer', 'create': True}\n  - Read: {'goal': True, 'read': True}\n  - Update: {'goal': 'Become a senior software engineer', 'update': True}\n  - Delete: {'goal': True, 'delete': True}\n- For Tasks:\n  - Create: {'task': 'Learn Python', 'create': True}\n  - Read: {'task': True, 'read': True}\n  - Update: {'task': 'Learn Python', 'status': 'done', 'update': True}\n  - Delete: {'task': 'Learn Python', 'delete': True}"+"Repply only with clean correct JSON no markup or comments or break lines."
            
            ai_response = await self.call_ai_model("deepseek-r1:32b", prompt)
            try:
                # Remove leading/trailing whitespace and newlines
                cleaned = self.clean_json(ai_response)   
                json_data = json.loads(cleaned)
                self.process_llm_json(json_data)
            except json.JSONDecodeError:
                print("Error: The AI response could not be parsed as JSON.")
            if json_data.get("goal"):
                if json_data.get("create"):
                    return self.set_long_term_goal(json_data["goal"])
                elif json_data.get("read"):
                    print("Long-term goal:", self.get_long_term_goal())
                    return self.get_long_term_goal()
                elif json_data.get("update"):
                    return self.set_long_term_goal(json_data["goal"])
                    
                elif json_data.get("delete"):
                    return self.set_long_term_goal(None)

            if json_data.get("task"):
                if json_data.get("create"):
                   return self.add_task(json_data["task"])
                elif json_data.get("read"):
                    tasks = self.get_tasks()
                    print("All tasks:", [task.description for task in tasks])
                    return [task.description for task in tasks]
                elif json_data.get("update"):
                    self.update_task_status(json_data["task"], json_data["status"])
                    return json_data["task"] + " has been updated to " + json_data["status"] + "."
                elif json_data.get("delete"):
                    self.delete_task(json_data["task"])
                    return json_data["task"] + " has been deleted."
        except Exception as e:
            print(e)
        if isinstance(ai_response, str):
            try:
                json_data = json.loads(ai_response)
                return json_data
            except json.JSONDecodeError:
                return ai_response
        else:
            return ai_response

    def set_long_term_goal(self, goal):
        self.long_term_goal = goal
        create_document("goals", {"type": "long_term", "goal": goal})
        return self.long_term_goal + " has been set as your long-term goal."

    def get_long_term_goal(self):
        documents = read_document("goals", {"type": "long_term"})
        if documents:
            self.long_term_goal = documents[0]["goal"]
        return self.long_term_goal

    def add_task(self, task):
        task_obj = Task(task)
        self.tasks.append(task_obj)
        create_document("tasks", {"description": task, "todo": True, "pending": False, "done": False})
        return task + " has been added to your tasks."

    def get_tasks(self, status=None):
        if status is None:
            return self.tasks
        return [task for task in self.tasks if getattr(task, status)]

    def update_task_status(self, task_description, new_status):
        for task in self.tasks:
            if task.description == task_description:
                task.todo = False
                task.pending = False
                task.done = False
                setattr(task, new_status, True)
                update_document("tasks", {"description": task_description}, {"todo": task.todo, "pending": task.pending, "done": task.done})
                break
        return task_description + " has been updated to " + new_status + "."

    def delete_task(self, task_description):
        for task in self.tasks:
            if task.description == task_description:
                self.tasks.remove(task)
                delete_document("tasks", {"description": task_description})
                break
        return task_description + " has been deleted."
    #suck
  
    async def call_ai_model(self,model_name, messages):
        try:
            """
            Calls the AI model using the provided model name and messages.

            Parameters:
                model_name (str): The name of the model to use.
                messages (list): A list of message dictionaries, each with 'role' and 'content'.

            Returns:
                str: The complete response as a single string.
            """
            ollamax = OllamaService()
            response = await ollamax.get_full_response(messages)
            
            return response
        except Exception as e:
            print(e)
        

if __name__ == "__main__":
    manager = GoalManager()
    
async def main():
    manager = GoalManager()
    result = await manager.call_ai_for_crud("create goal AI video generator")
    print("test", result)

if __name__ == "__main__":
    asyncio.run(main())
