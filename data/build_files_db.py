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
def insert_db(camera_name, image_name, time_fields, new_path):
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
    
    camera_id, = camera[0]

    [year, month, day, hour, minute, second, name, direction]
    year = time_fields[0]
    month = time_fields[1]
    day = time_fields[2]
    hour = time_fields[3]
    minute = time_fields[4]
    second = time_fields[5]

    
    direction = "-" 
    if len(time_fields) == 8:
        direction =   time_fields[7] 
    
    # INSERTING IMAGE TO IMAGES TABLE
    cursor.execute("""INSERT INTO IMAGES(camera, name, year, 
                      month, day, hour, minute, second, 
                      date_taken, image_path, direction) 
                      VALUES (%s,'%s',%s,%s,%s,%s,%s, %s,
                              to_timestamp('%s', 'yyyy-mm-dd-hh24-mi-ss'),'%s','%s')""" % \
                    (camera_id, image_name, year, month, day, hour, minute, second, image_name_split[0], path, direction ))

    conn.commit()
    cursor.close()
    conn.close()

# GETTING PATH FROM NAME
def get_path(time_fields):
    path = '/'.join(time_fields)
    return path + '/'

# RENAMING AND MOVING
def rename_and_move(root, file):
    image_name = os.path.join(root, file)
    
    #Extracting time fields from an image
    time_fields = get_time(image_name)
    
    #Checking if time fields were present in the image
    if isinstance(time_fields, basestring):
        image_name_split = image_name.split('_')
        time_fields = image_name_split[0].split('-')

    camera_name = root[root.rfind('/')+1:]

    new_path = root + '/' + get_path(time_fields)

    #INSERTING TO DB
    insert_db(camera_name, image_name, time_fields, new_path)

    #Moving to new directory structure
    if not os.path.exists(new_path):
        os.makedirs(new_path)
    shutil.move(image_name, new_path + image_name)

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
