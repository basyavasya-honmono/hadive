
# coding: utf-8

import folium
import json
import vincent


# Add this line for using vincent in ipython notebook
try:
    vincent.core.initialize_notebook()
except:
    pass

location_list = [
    [40.728279, -74.002867],
    [40.717642, -74.007589],
    [40.734894, -73.991062],
    [40.719964, -73.978750],
    [40.826403, -73.950357],
    [40.841725, -73.939340],
    [40.813389, -73.956273],
    [40.787679, -73.975024],
    [40.770320, -73.991379],
    [40.770115, -73.957413],
    [40.752807, -73.979281],
    [40.742911, -73.992787],
    [40.739760, -74.002519],
    [40.717871, -73.985618],
    [40.716724, -73.989160],
    [40.717364, -73.991170],
    [40.717666, -74.007546],
    [40.728791, -74.007085],
]


# Need to be adjusted to match the names in image names
name_list = [
    '6 Av & W Houston St',
    'Worth St & E Broadway',
    'Union Sq & 14 St',
    'E Houston St & Ave D',
    'Broadway & 145 St',
    'Broadway & 169 St',
    'Amsterdam Ave & 125 St',
    'Amsterdam & 86 St',
    '11 Ave & 57 St',
    '2 Ave & 74 St',
    'Madison Ave & 42 St',
    '6 Ave & 23 St',
    '8 Ave & 14 St',
    'WBB-6 & Delancy-Clinton',
    'Grand St & Essex St',
    'Grand St & Allen St',
    'Worth St & W Broadway',
    'W Houston St & Hudson St',  
]



# function for adding markers
def add_marker(i):
    global map_1
    # NOTE! THIS IS FAKE DATA!!!
    fake_data = [3,0,1,0,0,0,12,14,8,28,5,9,14,23,12,15,37,23,14,18,22,20,12,6]
    bar = vincent.Bar(fake_data,width=400,height=200)
    bar.axis_titles(x=name_list[i], y='Number of pedestrians')
    bar.x_axis_properties(title_size=16)
    bar.to_json(name_list[i]+'.json')
    
    # marker
    folium.Marker(
    location_list[i],
    popup = folium.Popup(max_width=450).add_child(
            folium.Vega(json.load(open(name_list[i]+'.json')), \
                        width=450, height=250))
    ).add_to(map_1)


# use folium to create the html
global map_1
map_1 = folium.Map(location=[40.778279, -73.952867], zoom_start=11, tiles='CartoDB Positron')

for i in range(len(location_list)):
    add_marker(i)

map_1.create_map(path='mthood.html')





