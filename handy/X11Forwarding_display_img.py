#Port Forwarding
#ssh -X -L 1111:compute:22 NETID@gw.cusp.nyu.edu
#Open new terminal window
#ssh -X -p 1111 NETID@localhost

#Type python 
#Copy following lines
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import psycopg2
#Reading Image
#Specify image path

conn = psycopg2.connect("dbname='dot_pub_cams'")
conn = connectdb()
cursor = conn.cursor()	
cursor.execute("SELECT * FROM IMAGES WHERE labeled=false limit 1;")

image = cursor.fetchall()
image = image[0]

img = mpimg.imread(image[-3] + image[2])
#Plotting
imgplt = plt.imshow(img)
#this will open the plot window on your local machine
plt.show()
