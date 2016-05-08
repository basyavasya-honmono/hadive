import image_list
import numpy as np
import cv2
from matplotlib import pyplot as plt

def get_time(image):
# Dictionary for the possible characters
# Still lacking a sample of W and e for the word West !!!
	symbols = {'922221': 'F', '333351': 'a', '52222': 'c', '8': 'i', '71116': 'n', '63339': 'g', '933333': 'E', '3333': 's', '192': 't',
				'72227': '0', '119': '1', '43333': '2', '32336': '3', '223291': '4', '63335': '5', '73335': '6', '13432': '7', '63336': '8',
				'43337': '9', '2322': '/', '2': ':', '3332333': 'A', '922223': 'P', '922222229': 'M', '433334': 'S', '52225': 'o', '61117': 'u',
				'91116': 'h', '1111': '-', '9121219': 'N', '711192': 'rt', '22222': 'F', '343347': 'a', '432222': 'c', '1221': 'i', '11': '',
				'811127': 'n', '8544474': 'g', '1': '', '33333': 'E', '333435': 's', '119222': 't', '1111': '-', '44': ':', '662266': '0', '111': '1',
				'244454': '2', '223367': '3', '23321': '4', '633355': '5', '564355': '6', '124432': '7', '673366': '8', '553465': '9'}

# Reading the image and selecting the rectangle with the text
	img = cv2.imread(image)
	img = img[1: 19, 0: 285]

# Converting to grayscale
	gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	
# Preserving the edges with bilateral filter, removing the noise
	bilateral = cv2.bilateralFilter(gray, 35, 5, 5)
	
# Thresholding for brightnesses over 200 so the numbers remain at maximum (255) and the background becomes 0.
	ret, thresh = cv2.threshold(bilateral, 200, 255, cv2.THRESH_BINARY)

# Transposing
	transposed = thresh.transpose()

# Going from the left to the right over the verticals adding number of white pixels	
	characters = ""
	for i in range(0, len(transposed)):
		characters = characters + str(sum(transposed[i]) / 255)

# Clustering the characters
	characters = characters.split('0')
	characters = filter(None, characters)

# Joining the characters from the image into a single string
	result = ""
	for char in characters:
		result = result + symbols[char]
	if len(result):
    return result
  return 'Empty'
