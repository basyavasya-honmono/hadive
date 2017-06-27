from numpy import sum
from cv2 import cvtColor, threshold, imread, COLOR_BGR2GRAY, THRESH_BINARY
from os import path

def get_time(image):
# Dictionary for the possible characters filtering out words like Facing, extracting just the first letter of South, East, West, North
	symbols = {'9121219': 'N ', '22221': 'N', '33333': 'E ', '933333': 'E ', '333242333': 'W ', '47332264': 'W', '433334': 'S ', '453445': 'S', \
				'161633343331616':'N', '1124525421':'W', '161666666666':'E',
			   '933332': 'E', '922222': '', '922221': '', '333351': '', '52222': '', '8': '', '71116': '', '63339': '',  '3333': '', '192': '', '182': '', \
			   '72227': '0', '72127': '0', '62227': '0',
				'72226': '0', '119': '1', '118': '1', '43333': '2', '32335': '3', '32236': '3', '32336': '3', '3432': '',
				'223291': '4', '223191': '4', '222291': '4', '53335': '5', '63335': '5', '73335': '6', '73334': '6', '73235': '6', '73325': '6',
		   '22': '', '112': '', '121': '', '21': '',
				'13432': '7', '13422': '7', '63336': '8', '43337': '9', '2322': '/', '2': ':', '3332333': 'A', '922223': 'P', '912223': 'P', '922222229': 'M',
		   '52225': '', '822222229':'M',
				'61117': '', '51117': '', '91116': '', '81116': '', '1111': '', '711192': '', '22222': '', '343347': '', '53334': '', '92222': '', '432222': '', 
				'1221': '', '11': '', '811127': '', '8544474': '', '7544474': '', '1': '',  '333435': '', '119222': '', '1111': '', '44': ':', '662266': '0', '111': '1',
				'244454': '2', '244354': '2', '243454': '2', '223367': '3', '23321': '4', '633355': '5', '564355': '6', '124432': '7', '673366': '8', '553465': '9'}

# Reading the image and selecting the rectangle with the text
	direction = 'NA'
	im = image
	# img = imread(image)
	check = im.reshape(im.shape[0] * im.shape[1], 3).mean(axis=1)
	black_im = 100 * check[check < 2].shape[0]/84480
	if black_im > 80:
		return 'black_im' 
	gray_im = 100 * check[check > 220].shape[0]/84480
	if gray_im > 63:
		return 'gray_im'
	if im[:,-32:].mean() < 2 and im[20:,:35].mean() > 250:
		return 'rainbow_im'

	img = im[0: 20, 0: 285]

# Converting to grayscale
	gray = cvtColor(img, COLOR_BGR2GRAY)
	
# Thresholding for brightnesses over 200 so the numbers remain at maximum (255) and the background becomes 0.
	ret, thresh = threshold(gray, 205, 255, THRESH_BINARY)

# Transposing
	transposed = thresh.transpose()
	
# Going from the left to the right over the verticals adding number of white pixels	
	characters = ""
	for i in range(0, len(transposed)):
		characters = characters + str(int(sum(transposed[i]) / 255))
		
# Clustering the characters
	a1 = characters.count('1')
	characters = characters.split('0')
	characters = filter(None, characters)
	
# Joining the characters from the image into a single string
	result = ""
	
	for char in characters:
		result = result + symbols.get(char, "")

# Extracting the name of the camera
		
	if len(result)>10:
		if result[0].isdigit():
			if result[-1] == 'M':
				if (result[-2] == 'A') or (result[-2] == 'P' and result[10:12] == '12'):
					direction = 'NA'
					
				else :
					direction = 'NA'
					

# Working with the AM/PM time format
		elif result[-1] == 'M':
# Extracting the date and time 
			if (result[-2] == 'A') or (result[-2] == 'P' and result[12:14] == '12'):
				direction = result[0]
				
		 	else :
				direction = result[0]
				

# Working with 24-hour time format
		else :
			direction = result[0]
			
		return direction
	return direction