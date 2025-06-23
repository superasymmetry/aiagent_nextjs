import os
import sys
import base64
import pyautogui
from io import BytesIO

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from openai import OpenAI

class visionModel():
    def __init__(self):
        self.action_history = []
        self.task = ""
        basedir = os.path.dirname(os.path.abspath(__file__))
        # os.environ["GROQ_API_KEY"] = "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"
        os.environ["DEEPSEEK_API_KEY"] = "sk-519a6304c7674c5985903d1bd91c7622"
        # self.llm = ChatGroq(
        #     model="llama-3.2-90b-vision-preview",
        #     temperature=0.01,
        #     api_key=os.environ["GROQ_API_KEY"]
        # )
        # self.client = Groq(api_key=os.environ["GROQ_API_KEY"])
        self.client = OpenAI(
            api_key=os.environ["DEEPSEEK_API_KEY"],
            base_url="https://api.deepseek.com"  # Deepseek's API endpoint
        )
        with open(r"C:\Users\2025130\Documents\aiagent_nextjs\server\vision\prompt1.md", "r", encoding="utf-8") as file:
            self.prompt_template = file.read()

    def capture_screenshot(self):
        screenshot = pyautogui.screenshot()
        buffered = BytesIO()
        screenshot.save(buffered, format="JPEG")
        return base64.b64encode(buffered.getvalue()).decode("utf-8")

    def call(self, query, img_base64, chat_history):
        chat_completion = self.client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": f'You are an agent that navigates the laptop and executes tasks. The user\'s task is "{query}". Decompose the user\'s query into its most fundamental steps, which must be one of left-clicking, right-clicking, typing, dragging the cursor, scrolling, or pressing hotkeys. You have to determine the current state in the task based on the provided action history {chat_history} and the screenshot given (keep in mind that the screenshot is a greater determinant of the current progress in the task than the chat history). When looking at the screenshot, check which page the screen is at at the current moment. If it is not at the state you intend it, do actions to get it to that state. Think through step-by-step the entire process of executing the task. The features of the UI are given in the image. Please output **one sentence** that states the immediate next step AND ONLY THE IMMEDIATE NEXT STEP NOTHING MORE to performing the user\'s query. If you realize the task is already finished, output "Task completed".'},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{img_base64}",
                            },
                        },
                    ],
                }
            ],
            model="llama-3.2-90b-vision-preview",
        )

        return (chat_completion.choices[0].message.content)
    
    def find_bounding_boxes(self, query, img_base64):
        formatted_prompt = self.prompt_template.format(query=query)
        
        chat_completion = self.client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": formatted_prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{img_base64}",
                            },
                        },
                    ],
                }
            ],
            model="llama-3.2-90b-vision-preview",
        )

        return (chat_completion.choices[0].message.content)

if __name__ == "__main__":
    vision_model = visionModel()
    screenshot_base64 = vision_model.capture_screenshot()
    response = vision_model.call("Search for the weather", screenshot_base64, [])
    response = vision_model.find_bounding_boxes("Search for the weather", screenshot_base64)
    print(response)

    
#         prompt = f"""You are an agent that navigates the laptop and executes tasks. The user's task is "{query}". Decompose the user's query into its most fundamental steps, which must be one of left-clicking, right-clicking, typing, dragging the cursor, and scrolling. Think through step-by-step the entire process of executing the task.
# The features of the UI are given in the image.

# Please output the immediate next step ANF ONLY THE IMMEDIATE NEXT STEP NOTHING MORE to performing the user's query."""
#         response = self.llm.invoke(prompt)
#         return response

# think_model = visionModel()
# print(think_model.call("Open Google Chrome and search for the weather").content)

# from huggingface_hub import InferenceClient

# client = InferenceClient(
# 	# provider="hf-inference",
# 	api_key="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"
# )

# messages = "\"Can you please let us know more details about your \""

# stream = client.chat.completions.create(
# 	model="Qwen/Qwen2.5-VL-7B-Instruct", 
# 	messages=messages, 
# 	max_tokens=500,
# 	stream=True
# )

# for chunk in stream:
#     print(chunk.choices[0].delta.content, end="")

# processor = AutoProcessor.from_pretrained("deepseek-ai/Janus-Pro-7B")

# # Prepare inputs. If you have both text and image inputs, include the text field as needed.
# inputs = processor(images=img, return_tensors="pt")

# # Pass inputs to the model
# outputs = model(**inputs)

# # Process outputs as needed (e.g., decode predictions)
# print(outputs)

# import base64
# from openai import OpenAI

# # Initialize the Deepseek client using the OpenAI wrapper
# client = OpenAI(
#     api_key="sk-519a6304c7674c5985903d1bd91c7622", 
#     base_url="https://api.deepseek.com"
# )

# # Load and encode the image (adjust the file path and MIME type as needed)
# with open("screenshot.png", "rb") as image_file:
#     encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
# # Construct a data URL (assuming JPEG, change if needed)
# image_data = f"data:image/jpeg;base64,{encoded_image}"

# response = client.chat.completions.create(
#     model="deepseek-chat",
#     messages=[
#         {
#             "role": "system", 
#             "content": "You are an assistant."
#         },
#         {
#             "role": "user", 
#             "content": "What is in this image?", 
#             "image": image_data
#         }
#     ]
# )
