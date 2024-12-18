import numpy as np
from functools import cmp_to_key
from PIL import Image
from skimage.feature import hog, match_template
from sklearn.metrics.pairwise import cosine_similarity
from skimage.metrics import structural_similarity as ssim
import numpy as np

def hog_similarity(a, b):
    # Convert images to grayscale
    a_gray = a.convert('L')
    b_gray = b.convert('L')
    
    # Resize images to the same size if necessary
    size = (128, 128)
    a_gray = a_gray.resize(size)
    b_gray = b_gray.resize(size)
    
    # Compute HOG features
    a_hog = hog(np.array(a_gray), pixels_per_cell=(16, 16), cells_per_block=(2, 2))
    b_hog = hog(np.array(b_gray), pixels_per_cell=(16, 16), cells_per_block=(2, 2))
    
    # Compute similarity using cosine similarity
    similarity = cosine_similarity([a_hog], [b_hog])[0][0]
    return similarity

def hog_scoring(original, generated):
    def comparator(a, b):
        lossa = hog_similarity(original, a[0])
        lossb = hog_similarity(original, b[0])

        return lossb - lossa

    return sorted(generated, key=cmp_to_key(comparator))

