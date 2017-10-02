from PIL import Image
from numpy import sum
from cv2 import cvtColor, threshold, imread, COLOR_BGR2GRAY, THRESH_BINARY
from os import path

def get_time(im):
    symbols = {'9121219': 'N ', '22221': 'N ', '161633343331616':'N ', '433334': 'S ',
            '453445': 'S ', '33333': 'E ', '933333': 'E ', '161666666666':'E ',
            '933332': 'E ', '333242333': 'W ', '47332264': 'W ', '1124525421':'W ',
            '72227': '0', '72127': '0', '62227': '0', '72226': '0', '662266': '0', '119': '1',
            '118': '1', '111': '1', '43333': '2', '244454': '2', '244354': '2', '243454': '2',
            '32335': '3', '32236': '3', '32336': '3', '223367': '3', '223291': '4', '223191': '4',
            '222291': '4', '23321': '4', '53335': '5', '63335': '5', '633355': '5', '73335': '6',
            '73334': '6', '73235': '6', '73325': '6',  '564355': '6', '13432': '7', '13422': '7',
            '124432': '7', '63336': '8',  '673366': '8', '43337': '9', '553465': '9', '2322': '/', 
            '1111': '-', '2': ':', '44': ':', '3332333': 'A', '922223': 'P', '912223': 'P', 
            '922222229': 'M', '822222229':'M'}

    direction = 'NA'
    time_ = 'Time Absent'

    img = im[0: 20, 0: 300] # Select the rectangle with the text
    gray = cvtColor(img, COLOR_BGR2GRAY)
    ret, thresh = threshold(gray, 205, 255, THRESH_BINARY)
    transposed = thresh.transpose()

    characters = ""
    for i in range(0, len(transposed)):
        characters = characters + str(int(sum(transposed[i]) / 255))
    characters = filter(None, characters.split('0'))

    result = ""
    for char in characters:
        result = result + symbols.get(char, "")

    if len(characters) > 5:
        if result[0].isalpha() and result[2:4].isdigit() and result[10:12].isdigit(): # Check dir & time
            direction = result[0]
            time_ = result[2:12] + ' ' + result[12:]
        elif result[:2].isdigit() and result[8:10].isdigit(): # Check time only
            time_ = result[:10] + ' ' + result[12:]
        elif len(set(characters)) < 2: # Check if the color is all the same in top bar.
            time_ = 'Cam not in Service'
        else:
            time_ = 'No Info Ribbon'

    return direction, time_
