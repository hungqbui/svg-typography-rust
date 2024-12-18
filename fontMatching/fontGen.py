from PIL import Image, ImageDraw, ImageFont
import os
import base64

def create_text(text, dimension):
    res = []
    
    font_path = os.path.join(os.path.dirname(__file__), "fonts")

    for fontName in os.listdir(font_path):
        
        if not fontName.endswith(".ttf"):
            continue
        
        cur_path = os.path.join(font_path, fontName)

        font_size = bsearch_size(text["text"], dimension[1], cur_path)

        font = ImageFont.truetype(cur_path, font_size)
        temp = Image.new("RGBA", (3000, 3000), text["backgroundColor"])
        draw = ImageDraw.Draw(temp)

        draw.text((0, 0), text["text"], font=font, fill=text["color"])
        text_bbox = draw.textbbox((0, 0), text["text"], font=font)

        text_image = temp.crop(text_bbox)
        res.append((text_image.resize(dimension), cur_path, font_size))

    return res

def crop_image(image_path, bounds):
    image = Image.open(image_path)
    cropped = image.crop((bounds[0], bounds[2], bounds[1], bounds[3]))

    return cropped

def bsearch_size(text, height, font_path):
    min_font_size = 1
    max_font_size = 300
    while min_font_size <= max_font_size:
        font_size = (min_font_size + max_font_size) // 2
        font = ImageFont.truetype(font_path, font_size)
        dummy_img = Image.new("RGB", (1, 1))
        draw = ImageDraw.Draw(dummy_img)
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_height = text_bbox[3] - text_bbox[1]
        if text_height == height:
            return font_size
        elif text_height < height:
            min_font_size = font_size + 1
        else:
            max_font_size = font_size - 1
    return max_font_size

def font_to_base64(font_path):
    with open(font_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")