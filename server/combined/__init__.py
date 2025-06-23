import re
import os
import sys
import json
import pygetwindow as gw
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from auto import AutomationAgent
from think import thinkModel
from tool import toolModel
# from agents.vision import visionModel
from agentic import agenticModel
from extract import extractModel

class combinedModel():
    def __init__(self):
        os.environ["GROQ_API_KEY"] = "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"

        print("Initializing models...")
        # self.think_model = thinkModel()
        self.tool_model = toolModel()
        # self.vision_model = visionModel()
        self.vision_model = agenticModel()
        self.agent = AutomationAgent()
        self.extract_model = extractModel()
        if os.path.exists("ui_elements.json")==False or os.path.getsize("ui_elements.json") == 0:
            j = {"desktop": {}, "taskbar": {}}
            extract = extractModel()
            clickable_elements = extract.get_clickable_elements()
            for name, coords in clickable_elements.items():
                if(coords[1]>1776 and coords[1]<1920):  # check if it is in the taskbar position
                    j["taskbar"][name] = coords
                else:
                    j["desktop"][name] = coords
                # print(name, j["desktop"][name])
            active_window_elements = extract.get_active_window_elements()

            active_window = gw.getActiveWindow().title
            j[f"{active_window}"] = {}
            # active window elements
            for name, coords in active_window_elements.items():
                j[f"{active_window}"][name] = coords
                print(name, j[f"{active_window}"][name])

            with open("ui_elements.json", "w") as file:
                json.dump(j, file, indent=4)
        else:
            pass

    def call(self, query):
        chat_history = []
        last_command = None
        while(True):
            think_query = self.vision_model.call(query, self.agent.capture_screen(), chat_history)
            clean_query = re.sub(r'<think>.*?</think>', '', think_query, flags=re.DOTALL).strip()
            print("Thought action:", clean_query)
            tool_call = self.tool_model.call(clean_query).content
            print("Tool action:", tool_call)
            json_pattern = r'```json\s*(\{.*?\})\s*```'
            match = re.search(json_pattern, tool_call, re.DOTALL)
            if match:
                json_str = match.group(1)
                try:
                    command = json.loads(json_str)
                    print("Extracted JSON object:", command)
                except json.JSONDecodeError as e:
                    print("Error decoding JSON:", e)
            else:
                print("No JSON block found.")
            chat_history.append(command)

            if("completed" in command or "finish" in command or "done" in command or "completed" in command):
                return "Task completed"
            elif(command["action"] == "left_click"):
                self.agent.left_click(int(command["details"]["x"]), int(command["details"]["y"]))
            elif(command["action"] == "right_click"):
                self.agent.right_click(int(command["details"]["x"]), int(command["details"]["y"]))
            elif(command["action"] == "vertical_scroll"):
                self.agent.scroll(command["details"]["direction"])
            elif(command["action"] == "horizontal_scroll"):
                self.agent.horizontal_scroll(command["details"]["direction"])
            elif(command["action"] == "move_cursor"):
                self.agent.move_cursor(int(command["details"]["x"]), int(command["details"]["y"]))
            elif(command["action"] == "type_text"):
                self.agent.type(command["details"]["text"])
            elif(command["action"] == "press_hotkey"):
                self.agent.hotkey(command["details"]["key"])
            else:
                print("Invalid action")
                # route to debug model
            
if __name__ == "__main__":
    combined_model = combinedModel()
    print(combined_model.call("Search up the leafs record"))