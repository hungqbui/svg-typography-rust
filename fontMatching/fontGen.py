from PIL import Image, ImageDraw, ImageFont
import os

def create_text(text, dimension):
    res = []
    
    font_path = os.path.join(os.path.dirname(__file__), "fonts")

    for font in os.listdir(font_path):
        if not font.endswith(".ttf"):
            continue
        font = ImageFont.truetype(f"{font_path}/{font}", text["fontSize"])
        image = Image.new("RGBA", dimension, (255, 255, 255, 0))
        draw = ImageDraw.Draw(image)

        draw.text((text["x"], text["y"]), text["text"], font=font, fill=text["color"])
        res.append(image)

    return res
