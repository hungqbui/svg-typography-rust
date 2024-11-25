
from os import walk
import json
from ocr import interogate, add_rect 
import math
from bs4 import BeautifulSoup
from svgpathtools import svg2paths2


# Approach 1: Find min distance from center of path to center of OCR box
# Constraints:
#   - For all i in object list sum(x[i]) == 1
#   - For all j in OCR list sum of x's column j >= 1
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

def optimize1(d, x, depth=100, overallMin=float("inf")):
    if depth <= 0:
        return overallMin

    m = len(d)
    n = len(d[0])
    
    # Toggle the j that makes d_ij min for each i
    for i in range(m):
        x[i][d[i].index(min(d[i]))] = 1
        
    return loss(d,x,m,n)

# Approach 2: 
# Assumption:
#   - Each path object is either a character or non-text object
#   - OCR gives an overestimation of the word -> center of path object is in the box or close to the the boundary of the box
#   - There cannot be overlapping OCR boxes at each path center (a letter cannot be part of two words unless OCR perform poorly)
# => For each path object i, match i to the OCR box that contains or is close to the center of i


# Case 1: Center of path in bound => x_ij = 1 (x in [ bound_left, bound_right ] AND y in [ bound_top, bound_bottom ])
# Case 2: Center of path not in any bound => x_ij = 1 when D_ij min (D_ij is the min distance to a point in the OCR box)
#   - Subcase 1: Center is closer to vertex (center_x NOT in [bound_left, bound_right] AND center_y NOT in [bound_top, bound_bottom]) => D_ij = distance to closest vertex
#   - Subcase 2: Center is closer to edge (x in [ bound_left, bound_right ] OR y in [ bound_top, bound_bottom ])  => D_ij = distance to closest edge

def optimize2(ocr_bounds, path_center, assign): 
    m,n = len(path_center), len(ocr_bounds)
    for i in range(m):
        # min_distance_index = 0
        # min_distance = float("inf")
        # flag = False
        for j in range(n):
            x,y = path_center[i]
            left,right,top,bottom = ocr_bounds[j]

            if left <= x <= right and top <= y <= bottom:
                assign[i][j] = 1
                flag=True
                break
            # elif left <= x <= right:
            #     curMin = min( abs(y-top), abs(y-bottom) )
            # elif top <= y <= bottom:
            #     curMin = min( abs(x- left), abs(x-right) )
            # else:
            #     minx = min(right, max(left, x))
            #     miny = min(bottom, max(top, y))
            #     curMin = math.sqrt((x-minx)**2 + (y-miny)**2)
        #     if curMin < min_distance:
        #         min_distance = curMin
        #         min_distance_index = j
        # if not flag:
        #     assign[i][min_distance_index] = 1          


        

                