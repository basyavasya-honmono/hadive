import psycopg2 


try:
    conn = psycopg2.connect("dbname='dot_pub_cams'")
except:
    print "Unable to connect to the database"

cursor = conn.cursor() 

cameraTableSQL = '''CREATE TABLE CAMERAS(
   id SERIAL PRIMARY KEY NOT NULL,
   name VARCHAR(50) NOT NULL,
   description VARCHAR(200),
   lat REAL NOT NULL,
   lon REAL NOT NULL
);'''

imageTableSQL = '''CREATE TABLE IMAGES(
	camera INT REFERENCES CAMERAS(id),
	id SERIAL PRIMARY KEY NOT NULL,
	name VARCHAR(200) NOT NULL,
	year INT NOT NULL,
	month INT NOT NULL,
	day INT NOT NULL,
	hour INT NOT NULL,
	minute INT NOT NULL,
	second INT,
	date_taken TIMESTAMP NOT NULL,
	image_path VARCHAR(500) NOT NULL,
	direction VARCHAR(5),
	labeled boolean DEFAULT FALSE
);'''

labelTableSQL =  '''CREATE TABLE LABELS(
	id SERIAL PRIMARY KEY NOT NULL,
	image INT REFERENCES IMAGES(id),
	topx INT,
	topy INT,
	botx INT,
	boty INT,
	label INT,
	patch_path VARCHAR(500)
);'''

r = cursor.execute(cameraTableSQL)
r = cursor.execute(imageTableSQL)
r = cursor.execute(labelTableSQL) 
