'''
Scraping for Camera List:

The scrapingCameraList.py is used to get the locations of camera, with the its corresponding IDs.
This is done to have ot on our record, so that we can switch between cameras, accessing their IDs and location.
The value/id of camera can be appended at the end of the followinf url, and we can scrape the images 
from single,multiple camera

http://dotsignals.org/google_popup.php?cid=<id>
'''


from bs4 import BeautifulSoup
import pandas as pd 
import numpy as np 
import urllib
import re

r = urllib.urlopen("http://dotsignals.org/multiview2.php").read()
soup = BeautifulSoup(r,"lxml")
'''
When "lxml" is not specified , BeautifulSoup will use "lxml" by default, but when run on another system, it might make
choose different parsers (eg. html5lib, Pythons html.parser,lxmls XML parser) and tree formed would be different
Hence speicfying it is better always

print soup.prettify()[0:1000] to see the tree structure of the DOM
'''

camera_ids = []
camera_location_names = []

get_span = soup.find_all("span",class_="OTopTitle")
camera_location_names = []
for loc in get_span:
	camera_location_names.append(loc.get_text())
	


get_tds = soup.find_all("td",id="repCam__ctl0_lbNum")
for tds in get_tds:

	child = tds.findChildren()#.get_text()
	if child!=[]:

		camera_ids.append(child[0].get('value'))
	else:
		camera_ids.append('Inactive')


boroughs_list = []

for i in ['','1','2','3','4']:
	
	get_table = soup.find("table",id="tableCam"+i)
	#print len(get_table.findChildren())
	rows = len(get_table.findAll('tr'))
	count = rows-2
	
	borough = [re.sub('\s+',' ',get_table.findAll('tr')[0].findAll('td')[0].get_text().strip())]
	
	
	boroughs_list += borough*count
	
	
#camera_dict = {'location':camera_location_names,'camera_id':camera_ids}

camera_location_names_ids = pd.DataFrame(columns = ['location','camera_id','borough'])
camera_location_names_ids['location'] = camera_location_names
camera_location_names_ids['camera_id'] = camera_ids
camera_location_names_ids['borough'] = boroughs_list
print camera_location_names_ids.head()	
camera_location_names_ids.to_csv('camera_location_names_ids.csv')	