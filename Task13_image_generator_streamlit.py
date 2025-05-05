import streamlit as st
import replicate
import os
from dotenv import load_dotenv
import requests
from PIL import Image
from io import BytesIO

# API-avain 
from dotenv import load_dotenv

# Reload environment variables
load_dotenv()
replicate_token = os.getenv("REPLICATE_API_TOKEN")

if not replicate_token:
    st.error("Replicate API token is missing! Please set the REPLICATE_API_TOKEN environment variable.")
    st.stop()

# UI
st.title("Image Generator")

prompt = st.text_area("Prompt", placeholder="for example: a girl in the forrest")
neg_prompt = st.text_area("Negative prompt", placeholder="for example: recycle bin, trash, garbage")
aspect = st.selectbox("Aspect ratio", ["1:1", "16:9", "3:2", "9:16", "4:5"])



if st.button("Generate Image") and prompt and replicate_token:
    st.info("Generating image...")

    client = replicate.Client(api_token=replicate_token)
    
    try:
       output = client.run(
    "black-forest-labs/flux-schnell",
    input={
        "prompt": prompt,
        "negative_prompt": neg_prompt,
        "go_fast": True,
        "megapixels": "1",
        "num_outputs": 1,
        "aspect_ratio": aspect,
        "output_format": "png",
        "output_quality": 80,
        "num_inference_steps": 4
    }
)

 
       for index, image_url in enumerate(output):
                img_data = requests.get(image_url).content
                img = Image.open(BytesIO(img_data))
                st.image(img, caption="Generated Image", use_container_width=True)

                img_bytes = BytesIO()
                img.save(img_bytes, format='PNG')
                st.download_button("Download Image", data=img_bytes.getvalue(), file_name="generated.png", mime="image/png")

    except Exception as e:
        st.error(f"Image generation failed: {str(e)}")