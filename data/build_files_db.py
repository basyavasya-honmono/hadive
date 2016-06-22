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

    year = time_fields[0]
    month = time_fields[1]
    day = time_fields[2]
    hour = time_fields[3]
    minute = time_fields[4]
    second = time_fields[5]
    
    date_taken = year + '-' \
	       + month + '-' \
               + day + '-' \
               + hour + '-'  \
               + minute + '-'  \
               + second 
    
    direction = "-" 
    if len(time_fields) == 8:
        direction =   time_fields[7] 
    
    # INSERTING IMAGE TO IMAGES TABLE
    cursor.execute("""INSERT INTO tempimage(camera, name, year, 
                      month, day, hour, minute, second, 
                      date_taken, image_path, direction) 
                      VALUES (%s,'%s',%s,%s,%s,%s,%s, %s,
                              to_timestamp('%s', 'yyyy-mm-dd-hh24-mi-ss'),'%s','%s')""" % \
                    (camera_id, image_name, year, month, day, hour, minute, second, date_taken, new_path, direction ))

    conn.commit()
    cursor.close()
    conn.close()

# GETTING PATH FROM NAME
def get_path(time_fields):
    path = '/'.join(time_fields[:5])
    return path + '/'

# RENAMING AND MOVING
def rename_and_move(root, image_name, outpath):
    image_full_path = os.path.join(root, image_name)
    
    #Extracting time fields from an image
    time_fields = get_time(image_full_path)

    camera_name = image_name[ image_name.find('_')+1 : image_name.find('.jpg') ]
    
    #Checking if time fields were present in the image
    if isinstance(time_fields, basestring):
        image_name_split = image_name.split('_')
        time_fields = image_name_split[0].split('-')

    new_path = outpath + camera_name + '/' + get_path(time_fields)
    print new_path
    
    #INSERTING TO DB
    insert_db(camera_name, image_name, time_fields, new_path)

    #Moving to new directory structure
    if not os.path.exists(new_path):
        os.makedirs(new_path)
        os.chmod(new_path, 0777)
    
    print("old path %s"%(image_full_path))
    print("new path %s"%(new_path + image_name))
    shutil.copyfile(image_full_path, new_path + image_name)
    os.chmod(new_path + image_name, 0777)

# RENAMING AND INSERTING TO DB
def rename_and_dbinsert(path_file):
    inpath = ''
    outpath = ''
    with open(path_file) as f:
        inpath = f.readline().strip()
        outpath = f.readline().strip()
    print inpath
    print outpath
    if inpath!='':
        for root, dirs, files in os.walk(inpath):
            #Skipping already processed directories
            for d in dirs:
                if "2016" in d or len(d)<3:
                    dirs.remove(d)
            print "started moving"
            for file in files:
                if file.endswith('.jpg'):
                    rename_and_move(root, file, outpath)
                    
    else:
        raise AssertionError('Path file is empty!')


if __name__ == "__main__":
    if len(sys.argv) < 1:
        print('Please provide the txt file containing path')
        sys.exit(0)
    rename_and_dbinsert(sys.argv[1])    
