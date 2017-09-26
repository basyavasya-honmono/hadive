import matplotlib
matplotlib.use('TkAgg')

import os
import json
import argparse
import matplotlib.pyplot as plt
from PIL import Image
plt.rcParams['toolbar'] = 'None'

def parse_args():
    """Parse input arguments."""
    parser = argparse.ArgumentParser(description='Label people.')
    parser.add_argument('--path', dest='path', help='Path to images.')
    args = parser.parse_args()
    return args

class LabelPoints:
    def __init__(self, path, im):
        self.path = path
        self.im = im
        self.img = Image.open(os.path.join(path, im))
        self.xs = []
        self.ys = []
        self.people = 0
        self.fig, self.ax = plt.subplots(1, 1, figsize=(1. * self.img.size[0] / 50, 1. * self.img.size[1] / 50))
        self.fig.canvas.set_window_title(self.im)
        self.fig.subplots_adjust(left=0,right=1,bottom=0,top=1)

        connect = self.fig.canvas.mpl_connect
        connect("button_press_event", self.on_click)
        connect("key_press_event", self.on_key)

        mng = plt.get_current_fig_manager()
        mng.window.resizable(False, False)
        self.ax.grid("off")
        self.ax.axis("off")
        self.ax.imshow(self.img, aspect="equal")
        plt.show(block=True)

    def on_click(self, event):
        if len(list(self.ax.get_lines())) > 0:
            self.ax.lines.pop(0)
        self.people += 1
        self.xs.append(event.xdata)
        self.ys.append(event.ydata)
        self.points = plt.plot(self.xs, self.ys, marker="o", ls="",
                               color="cyan", alpha=0.5)
        self.fig.canvas.draw()

    def on_key(self, event):
        """Change label using up, del bbox with left, and next with right."""
        if event.key == "right":
            self.write_output()

        elif event.key == "left":
            self.xs = self.xs[:-1]
            self.ys = self.ys[:-1]
            self.ax.lines.pop(0)
            self.points = plt.plot(self.xs, self.ys, marker="o", ls="",
                                   color="cyan", alpha=0.5)
            self.fig.canvas.draw()

        elif event.key == "q":
            quit()

    def write_output(self):
        print "{} people in {}".format(self.people, self.im)

        filename = "peds_{}.json".format(self.im.split("_")[0])
        new_data = {self.im: {"count": self.people, "locations": zip(self.xs, self.ys)}}

        if filename not in os.listdir("."):
            with open(filename, "w") as f:
                json.dump(new_data, f)
        else:
            with open(filename, "r") as f:
                data = json.load(f)
                data.update(new_data)
            os.system("rm {}".format(filename))
            with open(filename, "w") as f:
                json.dump(data, f)

        plt.close()

if __name__ == '__main__':
    args = parse_args()
    ims = os.listdir(os.path.join(args.path))
    filename = "peds_{}.json".format(ims[0].split("_")[0])

    if filename in os.listdir("."):
        with open(filename, "r+") as f:
            data = json.load(f)
            ims = set(ims) - set(data.keys())

    for im in ims:
        LabelPoints(args.path, im)
