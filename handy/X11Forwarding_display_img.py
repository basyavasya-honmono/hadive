#Port Forwarding
#ssh -X -L 1111:compute:22 NETID@gw.cusp.nyu.edu
#Open new terminal window
#ssh -X -p 1111 NETID@localhost

#Type python 
#Copy following lines
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
#Reading Image
#Specify image path
img = mpimg.imread('2016-04-30-18-40-06_Amsterdam_Ave__125_St.jpg')
#Plotting
imgplt = plt.imshow(img)
#this will open the plot window on your local machine
plt.show()
