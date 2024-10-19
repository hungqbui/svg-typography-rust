
from os import walk
import json
from ocr import interogate, add_rect 

for _,_,files in walk("./svgs"):
    for file in files:
        add_rect(file)
    for file in files:
        interogate(f"./pngs/{file}.png")