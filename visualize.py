
from os import walk
import json
from ocr import interogate, add_rect 
import math
from bs4 import BeautifulSoup
from svgpathtools import svg2paths2

def loss(d,x, m, n):
    sum = 0
    for i in range(m):
        for j in range(n):
            sum += d[i][j] * x[i][j]

    return sum

def swap(x,i,j,k):
    temp = x[i][j]
    x[i][j] = x[i][k]
    x[i][k] = temp

def optimize(d, x, depth=100, overallMin=float("inf")):
    if depth <= 0:
        return overallMin

    m = len(d)
    n = len(d[0])
    
    for i in range(m):
        x[i][d[i].index(min(d[i]))] = 1
        
    return loss(d,x,m,n)

        

for _,_,files in walk("./svgs"):
    for file in files:
        json_dict = add_rect(file)
        ocr_dict = interogate(f"./pngs/{file}.png")

        if (not ocr_dict): continue

        with open(f"./id_svg/{file}_withID.svg") as f:
            soup = BeautifulSoup(f, "xml")
            root = soup.find("svg")
            _,_, attr = svg2paths2(f"./id_svg/{file}_withID.svg")

        dim = attr["viewBox"].split(" ")

        svg_width = float(dim[2].replace("px",""))
        svg_height = float(dim[3].replace("px",""))

        m,n = len(json_dict), len(ocr_dict)

        json_map = {i : key for key, i in zip(list(json_dict.keys()), range(m))}
        ocr_map = {i : key for key, i in zip(list(ocr_dict.keys()), range(n))}

        bounds_json = list(json_dict.values())
        bounds_ocr = list(ocr_dict.values())

        center_json = [((b[1] + b[0]) / 2, (b[2] + b[3]) / 2) for b in bounds_json]
        center_ocr = [((b[1] + b[0]) * svg_width / 2, (b[2] +  b[3]) * svg_height / 2) for b in bounds_ocr]

        d = [[ 0 for i in range(n) ] for j in range(m)]


        for i in range(m):
            x1,y1 = center_json[i][0], center_json[i][1]
            for j in range(n):
                x2,y2 = center_ocr[j][0], center_ocr[j][1]

                d[i][j] = math.sqrt((x2-x1) ** 2 + (y2-y1)**2)

        x = [ [0] * (n) for i in range(m) ]

        print(optimize(d,x, depth=5))

        group = [[] for i in range(n)]
        for i in range(m):
            group[x[i].index(1)].append(json_map[i])
        for i in range(n):
            print(f"{ocr_map[i]}: {group[i]}")

                