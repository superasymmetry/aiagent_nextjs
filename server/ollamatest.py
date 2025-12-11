from openai import OpenAI
import base64

# Load your image as base64
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
)

image_path = r"C:\Users\2025130\Documents\aiagent_nextjs\server\screenshot.png"  # <-- your image
image_base64 = encode_image(image_path)

response = client.chat.completions.create(
    model="llava",
    messages=[
        {
            "role": "user",
            "content": "Describe this image."
        }
    ],
    extra_body={
        "images": [image_base64]
    }
)

print(response.choices[0].message.content)
