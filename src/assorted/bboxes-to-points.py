from __future__ import print_function
import os
import sys
import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from lxml import etree

def bboxes_to_points(xml_folder):
    xml_files = os.listdir(xml_folder)

    run = True
    img_points = {}

    for idx, ff in enumerate(xml_files):
        print("Parsing xml: {}/{}".format(idx, len(xml_files)), end="\r")

        tree = etree.parse(os.path.join(xml_folder, ff))
        filename = tree.find("filename").text
        bboxes = tree.findall("object")
        pos_points = []
        neg_points = []
        for obj in bboxes:
            if obj.find("name").text == "pos":
                xmin = float(obj.find("bndbox/xmin").text)
                xmax = float(obj.find("bndbox/xmax").text)
                ymin = float(obj.find("bndbox/ymin").text)
                ymax = float(obj.find("bndbox/ymax").text)
                pos_points.append(((xmin + xmax) / 2., (ymin + ymax) / 2.))
            if obj.find("name").text == "neg":
                xmin = float(obj.find("bndbox/xmin").text)
                xmax = float(obj.find("bndbox/xmax").text)
                ymin = float(obj.find("bndbox/ymin").text)
                ymax = float(obj.find("bndbox/ymax").text)
                neg_points.append(((xmin + xmax) / 2., (ymin + ymax) / 2.))

        img_points[filename] = {"pos_points": pos_points, "neg_points": neg_points}

    return img_points


def plot_im(img_folder, img_points):
    for img in img_points.keys():
        coords = img_points[img]
        xx, yy = zip(*coords)

        fig, [ax1, ax2] = plt.subplots(nrows=1, ncols=2, figsize=(14, 5))
        ax2.imshow(plt.imread(os.path.join(img_folder, img)), aspect="equal")
        ax2.scatter(xx, yy, c="cyan", s=80, alpha=0.5)
        plt.show(block=True)


def write_to_json(file_path, dd):
    if not os.path.isfile(file_path):
        with open(file_path, "w") as f:
            json.dump(dd, f)
    else:
        with open(file_path, "r") as f:
            data = json.load(f)
            for key in dd.keys():
                if key in data.keys():
                    data[key].update(dd[key])
                else:
                    data[key] = dd[key]
        os.system("rm {}".format(file_path))
        with open(file_path, "w") as f:
            json.dump(data, f)



# # -- Plot points on image.
# plot_im(".", bboxes_to_points("."))

# -- Get all points for each im.
dd = bboxes_to_points("./xml/")
