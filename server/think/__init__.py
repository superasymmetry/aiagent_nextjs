# from groq import Groq
# import os
# import json
# from auto import AutomationAgent

# class thinkModel():
#     def __init__(self):
#         self.action_history = []
#         self.task = ""
#         basedir = os.path.dirname(os.path.abspath(__file__))
#         folder_path = os.path.join(basedir, 'config.json')
#         with open(folder_path, "rb") as config_file:
#             config = json.load(config_file)
#         self.api_key = config["api_key"]
#         # self.client = Groq(api_key=self.api_key)
#         self.llm = Groq(
#             api_key=self.api_key,
#             model="deepseek-r1-distill-llama-70b",
#             temperature=0.2
#         )
        
#         self.task_library = {
#             "click_at_xy": self.click,
#             "move_cursor": self.move_cursor,
#             "type": self.type,
#             "select": self.select,
#             "scroll": self.scroll,
#         }
#         agent = AutomationAgent()
#         agent.get_major_controls(agent.root_control)
#         ui_features = agent.getTree()
#         with open("prompt.md", "r", encoding="utf-8") as file:
#             self.prompt_template = file.read()
#         formatted_prompt = self.prompt_template.format(ui_features=ui_features)
    
#     def call(self):
#         prompt = self.prompt_template
#         response = self.llm.chat(prompt)
#         return response

import os
import sys
import re

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from server.auto import AutomationAgent
from langchain_groq import ChatGroq

class thinkModel():
    def __init__(self):
        self.action_history = []
        self.task = ""
        basedir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(basedir, 'config.json')
        os.environ["GROQ_API_KEY"] = "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"
        self.llm = ChatGroq(
            model="deepseek-r1-distill-llama-70b",
            temperature=0.01,
            api_key=os.environ["GROQ_API_KEY"]
        )
        self.agent = AutomationAgent()

    def call(self, query):
        self.agent.get_major_controls(self.agent.root_control)
        ui_features = self.agent.getTree()
        prompt = f"""You are an agent that navigates the laptop and executes tasks. The user's task is "{query}". Decompose the user's query into its most fundamental steps, which must be one of clicking, typing, holding down cursor, dragging the mouse, lifting cursor, scrolling, and simultaneously pressing keys at once. Think through step-by-step the entire process of executing the task.
The features of the UI are given as: {ui_features}

Please output the immediate next step ANF ONLY THE IMMEDIATE NEXT STEP NOTHING MORE to performing the user's query."""
        response = self.llm.invoke(prompt)
        clean_query = re.sub(r'<think>.*?</think>', '', response.content, flags=re.DOTALL).strip()
        return clean_query

if __name__=="__main__":
    think_model = thinkModel()
    print(think_model.call("What is the Leafs record?").content)
