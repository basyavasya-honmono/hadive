import os, sys
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.image as mpimg
import numpy as np
from matplotlib.widgets import Button





class Annotate(object):
    def __init__(self):
        self.i = 1
        self.col = 'blue'
        self.ax = plt.gca()
        self.rect = Rectangle((0,0), 1, 1, alpha = 1,ls = 'solid',fill = False, clip_on = True,color = self.col)
        self.x0 = None
        self.y0 = None
        self.x1 = None
        self.y1 = None
        self.xy = []
        self.db = 0
        
        self.ax.add_patch(self.rect)
        connect = self.ax.figure.canvas.mpl_connect
        self.ax.figure.canvas.mpl_connect('button_press_event', self.on_click)
        self.draw_cid = connect('draw_event', self.grab_background)
        self.ax.figure.canvas.mpl_connect('key_press_event',self.colorChange)
        #self.ax.figure.canvas.mpl_connect('')
        #self.ax.figure.canvas.mpl_connect('button_release_event', self.on_release)


    def objCreation(self):
        #The new reactangle object after new events 
        
        self.rect = Rectangle((0,0), 1, 1, alpha = 1,ls = 'solid',fill = False, clip_on = True,color = self.col)
        self.x0 = None
        self.y0 = None
        self.x1 = None
        self.y1 = None
        self.ax.add_patch(self.rect)  


    def deletePrevious(self):
        #Clear the screen

        self.blit()
        self.xy = self.xy[:-1]
        #Make all the rects except the previous ones
        for coords in self.xy:
            self.rect.set_width(coords[2] - coords[0])
            self.rect.set_height(coords[3] - coords[1])
            self.rect.set_xy((coords[0], coords[1]))
            self.ax.draw_artist(self.rect)
            self.ax.figure.canvas.blit(self.ax.bbox)

        
    def colorChange(self,event):
        #Color changes to take  false positves into consideration - the default is color blue
        print('press', event.key)
        sys.stdout.flush()
        if event.key == 'r':
            self.col = 'r'
            self.objCreation()
            
            

        elif event.key == 'b':
            self.col = 'b' 
            self.objCreation()

        elif event.key == 'd':
            self.deletePrevious()

        elif event.key == 'c':
            self.blit()    
            self.xy = []
                
            


    def on_click(self, event):
       
       #Click event to draw rectangles - two clicks per rectangle 

  
        self.i = self.i + 1
        if self.i%2 == 0:

            

            print 'press'
            self.x0 = event.xdata
            self.y0 = event.ydata

        if self.i%2 == 1:    
            
   
            print 'release'
            self.x1 = event.xdata
            self.y1 = event.ydata

            
            self.xy.append([self.x0,self.y0,self.x1,self.y1])
            print self.xy
            self.rect.set_width(self.x1 - self.x0)
            self.rect.set_height(self.y1 - self.y0)
            self.rect.set_xy((self.x0, self.y0))
            self.ax.draw_artist(self.rect)
            self.ax.figure.canvas.blit(self.ax.bbox)


    # The following three functions taken from http://stackoverflow.com/questions/29277080/efficient-matplotlib-redrawing

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
    #Create the canvas
    fig = plt.figure()
    ax = fig.add_subplot(111)
    print type(img)
    ax.imshow(img)
    a = Annotate()

    plt.show()

