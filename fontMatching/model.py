import google.generativeai as genai
import os
import dotenv
import PIL
import json
from collections import Counter
import numpy as np

dotenv.load_dotenv()

genai.configure(api_key=os.getenv("GEM"))

model = genai.GenerativeModel("gemini-1.5-flash-latest", generation_config={"response_mime_type": "application/json", "temperature": 1.5})

def get_text_feature(image_path, texts):

    image = PIL.Image.open(image_path)

    prompt = f"""Analyze the image, describe the following texts: {texts}. 
    For EACH text, let the type
    Text = {{
        color: string (require, in hex),
        backgroundColor: string (require, in hex),
    }}
    
    Don't add the properties if the text does not have that property.

    MAKE SURE THAT HAVE EACH TEXT AS A SEPARATE OBJECT.

    Output a dictionary of the form:
    Dict<string, Text> = {{
        "text1": Text,
        "text2": Text,
        ...
    }}
    
    """

    response = model.generate_content([prompt, image])
    
    return json.loads(response.text)

def get_color(image):

    gray_image = image.convert('L')
    gray_array = np.array(gray_image)

    threshold = gray_array.mean()
    binary_mask = gray_array < threshold

    rgb_array = np.array(image)

    text_pixels = rgb_array[binary_mask]
    background_pixels = rgb_array[~binary_mask]

    text_color = tuple(np.mean(text_pixels, axis=0).astype(int))
    background_color = tuple(np.mean(background_pixels, axis=0).astype(int))
    
    return background_color, text_color

