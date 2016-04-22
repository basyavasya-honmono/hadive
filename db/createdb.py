import psycopg2 


try:
    conn = psycopg2.connect("dbname='dot_pub_cams'")
except:
    print "Unable to connect to the database"

cursor = conn.cursor() 

cameraTableSQL = '''CREATE TABLE CAMERA(
   id INT PRIMARY KEY NOT NULL,
   name VARCHAR(50) NOT NULL,
   description VARCHAR(200),
   lat REAL NOT NULL,
   lon REAL NOT NULL,
   position INT
);'''

imageTableSQL = '''CREATE TABLE IMAGE(
   camera INT REFERENCES CAMERA(id),
   id INT PRIMARY KEY NOT NULL,
   name VARCHAR(40) NOT NULL,
   year INT NOT NULL,
   month INT NOT NULL,
   day INT NOT NULL,
   hour INT NOT NULL,
   minute INT,
   date_taken TIMESTAMP NOT NULL,
   image_path VARCHAR(250) NOT NULL
);'''

labelTableSQL =  '''CREATE TABLE LABEL(
	image INT REFERENCES IMAGE(id),
	count INT
);'''

r = cursor.execute(cameraTableSQL)
r = cursor.execute(imageTableSQL)
r = cursor.execute(labelTableSQL) 