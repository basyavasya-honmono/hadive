import os, sys
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.image as mpimg
import numpy as np
from matplotlib.widgets import Button


class Annotate(object):
    def __init__(self):
        self.i = 1 # conditional incrementor for two click rectangle drawing
        self.col = 'blue' # deafult color for true positive label
        self.ax = plt.gca()
        # Initialize the Reactangle patch object with properties 
        self.rect = Rectangle((0,0), 1, 1, alpha = 1,ls = 'solid',fill = False, clip_on = True,color = self.col)
        # Initialize two diagonally opposite co-ordinates of reactangle as None
        self.x0 = None
        self.y0 = None
        self.x1 = None
        self.y1 = None
        # The list that will store value of those two co-ordinates of 
        # all the patches for storing into the file later
        self.xy = []
        self.ax.add_patch(self.rect)
        # Initialize mpl connect object 
        connect = self.ax.figure.canvas.mpl_connect
        # Create objects that will handle user initiated events 
        # We are using three events 
        # First event is button press event (on left key click)- 
        # on which on_click function is called
        self.ax.figure.canvas.mpl_connect('button_press_event', self.on_click)
        # Second event to draw, in case a mistake in labelling is made, 
        # deleting the patch requires redrawing the original canvas
        self.draw_cid = connect('draw_event', self.grab_background)

        # Third event - key press event
        # To change color of the patches when you want to switch between 
        # true postive and false postive labels
        self.ax.figure.canvas.mpl_connect('key_press_event',self.colorChange)
 

    def objCreation(self):
        # The new reactangle object to use after blit function (clearing 
        # the canvas and removing rectangle objects)
        
        self.rect = Rectangle((0,0), 1, 1, alpha = 1,ls = 'solid',fill = False, clip_on = True)
        self.x0 = None
        self.y0 = None
        self.x1 = None
        self.y1 = None
        self.ax.add_patch(self.rect)  


    def deletePrevious(self):
        '''
        Deletes the latest patch that was drawn
        '''
        # Clear the screen by calling blit function
        self.blit()
        # Remove the last patch co-ordinates from the list
        self.xy = self.xy[:-1]

        # Redraw all the rects except the previous ones
        # same as in on_click method 
        # xy = [[x0,y0,x1,y1,color],[x0,y0,x1,y1,col],.. for each patch]
        for coords in self.xy:
            self.rect.set_width(coords[2] - coords[0])
            self.rect.set_height(coords[3] - coords[1])
            self.rect.set_xy((coords[0], coords[1]))
            self.rect.set_color(coords[4])
            self.ax.draw_artist(self.rect)
            self.ax.figure.canvas.blit(self.ax.bbox)

        
    def colorChange(self,event):
        '''
        To change color to take  false positves into consideration - the default is color blue for true postive
        '''
        
        print('press', event.key)
        sys.stdout.flush()
        if event.key == 'r':
            # When 'r' key is pressed, the color of the next patch will be red
            self.col = 'r'
           

        elif event.key == 'b':
            # When 'b' key is pressed, the color of the next patch will be blue
            self.col = 'b' 
            

        elif event.key == 'd':
            # When 'd' key is pressed, the latest patch drawn is deleted
            self.deletePrevious()

        elif event.key == 'c':
            # When 'c' key is pressed, all the patches are cleared, only orignal background is present
            self.blit()    
            self.xy = []
            # Flush out the list as we don't want to consider any patch co-ordinates
                
            


    def on_click(self, event):
        '''
        Using two diagonally opposite clicks to draw a reactangle 
        '''
       
       
        self.i = self.i + 1
        if self.i%2 == 0:
            # The first click to mark one point of the rectangle and save the coordinates 
            print 'click1'
            self.x0 = event.xdata
            self.y0 = event.ydata

        if self.i%2 == 1:    
            #on second click - the rectangle should show up
   
            print 'click2'
            self.x1 = event.xdata
            self.y1 = event.ydata

            
            self.xy.append([self.x0,self.y0,self.x1,self.y1,self.col])
            print self.xy
            #Set the width and height of the rectangle patch as these two alone can characterize the patch
            self.rect.set_width(self.x1 - self.x0)
            self.rect.set_height(self.y1 - self.y0)
            self.rect.set_xy((self.x0, self.y0))
            #Set the color of the reactangle - can be blue/red depending on postive/negative label respectively
            self.rect.set_color(self.col)
            self.ax.draw_artist(self.rect)
            # Blit is used to successively retain and display patches on the screen 
            # Else Successively drawing one patch will remove the last drawn patch 
            self.ax.figure.canvas.blit(self.ax.bbox)


    # The following three functions taken from 
    # http://stackoverflow.com/questions/29277080/efficient-matplotlib-redrawing

    def safe_draw(self):
        """Temporarily disconnect the draw_event callback to avoid recursion"""
        canvas = self.ax.figure.canvas
        canvas.mpl_disconnect(self.draw_cid)
        canvas.draw()
        self.draw_cid = canvas.mpl_connect('draw_event', self.grab_background)


    def grab_background(self, event=None):
        """
        When the figure is resized, hide the rect, draw everything,
        and update the background.
        """
        self.rect.set_visible(False)
        self.safe_draw()

        # With most backends (e.g. TkAgg), we could grab (and refresh, in
        # self.blit) self.ax.bbox instead of self.fig.bbox, but Qt4Agg, and
        # some others, requires us to update the _full_ canvas, instead.
        self.background = self.ax.figure.canvas.copy_from_bbox(self.ax.figure.bbox)
        self.rect.set_visible(True)
        self.blit()

    

    def blit(self):
        """
        Efficiently update the figure, without needing to redraw the
        "background" artists.
        """
        self.objCreation()
        self.ax.figure.canvas.restore_region(self.background)
        self.ax.draw_artist(self.rect)
        self.ax.figure.canvas.blit(self.ax.figure.bbox)


if __name__ == '__main__':


    img = mpimg.imread('433.jpg')
    # Create the canvas
    fig = plt.figure()
    ax = fig.add_subplot(111)
    print type(img)
    ax.imshow(img)
    a = Annotate()

    plt.show()

