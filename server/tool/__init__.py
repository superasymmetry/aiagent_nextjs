import os
import sys
import re
import json
import pygetwindow as gw

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from server.auto import AutomationAgent
from server.extract import extractModel
from langchain_groq import ChatGroq

class toolModel():
    def __init__(self):
        self.action_history = []
        self.task = ""
        basedir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(basedir, 'config.json')
        # Here we set the Groq API key directly or load it from your config
        os.environ["GROQ_API_KEY"] = "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"
        self.llm = ChatGroq(
            model="deepseek-r1-distill-llama-70b",
            temperature=0.01,
            api_key=os.environ["GROQ_API_KEY"]
        )
        self.agent = AutomationAgent()
        self.extract_model = extractModel()
        with open(r"C:\Users\2025130\Documents\aiagent\agents\tool\prompt.md", "r", encoding="utf-8") as file:
            self.prompt_template = file.read()
        # self.agent.get_major_controls(self.agent.root_control)
        # self.ui_features = self.agent.getTree()

    def call(self, query):
        # Retrieve the UI features from the agent (i.e. from your RAG database)
        with open("ui_elements.json", "r") as f:
            j = json.load(f)
            active_window = gw.getActiveWindow().title
            if(active_window not in j):
                j[active_window] = self.extract_model.get_clickable_elements()
        
            ui_features = j[active_window]
            taskbar = j["taskbar"]
        
        with open("ui_elements.json", "w") as f:
            json.dump(j, f)
        
        # get taskbar elements


        formatted_prompt = self.prompt_template.format(ui_features=ui_features, taskbar=taskbar, query=query)
        
        # Invoke the Groq model with the formatted prompt
        response = self.llm.invoke(formatted_prompt, config={"max_tokens": 100})
        return response

# Example usage
# think_model = thinkModel()
# tool_query = think_model.call("Open Google Chrome and search for the weather").content
# clean_query = re.sub(r'<think>.*?</think>', '', tool_query, flags=re.DOTALL).strip()
# print("Cleaned query:", clean_query)
# tool_model = toolModel()
# tool_call = tool_model.call(clean_query).content
# print(tool_call)
# json_pattern = r'```json\s*(\{.*?\})\s*```'
# match = re.search(json_pattern, tool_call, re.DOTALL)
# if match:
#     json_str = match.group(1)
#     print("Raw JSON output:")
#     print(json_str)
#     try:
#         output = json.loads(json_str)
#         print("Extracted JSON object:", output)
#     except json.JSONDecodeError as e:
#         print("Error decoding JSON:", e)
# else:
#     print("No JSON block found.")