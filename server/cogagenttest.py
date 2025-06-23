# import requests
# from PIL import Image
# import io
# import base64

# def compress_image(image_path, max_size=(512, 512), quality=85):
#     """
#     Compress and resize the image to stay within the API limits.
#     """
#     image = Image.open(image_path).convert("RGB")
#     image.thumbnail(max_size)  # Resize keeping aspect ratio
#     buffer = io.BytesIO()
#     image.save(buffer, format="JPEG", quality=quality)  # Save with compression
#     buffer.seek(0)
#     img_base64 = base64.b64encode(buffer.read()).decode('utf-8')
#     return img_base64

# def query_cogagent(gradio_url, image_path, prompt):
#     """
#     Send an image and a prompt to CogAgent Gradio API and get the result.
#     """
#     img_base64 = compress_image(image_path)

#     # Prepare payload
#     payload = {
#         "data": [
#             img_base64,
#             prompt
#         ]
#     }

#     # API endpoint (predict function 0)
#     api_endpoint = f"{gradio_url}/api/predict/0"

#     # Send POST request
#     response = requests.post(api_endpoint, json=payload)

#     # Handle response
#     if response.status_code == 200:
#         result = response.json()
#         print("CogAgent output:", result["data"])
#         return result["data"]
#     else:
#         print(f"Error {response.status_code}: {response.text}")
#         return None

# # =========================
# # USAGE EXAMPLE
# # =========================

# # 1. Put the Gradio app URL here (must be publicly accessible)
# gradio_url = "https://huggingface.co/spaces/THUDM-HF-SPACE/CogAgent-Demo"  # Replace this with actual URL

# # 2. Set your image and your prompt
# image_path = "screenshot.png"  # Replace this with your image path
# prompt = "Describe this image."

# # 3. Query CogAgent
# query_cogagent(gradio_url, image_path, prompt)







# from gradio_client import Client

# client = Client("THUDM-HF-SPACE/CogAgent-Demo")

# result = client.predict(
#     "Describe this image",
#     img_path="screenshot.png",
#     # query_text="Describe this image",  # ⚡ (name it exactly!)

#     api_name="/predict"
# )

# print(result)





from gradio_client import Client

# Initialize the client with the DeepSeek Space URL
client = Client("deepseek-ai/deepseek-vl2-small")

# Provide the image path or image URL
img_path = "screenshot.jpg"  # Update with the correct image path

# Predict using the space API, passing the image as a dictionary
result = client.predict(
    inputs=[{"path": img_path}],  # Pass inputs in a list of dictionaries
    api_name="/predict"  # Use the /predict API endpoint
)

print(result)
