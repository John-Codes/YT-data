import re
import subprocess
from ollama import chat
from ollama import ChatResponse
import ollama

class OllamaService:
    @staticmethod
    def start_service():
        """Start the Ollama service."""
        try:
            subprocess.run("sudo systemctl start ollama", shell=True, check=True)
            print("Service started successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to start service: {e}")

    @staticmethod
    def stop_service():
        """Stop the Ollama service."""
        try:
            subprocess.run("sudo systemctl stop ollama", shell=True, check=True)
            print("Service stopped successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to stop service: {e}")

    @staticmethod
    def disable_auto_start():
        """Disable auto-start for the Ollama service."""
        try:
            subprocess.run("sudo systemctl disable ollama", shell=True, check=True)
            print("Auto-start disabled successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to disable auto-start: {e}")

    @staticmethod
    def check_service_status():
        """Check the status of the Ollama service."""
        try:
            subprocess.run(" systemctl status ollama", shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Failed to check service status: {e}")

    @staticmethod
    def view_logs():
        """View logs for the Ollama service."""
        try:
            subprocess.run("journalctl -e -u ollama", shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Failed to view logs: {e}")

    @staticmethod
    def check_loaded_models():
        """Check the loaded models."""
        try:
            subprocess.run("curl http://localhost:11434/api/ps", shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Failed to check loaded models: {e}")

    @staticmethod
    def manual_start():
        """Manually start the Ollama service."""
        try:
            subprocess.run("nohup ollama serve &", shell=True, check=True)
            print("Service started manually.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to manually start service: {e}")

    @staticmethod
    def manual_stop():
        """Manually stop the Ollama service."""
        try:
            subprocess.run("pkill ollama", shell=True, check=True)
            print("Service stopped manually.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to manually stop service: {e}")

    @staticmethod
    def unload_specific_model(model_name):
        """Unload a specific model."""
        try:
            subprocess.run(f"ollama stop {model_name}", shell=True, check=True)
            print(f"Model '{model_name}' unloaded successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to unload model '{model_name}': {e}")

 
 
    @staticmethod
    def load(model_name):
        return chat(model=model_name, messages=[], keep_alive=-1)

    @staticmethod
    def unload(model_name):
        return chat(model=model_name, messages=[], keep_alive=0)

    @staticmethod
    def stream_response(model_name, messages, stream=True):
        """
        Streams the response from the Ollama API.

        Parameters:
            model_name (str): The name of the model to use.
            messages (list): A list of message dictionaries, each with 'role' and 'content'.
            stream (bool): Whether to enable streaming (default is True).

        Returns:
            str: The complete streamed response as a string.
        """
        stream_output = ""
        stream_instance = chat(
            model=model_name,
            messages=messages,
            stream=stream
        )
        for chunk in stream_instance:
            content = chunk['message']['content']
            print(content, end='', flush=True)  # Print as it streams
            stream_output += content
        return stream_output

    @staticmethod
    async def get_full_response( txtprompt,model_name="deepseek-r1:32b"):
        try:
            """
            Returns the full response from the Ollama API as a single string.

            Parameters:
                model_name (str): The name of the model to use.
                messages (list): A list of message dictionaries, each with 'role' and 'content'.

            Returns:
                str: The complete response as a single string.

            OllamaService.manual_start()
            OllamaService.load(model_name)
            """
            # OllamaService.check_service_status()
            # OllamaService.check_loaded_models()
            #print method is runing in blue
            print("\033[94m" + "OllamaService.get_full_response() called." + "\033[0m") 
            
            output=""
            a= ollama.generate(model=model_name, prompt=txtprompt)
#wait 30 seconds for the response
            
            # output = await ollama.generate(model=model_name, prompt=txtprompt)
            a=a['response']
            output= OllamaService.remove_think_tags(a)
            OllamaService.unload(model_name)
            OllamaService.manual_stop()
            return output  # Assuming this is the structure of the response
        except Exception as e:
            print(e)


    @staticmethod
    def remove_think_tags(text):
        # Define the pattern to match text between <think> and </think> tags
        pattern = re.compile(r'<think>\n.*?\n</think>', re.DOTALL)

        # Substitute the matched pattern with an empty string
        result = pattern.sub('', text)

        return result    

    @staticmethod
    def chat_stream_console(model_name='deepseek-r1:32b', messages=[], stream=True):
        stream_instance = chat(
            model=model_name,
            messages=messages,
            stream=stream,
        )
        message=""
        # Removed the thinking part (printing to console)

        for chunk in stream_instance:
            #convert chunks to string and append to message
            message+=chunk['message']['content']
            print(chunk['message']['content'], end='', flush=True)
        #remove the thinking tags 
        message = OllamaService.remove_think_tags(message)
        return message
    
   


    @staticmethod
    def chat_on_off(system_message=None, model_name='deepseek-r1:32b', messages=None, user_input=None, stream=True):
        # Ensure system_message is provided as a dictionary
        if system_message is None:
            system_message = {"role": "system", "content": "Initial system message"}
        
        # Ensure messages is provided and initialized
        if messages is None or len(messages) == 0:
            messages = [system_message]  # Add the default system message

        # Ensure user_input is provided
        if user_input is None:
            raise ValueError("user_input parameter cannot be None")

        ollama = OllamaService()
        
        # Start the service and load the model
        ollama.manual_start()
       
        ollama.load(model_name)
        ollama.check_loaded_models()

        # Append the user's message to the messages list
        messages.append({'role': 'user', 'content': user_input})

        # Generate a response using Ollama
        assistant_message = ollama.chat_stream_console(model_name, messages)
        messages.append({'role': 'assistant', 'content': assistant_message})

        # Unload model and stop service (optional for stateless mode)
        ollama.unload(model_name)
        ollama.manual_stop()

        # Return the updated messages list
        return messages

# Example usage
import asyncio

async def main():
    o = OllamaService()

    model="deepseek-r1:32b"
    # Example: Start the service
    # ollama.start_service()
    o.manual_start()  
    #ollama.view_logs() 
    o.load(model)
    o.check_loaded_models()
    x = await o.get_full_response("create* goal* AI video generator")
    print(x)
    o.unload(model)
    o.manual_stop()
if __name__ == "__main__":
    
    asyncio.run(main())

    # Example: Unload a specific model
    # ollama.unload_specific_model("example_model")
