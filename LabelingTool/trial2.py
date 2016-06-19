import os, sys
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.image as mpimg
import numpy as np
from matplotlib.widgets import Button
import glob
from tempfile import TemporaryFile





if __name__ == '__main__':

    #for image_name in ('433.jpg','434.jpg'):
    #def main(image_name):
        # '''
        # Start label tool per image object


        # '''
    def on_click(event):
        connect = ax.figure.canvas.mpl_connect
        # Create objects that will handle user initiated events 
        # We are using three events 
        # First event is button press event (on left key click)- 
        # on which on_click function is called
        connect('button_press_event', on_click)
        x0 = event.xdata
        y0 = event.ydata
        rect = Rectangle((0,0), 1, 1, alpha = 1,ls = 'solid',fill = False, clip_on = True,color = 'blue')
        ax.add_patch(rect)
        rect.set_width(30)
        rect.set_height(40)
        rect.set_xy((x0, y0))
        rect.set_visible(True)
        ax.draw_artist(rect)

        print 'hi'
    
    i = 0

    img = mpimg.imread('433.jpg')
    imgname = '433.jpg'
    # Create the canvas
    fig = plt.figure()
    ax = fig.add_subplot(111)
    
    #connect('close_event', handle_close)
    
    
    # Second event to draw, in case a mistake in labelling is made, 
    # deleting the patch requires redrawing the original canvas
    #self.draw_cid = connect('draw_event', grab_background)
        
    # print type(img)
    ax.imshow(img)
    
    plt.show()