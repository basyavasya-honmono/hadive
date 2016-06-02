import os
import sys
import shutil
import psycopg2
import datetime 
from get_time import get_time

# CONNECTING TO DB
def connectdb():
    try:
        conn = psycopg2.connect("dbname='dot_pub_cams'")
        return conn
    except:
        print "Unable to connect to the database"

# INSERTING TO DB
def insert_db(camera_name, image_name, path):
    conn = connectdb()
    cursor = conn.cursor()
    
    #check if camera exists in camera table
    cursor.execute("SELECT id FROM CAMERAS WHERE name='%s'" % camera_name)
    camera = cursor.fetchall()
    if len(camera) == 0:
        #IF CAMERA DOESN'T EXISTS, INSERT IT
        cursor.execute("INSERT INTO CAMERAS(name) values ('%s')" % (camera_name));
        cursor.execute("SELECT id FROM CAMERAS WHERE name='%s'" % camera_name)
        camera = cursor.fetchall()
    camera, = camera[0]
    
    # SPLITING IMAGE NAME TO FIELDS
    image_name_split = image_name.split('_')
    time = image_name_split[0].split('-')
    year = time[0]
    month = time[1]
    day = time[2]
    hour = time[3]
    minute = time[4]
    second = time[5]
    direction =  image_name_split[2][0]
    
    # INSERTING IMAGE TO IMAGES TABLE
    cursor.execute("INSERT INTO IMAGES(camera, name, year, month, day, hour, minute, second, date_taken, image_path, direction) VALUES (%s,'%s',%s,%s,%s,%s,%s, %s,to_timestamp('%s', 'yyyy-mm-dd-hh24-mi-ss'),'%s','%s')" %
                        (camera, image_name, year, month, day, hour, minute, second, image_name_split[0], path, direction ))

    conn.commit()
    cursor.close()
    conn.close()

# GETTING PATH FROM NAME
def get_path(new_name):
    time = new_name.split('_')[0]
    path = '/'.join(time.split('-')[:-1])
    return path + '/'

# RENAMING AND MOVING
def rename_and_move(root, file):
    old_file = os.path.join(root, file)
    new_name = get_time(old_file) + '.jpg'
    new_name = new_name.replace('Mark','')
    new_path = root + '/' + get_path(new_name)
    
    camera_name = root[root.rfind('/')+1:]
    #INSERTING TO DB
    insert_db(camera_name, new_name, new_path)

    if not os.path.exists(new_path):
        os.makedirs(new_path)
    shutil.move(old_file, new_path + new_name)

# RENAMING AND INSERTING TO DB
def rename_and_dbinsert(path_file):
    path = ''
    with open(path_file) as f:
        path = f.readlines()[0].rstrip()
    print path
    if path!='':
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith('.jpg'):
                    rename_and_move(root, file)
                    
    else:
        raise AssertionError('Path file is empty!')


if __name__ == "__main__":
    if len(sys.argv) < 1:
        print('Please provide the txt file containing path')
        sys.exit(0)
    rename_and_dbinsert(sys.argv[1])    
