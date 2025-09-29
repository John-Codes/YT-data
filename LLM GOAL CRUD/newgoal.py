import json

class DocumentManager:
    document = {"id": "hardcoded_goal_id"}  # Initial document with just the ID

    @staticmethod
    def update(user_input): 
        # Simulate LLM replacing the entire document
        # In a real system, this calls an LLM API: new_doc = llm_api(user_input)
        new_doc = DocumentManager._simulate_llm(user_input)
        DocumentManager.document = new_doc
        return DocumentManager.document

    @staticmethod
    def read():
        print("goal data:",json.dumps(DocumentManager.document, indent=2) if DocumentManager.document else "No document")
        return DocumentManager.document

    @staticmethod
    def delete():
        DocumentManager.document = {"id": "hardcoded_goal_id"}  # Reset to just ID
        return DocumentManager.document

    @staticmethod
    def _simulate_llm(user_input):
        # Placeholder: mimics LLM creating a new document
        # Real LLM would generate any JSON structure it wants
        return {"id": "hardcoded_goal_id", "data": user_input}
    
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


# Example usage
if __name__ == "__main__":
    d=DocumentManager.update("I want to learn Python")
    print(d)
    d=DocumentManager.read()
    print(d)
    d=DocumentManager.update("Now learning Java")
    print(d)
    d=DocumentManager.read()
    print(d)
    d=DocumentManager.delete()
    print(d)    
    d =DocumentManager.read()
    print(d)


