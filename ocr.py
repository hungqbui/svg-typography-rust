import requests
import json
from io import BytesIO
import base64
from PIL import Image, ImageDraw
import dotenv
import os
from bs4 import BeautifulSoup
from svgpathtools import svg2paths2

dotenv.load_dotenv()

def add_rect(file, bounds = None, save_to = None, color = "red", labels = None):
    with open(f"./svgs/{file}") as f:
        soup = BeautifulSoup(f, "xml")
        root = soup.find("svg")
        _,_, attr = svg2paths2(f"./svgs/{file}")

    dim = attr["viewBox"].split(" ")

    svg_width = float(dim[2].replace("px",""))
    svg_height = float(dim[3].replace("px",""))

    # img_height= float(attr["height"].replace("px",""))
    # img_width= float(attr["width"].replace("px",""))

    if not bounds:
        data = json.load(open(f"./jsons/{file}.json"))
        bounds = list(set(map(lambda x: (x[0], x[2], x[1] - x[0], x[3] - x[2]), data["bounds"])))
    else:
        bounds = list(map(lambda x: (x[0]*svg_width, x[2]*svg_height, (x[1] - x[0])*svg_width, (x[3] - x[2])*svg_height), bounds))

    for index, (left, top, width, height) in enumerate(bounds):
        group = soup.new_tag("g")
        rect = soup.new_tag("rect", x=left, y=top, width=width, height=height, fill="none", stroke=color)
        group.append(rect)

        if labels:
            text = soup.new_tag("text", x=left+5, y=top+10, fill=color)
            text.attrs["font-size"] = "7px"
            text.insert(0, labels[index])
            group.append(text)


        root.append(group)

    with open(f"./visualized/{file}-bounded.svg" if not save_to else save_to, "w", encoding="utf-8") as f:
        f.write(str(soup))

def interogate(image_path):
    image = Image.open(image_path)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    image_base64 = base64.b64encode(buffer.getvalue())

    width, height = image.size

    payload = json.dumps({
        "requests": [
            {
            "features": [
                {
                "type": "DOCUMENT_TEXT_DETECTION"
                }
            ],
            "image": {
                "content": image_base64.decode("utf-8")
            }
            }
        ]
    })
    headers = {
        'Content-Type': 'application/json'
    }

    url = f"https://vision.googleapis.com/v1/images:annotate?key={os.getenv("OCR")}"

    response = requests.request("POST", url, headers=headers, data=payload)

    output = json.loads(response.text)

    if not output['responses'][0].get("textAnnotations", None):
        return

    print(width, height, image_path)


    bounds = []
    labels = []
    draw = ImageDraw.Draw(image)
    for text in output['responses'][0]["textAnnotations"]:
        cur = []
        draw.polygon(tuple(map(lambda x: (x.get("x", 0), x.get("y", 0)), text["boundingPoly"]["vertices"])), outline="red")
        for point in text["boundingPoly"]["vertices"]:
            x = point.get("x", 0)
            y = point.get("y", 0)
            if not cur:
                cur= [x, x,y, y]
            else:
                cur[0] = min(cur[0], x)
                cur[1] = max(cur[1], x)
                cur[2] = min(cur[2], y)
                cur[3] = max(cur[3], y)

        labels.append(text["description"])
        bounds.append((cur[0]/width, cur[1]/width, cur[2]/height, cur[3]/height))

    image.save(f"./outputpng/ocred-{image_path.split('/')[-1]}")

    svg = image_path.split("/")[-1].replace(".png", "")
    add_rect(image_path.split("/")[-1].replace(".png", ""), bounds, save_to=f"./output/ocred-{svg}.svg", labels=labels, color="blue")

interogate("./pngs/text cool.svg.png")
