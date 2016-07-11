from get_patches import get_patches
from PIL import Image
from matplotlib import pyplot as plt

# Acquiring all patches
patches = get_patches()
# Number of patches
print len(patches)
# Loading test image
img = Image.open("1.jpg")
# Extracting a sample patch 
crop = img.crop(patches[-1])
# Coordinates of the sample patch
print patches[-1]
# Drawing the sample patch
plt.imshow(crop)
plt.show()
