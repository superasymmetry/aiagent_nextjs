import os
import base64
import pyautogui
from io import BytesIO
import certifi
from openai import OpenAI  # OpenAI client works with OpenRouter when configured properly

# Ensure that the certificate bundle is up-to-date
os.environ["CURL_CA_BUNDLE"] = certifi.where()

# Set your OpenRouter API key (which gives you access to Deepseek via OpenRouter)
os.environ["OPENROUTER_API_KEY"] = "sk-519a6304c7674c5985903d1bd91c7622"

class VisionModelDeepseekOpenRouter:
    def __init__(self):
        # Initialize the OpenAI client to use OpenRouter's endpoint
        self.client = OpenAI(
            api_key=os.environ["OPENROUTER_API_KEY"],
            base_url="https://api.openrouter.ai"  # OpenRouter's endpoint
        )

    def capture_screenshot(self):
        """Capture a screenshot and return its base64-encoded JPEG representation."""
        screenshot = pyautogui.screenshot()
        buffered = BytesIO()
        screenshot.save(buffered, format="JPEG")
        return base64.b64encode(buffered.getvalue()).decode("utf-8")

    def call(self, query, img_base64, chat_history):
        """
        Call Deepseek via OpenRouter using both text and an image.
        Parameters:
            query (str): The user's query.
            img_base64 (str): Base64-encoded screenshot.
            chat_history (list): Chat history for context.
        Returns:
            str: The model's response.
        """
        response = self.client.chat.completions.create(
            model="deepseek-chat",  # Replace with the correct Deepseek model name if needed
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                f'You are an agent that navigates the laptop and executes tasks. '
                                f'The user\'s task is "{query}". '
                                f'Consider the following chat history: {chat_history} and the current UI state provided by the image. '
                                'Output only one sentence stating the immediate next step. '
                                'If the task is completed, output "Task completed".'
                            )
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{img_base64}"
                            }
                        }
                    ]
                }
            ]
        )
        return response.choices[0].message.content

# Example usage:
if __name__ == "__main__":
    vm = VisionModelDeepseekOpenRouter()
    screenshot_base64 = vm.capture_screenshot()
    output = vm.call("Open Google Chrome and search for the weather", screenshot_base64, [])
    print("Deepseek/OpenRouter response:", output)
