from numpy import sum
from cv2 import cvtColor, threshold, imread, COLOR_BGR2GRAY, THRESH_BINARY
from os import path

def get_time(image):
# Dictionary for the possible characters filtering out words like Facing, extracting just the first letter of South, East, West, North
	symbols = {'9121219': 'N ', '33333': 'E ', '933333': 'E ', '333242333': 'W ', '433334': 'S ',
				'922221': '', '333351': '', '52222': '', '8': '', '71116': '', '63339': '',  '3333': '', '192': '', '182': '', '72227': '0', '72127': '0', '62227': '0',
				'72226': '0', '119': '1', '118': '1', '43333': '2', '32335': '3', '32236': '3', '32336': '3',
				'223291': '4', '222291': '4', '53335': '5', '63335': '5', '73335': '6', '73334': '6', '22': '', '112': '', '121': '', '21': '',
				'13432': '7',	'63336': '8', '43337': '9', '2322': '/', '2': ':', '3332333': 'A', '922223': 'P', '912223': 'P', '922222229': 'M',  '52225': '', 
				'61117': '', '51117': '', '91116': '', '81116': '', '1111': '-', '711192': '', '22222': '', '343347': '', '53334': '', '92222': '', '432222': '', 
				'1221': '', '11': '', '811127': '', '8544474': '', '7544474': '', '1': '',  '333435': '', '119222': '', '1111': '-', '44': ':', '662266': '0', '111': '1',
				'244454': '2', '244354': '2', '243454': '2', '223367': '3', '23321': '4', '633355': '5', '564355': '6', '124432': '7', '673366': '8', '553465': '9'}

# Reading the image and selecting the rectangle with the text
	path_ = path.basename(image)
	img = imread(image)
	if img == None:
		return path_
	img = img[0: 20, 0: 285]

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
	

# Checking if the pixel counts are false positive (no datetime on actual image)
	for c in characters:
		if len(c) > 10:
			return path_
	
	if len(characters)<15:
		return path_
	
	a = 1.0*(a1) / (len(characters)+1)
	if a> 1.2:
		return path_
	
# Joining the characters from the image into a single string
	result = ""
	
	for char in characters:
		result = result + symbols[char]

# Extracting the name of the camera
	name = ''.join(path_.split('_')[1:]).split('.')[0]
	
	if len(result)>10:
		if result[0].isdigit():
			if result[-1] == 'M':
				if (result[-2] == 'A') or (result[-2] == 'P' and result[10:12] == '12'):
					result = result[6:10]+'-'+result[0:2]+'-'+result[3:5]+'-'+result[10:12]+'-'+result[13:15]+'-'+result[16:18]+'_'+name
				else :
					result = result[6:10]+'-'+result[0:2]+'-'+result[3:5]+'-'+str((int(result[10:12])+12)%24)+'-'+result[13:15]+'-'+result[16:18]+'_'+name

# Working with the AM/PM time format
		elif result[-1] == 'M':
# Extracting the date and time 
			if (result[-2] == 'A') or (result[-2] == 'P' and result[12:14] == '12'):
		 		result = result[8:12]+'-'+result[2:4]+'-'+result[5:7]+'-'+result[12:14]+'-'+result[15:17]+'-'+result[18:20]+'_'+name+'_'+result[0]
		 	else :
		 		result = result[8:12]+'-'+result[2:4]+'-'+result[5:7]+'-'+str((int(result[12:14])+12)%24)+'-'+result[15:17]+'-'+result[18:20]+'_'+name+'_'+result[0]

# Working with 24-hour time format
		else :
			result = result[2:6]+'-'+result[7:9]+'-'+result[10:12]+'-'+result[12:14]+'-'+result[15:17]+'-'+result[18:20]+'_'+name+'_'+result[0]

# Checking if the difference in time exceeds 10 seconds

		file_split = path_.split('-')
		file_time = int(file_split[5].split('_')[0])+int(file_split[4])*60+int(file_split[3])*3600
	       	image_time = int(result[17:19])+int(result[14:16])*60+int(result[11:13])*3600
		if abs(image_time-file_time)>10:
			result = "Mark"+result

		return result
	return path_
