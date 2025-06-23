from openai import OpenAI
import pyautogui
import base64

class agenticModel():
    def __init__(self):
        self.client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key="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",
        )
        with open(r"C:\Users\2025130\Documents\aiagent_nextjs\server\agentic\prompt1.md", "r", encoding="utf-8") as file:
            self.prompt_template = file.read()

    def capture_screen(self):
        im1 = pyautogui.screenshot()
        im1.save(r"C:\Users\2025130\Documents\aiagent\screenshot.jpeg")
        # image_path = pathlib.Path("C:\\Users\\2025130\\Documents\\aiagent\\screenshot.png").as_uri()

        with open(r"C:\Users\2025130\Documents\aiagent\screenshot.jpeg", "rb") as f:
            img = base64.b64encode(f.read()).decode("utf-8")

        img = f"data:image/jpeg;base64,{img}"
        return img

    def call(self, query, img_base64, chat_history):
        completion = self.client.chat.completions.create(
        model="qwen/qwen2.5-vl-3b-instruct:free",
        messages=[
            {
            "role": "user",
            "content": [
                {
                "type": "text",
                "text": f'You are an agent that navigates the laptop and executes tasks. The user\'s task is "{query}". Decompose the user\'s query into its most fundamental steps, which must be one of left-clicking, right-clicking, typing, dragging the cursor, scrolling, or pressing hotkeys. You have to determine the current state in the task based on the provided action history {chat_history} and the screenshot given (keep in mind that the screenshot is a greater determinant of the current progress in the task than the chat history). When looking at the screenshot, check which page the screen is at at the current moment. If it is not at the state you intend it, do actions to get it to that state. Think through step-by-step the entire process of executing the task. The features of the UI are given in the image. Please output **one sentence** that states the immediate next step AND ONLY THE IMMEDIATE NEXT STEP NOTHING MORE to performing the user\'s query. Be very clear but concise in your description of the immediate next step so that there are no ambiguities. If you realize the task is already finished, output "Task completed".'
                # "text": prompt.format(query=query, chat_history=chat_history),
                },
                {
                "type": "image_url",
                "image_url": {
                    "url": img_base64
                }
                }
            ]
            }
        ]
        )
        return (completion.choices[0].message.content)

    def find_bounding_boxes(self, query, img_base64):
        formatted_prompt = self.prompt_template.format(query=query)
        
        completion = self.client.chat.completions.create(
        model="qwen/qwen2.5-vl-3b-instruct:free",
        messages=[
            {
            "role": "user",
            "content": [
                {
                "type": "text",
                "text": formatted_prompt
                },
                {
                "type": "image_url",
                "image_url": {
                    "url": img_base64
                }
                }
            ]
            }
        ]
        )
        return (completion.choices[0].message.content)

    
if __name__ == "__main__":
    agentic_model = agenticModel()
    screenshot_base64 = agentic_model.capture_screen()
    response = agentic_model.call("Open Google Chrome and search for the weather", screenshot_base64, [])
    response1 = agentic_model.find_bounding_boxes("Find the coordinates of google chrome", screenshot_base64)
    print(response, response1)