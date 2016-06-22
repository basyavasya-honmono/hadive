from numpy import sum
from cv2 import cvtColor, threshold, imread, COLOR_BGR2GRAY, THRESH_BINARY
from os import path

def name_parser(image):
	datetime_list = image.split('.')[0].split('-')	
	datetime_list.append(datetime_list[-1][3:])
	datetime_list[-2] = datetime_list[-2][0:2]
	datetime_list.append('NA')
	return datetime_list

def empty_check(characters, a1): 
	for c in characters:
                if len(c) > 10:
                        return 1

        if len(characters)<15:
                return 1

        a = 1.0*(a1) / (len(characters)+1)
        if a> 1.2:
                return 1
	return 0

def get_time(image):
# Dictionary for the possible characters filtering out words like Facing, extracting just the first letter of South, East, West, North
	symbols = {'9121219': 'N ', '33333': 'E ', '933333': 'E ', '333242333': 'W ', '433334': 'S ', '933332': '', '922222': '',
				'922221': '', '333351': '', '52222': '', '8': '', '71116': '', '63339': '',  '3333': '', '192': '', '182': '', '72227': '0', '72127': '0', '62227': '0',
				'72226': '0', '119': '1', '118': '1', '43333': '2', '32335': '3', '32236': '3', '32336': '3', '3432': '',
				'223291': '4', '223281': '4', '223191': '4', '222291': '4', '53335': '5', '63335': '5', '73335': '6', '73334': '6', '73235': '6', '73325': '6',
		   '22': '', '112': '', '121': '', '21': '',
				'13432': '7', '13422': '7', '63336': '8', '43337': '9', '2322': '/', '2': ':', '3332333': 'A', '922223': 'P', '912223': 'P', '922222229': 'M',
		   '52225': '', '822222229':'M',
				'61117': '', '51117': '', '91116': '', '81116': '', '1111': '-', '711192': '', '22222': '', '343347': '', '53334': '', '92222': '', '432222': '', 
				'1221': '', '11': '', '811127': '', '8544474': '', '7544474': '', '1': '',  '333435': '', '119222': '', '1111': '-', '44': ':', '662266': '0', '111': '1',
				'244454': '2', '244354': '2', '243454': '2', '223367': '3', '23321': '4', '633355': '5', '464355': '6', '564355': '6', '124432': '7', '673366': '8', '553465': '9'}

# Reading the image and selecting the rectangle with the text
	default_name = name_parser(path.basename(image))
	img = imread(image)
	if img == None:
		return default_name
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
	if empty_check(characters, a1):
		return default_name
	
# Joining the characters from the image into a single string
	result = ""
	
	for char in characters:
		result = result + symbols[char]

# Extracting the name of the camera
	name = default_name[-2]
		
	if len(result)>10:
		if result[0].isdigit():
			if result[-1] == 'M':
				if (result[-2] == 'A') or (result[-2] == 'P' and result[10:12] == '12'):
					year = result[6:10]
					month = result[0:2]
					day = result[3:5]
					hour = result[10:12]
					minute = result[13:15]
					second = result[16:18]
					direction = 'NA'
					
				else :
					year = result[6:10]
					month = result[0:2]
					day = result[3:5]
					hour = str((int(result[10:12])+12)%24)
					minute = result[13:15]
					second = result[16:18]
					direction = 'NA'
					

# Working with the AM/PM time format
		elif result[-1] == 'M':
# Extracting the date and time 
			if (result[-2] == 'A') or (result[-2] == 'P' and result[12:14] == '12'):
		 		year = result[8:12]
				month = result[2:4]
				day = result[5:7]
				hour = result[12:14]
				minute = result[15:17]
				second = result[18:20]
				direction = result[0]
				
		 	else :
				year = result[8:12]
				month = result[2:4]
				day = result[5:7]
				hour = str((int(result[12:14])+12)%24)
				minute = result[15:17]
				second = result[18:20]
				direction = result[0]
				

# Working with 24-hour time format
		else :
			year = result[2:6]
			month = result[7:9]
			day = result[10:12]
			hour = result[12:14]
			minute = result[15:17]
			second = result[18:20]
			direction = result[0]
			

		return [year, month, day, hour, minute, second, name, direction]
	return default_name
