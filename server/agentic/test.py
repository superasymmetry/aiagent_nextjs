from openai import OpenAI
import pyautogui
from io import BytesIO
import base64
import pathlib

class agentic():
    def __init__(self, api_key="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"):
        self.client = OpenAI(
            base_url="https://router.huggingface.co/hf-inference/v1",
            api_key=api_key,
        )
    
    def capture_screenshot(self):
        screenshot = pyautogui.screenshot()
        buffered = BytesIO()
        screenshot.save(buffered, format="JPEG")
        return base64.b64encode(buffered.getvalue()).decode("utf-8")

    def call(self, query, img_base64, action_history):
        image_path = pathlib.Path("C:\\Users\\2025130\\Documents\\aiagent\\screenshot.png").as_uri()
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                                f'You are an agent that navigates the laptop and executes tasks. '
                                f'The user\'s task is "{query}". Decompose the query into its most fundamental steps, '
                                f'considering the following chat history: {action_history} and the current UI state provided by the image. '
                                'Output only one sentence stating the immediate next step. '
                                'If the task is completed, output "Task completed".'
                            )
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_path
                            # "url": "https://cdn.britannica.com/61/93061-050-99147DCE/Statue-of-Liberty-Island-New-York-Bay.jpg"
                        }
                    }
                ]
            }
        ]

        stream = self.client.chat.completions.create(
            model="Qwen/Qwen2.5-VL-7B-Instruct", 
            messages=messages,
            max_tokens=500,
            stream=False
        )
        return stream