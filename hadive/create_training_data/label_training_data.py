import matplotlib
matplotlib.use('TkAgg')

import os
import sys
import sqlite3
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.patches import Rectangle
plt.rcParams['toolbar'] = 'None'

class Annotate(object):


    def __init__(self, img_name):
        self.img_name = img_name
        self.i = 0
        self.ax = plt.gca()
        self.color = "r"
        self.rect = Rectangle((0,0), 1, 1, fill=False, color=self.color)
        self.x0 = None
        self.y0 = None
        self.x1 = None
        self.y1 = None
        self.x = None
        self.y = None
        self.height = None
        self.width = None
        self.label = "pos"
        self.boxes = []
        self.ax.add_patch(self.rect)

        connect = self.ax.figure.canvas.mpl_connect
        connect("button_press_event", self.on_click)
        connect("key_press_event", self.on_key)
        connect("close_event", self.end)
        self.draw_cid = connect('draw_event', self.grab_background)


    def on_click(self, event):
        """Use two clicks to define the bbox."""
        if self.i%2 == 0:
            self.x0 = event.xdata
            self.y0 = event.ydata
        if self.i%2 != 0:
            self.x1 = event.xdata
            self.y1 = event.ydata
            self.draw_rect()
        self.i += 1


    def on_key(self, event):
        """Change label using up, del bbox with left, and next with right."""
        if event.key == "up":
            if self.label == "pos":
                self.label = "neg"
                self.color = "b"
            else:
                self.label = "pos"
                self.color = "r"
            print "Current label: {}".format(self.label)
            sys.stdout.flush()
        elif event.key == "left":
            self.delete_bbox()
        elif event.key == "right":
            self.next_image()


    def draw_rect(self):
        """Draw new bbox on canvas."""
        self.y = min(self.y0, self.y1)
        self.height = max(self.y0, self.y1) - self.y
        self.width = self.height * 3. / 4.
        self.x = ((self.x0 + self.x1) / 2.) - self.width / 2.
        self.boxes.append([self.label, int(self.x), int(self.x) + int(self.width), int(self.y), int(self.y) + int(self.height)])
        self.rect.set_width(self.width)
        self.rect.set_height(self.height)
        self.rect.set_xy((self.x, self.y))
        self.rect.set_color(self.color)
        self.ax.draw_artist(self.rect)
        self.ax.figure.canvas.blit(self.ax.figure.bbox)
        print self.boxes
        sys.stdout.flush()


    def delete_bbox(self):
        """Delete last bbox on canvas and redraw others."""
        self.blit()
        self.boxes = self.boxes[:-1]
        for label, xmin, xmax, ymin, ymax in self.boxes:
            if label == "pos":
                color = "r"
            else:
                color = "b"
            self.rect.set_width(xmax - xmin)
            self.rect.set_height(ymax - ymin)
            self.rect.set_xy((xmin, ymin))
            self.rect.set_color(color)
            self.ax.draw_artist(self.rect)
            self.ax.figure.canvas.blit(self.ax.bbox)


    def obj_creation(self):
        """Blank values after creating bbox"""
        self.rect = Rectangle((0,0), 1, 1, fill=False, color=self.color)
        self.x0 = None
        self.y0 = None
        self.x1 = None
        self.y1 = None
        self.x = None
        self.y = None
        self.height = None
        self.width = None
        self.ax.add_patch(self.rect)


    def grab_background(self, event=None):
        self.rect.set_visible(False)
        canvas = self.ax.figure.canvas
        canvas.mpl_disconnect(self.draw_cid)
        canvas.draw()
        self.draw_cid = canvas.mpl_connect('draw_event', self.grab_background)
        self.background = self.ax.figure.canvas.copy_from_bbox(self.ax.figure.bbox)
        self.rect.set_visible(True)


    def blit(self):
        self.obj_creation()
        self.ax.figure.canvas.restore_region(self.background)
        self.ax.draw_artist(self.rect)
        self.ax.figure.canvas.blit(self.ax.figure.bbox)


    def next_image(self):
        """Update db with labels and restart main()."""
        plt.close('all')

        img_name = self.img_name
        boxes = self.boxes
        data = map(lambda x: [img_name] + x, boxes)
        conn = sqlite3.connect("../../data/training/training.db")
        c = conn.cursor()

        if len(boxes) != 0:
            c.executemany("INSERT INTO labels VALUES(?, ?, ?, ?, ?, ?)", data)
            c.execute("UPDATE images SET labeled = 1 WHERE image = '{}'".format(img_name))
        else:
            c.execute("DELETE FROM images WHERE image = '{}'".format(img_name))
            os.remove(os.path.join("../../data/training/img", img_name))

        conn.commit()
        conn.close()

        main()

    def end(self):
        quit()


def main():
    """Connect to db, find unlabeled image, and begin annotation."""
    conn = sqlite3.connect("../../data/training/training.db")
    c = conn.cursor()

    try:
        img_info = c.execute("SELECT * FROM images WHERE labeled != 1 ORDER BY RANDOM() LIMIT 1").fetchall()
        img_name = img_info[0][0]
        img = mpimg.imread(os.path.join("../../data/training/img", img_name))
        x_, y_, z_ = img.shape
        fig, ax = plt.subplots(figsize=(1. * y_ / 60, 1. * x_ / 60))
        fig.canvas.set_window_title(img_name)
        fig.subplots_adjust(0, 0, 1, 1)
        ax.imshow(img)
        ax.axis("off")
        mng = plt.get_current_fig_manager()
        mng.window.resizable(False, False)
        a = Annotate(img_name)
        plt.show()

    except:
        print "There are no images to be labeled."

    conn.close()


if __name__ == '__main__':
    main()
