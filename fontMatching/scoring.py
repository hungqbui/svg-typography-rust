import numpy as np
from functools import cmp_to_key
from PIL import Image
from skimage.feature import hog, match_template
from sklearn.metrics.pairwise import cosine_similarity
from skimage.metrics import structural_similarity as ssim
import numpy as np

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torchvision.transforms as transforms
from torchvision.models import vgg19, VGG19_Weights

def hog_similarity(a, b):
    a_gray = a.convert('L')
    b_gray = b.convert('L')
    
    size = (128, 128)
    a_gray = a_gray.resize(size)
    b_gray = b_gray.resize(size)
    
    a_hog = hog(np.array(a_gray), pixels_per_cell=(8, 8), cells_per_block=(2, 2))
    b_hog = hog(np.array(b_gray), pixels_per_cell=(8, 8), cells_per_block=(2, 2))
    
    # Compute similarity using cosine similarity
    similarity = cosine_similarity([a_hog], [b_hog])[0][0]
    return similarity

def style_similarity(a, b):
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    imsize = 128

    loader = transforms.Compose([transforms.Resize(imsize), transforms.ToTensor()])

    def image_loader(image):
        image = loader(image).unsqueeze(0)
        return image.to(device, torch.float)
    
    def get_style_features(image):
        # Load VGG19 model
        model = vgg19(pretrained=True).features.to(device).eval()
        model = nn.Sequential(*list(model.children())[:9])
        
        # Load image
        image = image_loader(image)
        image = image[:, :3, :, :]
        
        # Get features
        features = model(image)
        return features

    def gram_matrix(input):
        a, b, c, d = input.size()
        features = input.view(a * b, c * d)
        G = torch.mm(features, features.t())
        return G.div(a * b * c * d)

    a = get_style_features(a)
    b = get_style_features(b)

    a_gram = gram_matrix(a)
    b_gram = gram_matrix(b)

    similarity = cosine_similarity(a_gram.cpu().detach().numpy(), b_gram.cpu().detach().numpy())[0][0]
    return similarity

def hog_scoring(original, generated):
    def comparator(a, b):
        lossa = hog_similarity(original, a[0])
        lossb = hog_similarity(original, b[0])

        return lossb - lossa

    return sorted(generated, key=cmp_to_key(comparator))

def style_scoring(original, generated):
    def comparator(a, b):
        lossa = style_similarity(original, a[0])
        lossb = style_similarity(original, b[0])

        return lossb - lossa

    return sorted(generated, key=cmp_to_key(comparator))
