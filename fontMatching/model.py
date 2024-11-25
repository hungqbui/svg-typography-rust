import google.generativeai as genai
import os
import dotenv
import PIL
import json

dotenv.load_dotenv()

genai.configure(api_key=os.getenv("GEM"))

model = genai.GenerativeModel("gemini-1.5-flash-latest", generation_config={"response_mime_type": "application/json", "temperature": 1.5})

def get_text_feature(image_path, texts):

    image = PIL.Image.open(image_path)

    prompt = f"""Analyze the image, describe the following texts: {texts}. 
    For each text, let the type 
    Text = {{
        color: string (require, in hex),
        fontSize: string, (require, in pixels)
        backgroundColor: string (require, in hex),
    }}
    
    Don't add the properties if the text does not have that property.

    Output a dictionary of the form:
    Dict<string, Text> = {{
        "text1": Text,
        "text2": Text,
        ...
    }}
    
    """

    response = model.generate_content([prompt, image])
    
    return json.loads(response.text)
