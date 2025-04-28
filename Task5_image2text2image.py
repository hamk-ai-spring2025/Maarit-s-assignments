import base64
import requests
import os
import sys
import openai  # Import the openai library

# OpenAI API Key
# api_key = "YOUR_OPENAI_API_KEY"  # unsafe way
api_key = os.getenv("OPENAI_API_KEY")  # set your OPENAI_API_KEY in an environment variable

# Ask the user for a path on the filesystem:
path = input("Enter a local filepath to an image: ")

# Function to encode the image
def encode_image(path):
    with open(path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# Path to your image
#image_path = "dall_0.png"
#image_path = "drawing1.png"



# Read the image and encode it to base64:
base64_image = ""
try:
    image = open(path.replace("'", ""), "rb").read()
    base64_image = base64.b64encode(image).decode("utf-8")
except:
    print("Couldn't read the image. Make sure the path is correct and the file exists.")
    sys.exit()

# Getting the base64 string
base64_image = encode_image(path)

headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}

payload = {
    "model": "gpt-4o-mini",
    "messages": [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "What’s in this image?"},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                },
            ],
        }
    ],
    "max_tokens": 300,
}

response = requests.post(
    "https://api.openai.com/v1/chat/completions", headers=headers, json=payload
)

#print(response.json())
description = response.json().get("choices")[0].get("message").get("content")
print(f"Description: {description}")

# Validate the description
if not description.strip():
    print("Error: The description is empty. Cannot generate an image.")
    sys.exit()

# Now use this description to generate an image using text-to-image model
# Generate an image using DALL-E
try:
    dalle_response = openai.Image.create(
        prompt=description,
        model="dall-e",  # Specify the DALL-E model
        n=1,  # Number of images to generate
        size="1024x1024"  # Set the desired image size
    )
    # Output the generated image URL or save the image locally
    image_url = dalle_response['data'][0]['url']
    print(f"Generated image based on the description: {image_url}")
except Exception as e:
    print(f"Error generating image: {e}")