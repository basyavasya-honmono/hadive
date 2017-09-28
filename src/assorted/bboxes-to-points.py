from __future__ import print_function
import os
import sys
import json
import random
import numpy as np
import seaborn as sns
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


def combine_json(files, filename):
    file1, file2 = files

    with open(os.path.join(file1)) as f:
        dd1 = json.load(f)
    with open(os.path.join(file2)) as f:
        dd2 = json.load(f)

    for key in dd1.keys():
        if key in dd2.keys():
            dd2[key].update(dd1[key])
        else:
            dd2[key] = dd1[key]

    with open("{}.json".format(filename), "w") as f:
        json.dump(dd2, f)


def point_in_box(point, box):
    xx, yy = [float(i) for i in point]
    x0, y0, x1, y1, _ = [float(i) for i in box]
    if xx >= x0 and xx <= x1 and yy >= y0 and yy <= y1:
        return True
    else:
        return False


def points_in_box(points, box):
    nn = []
    for pp in points:
        nn.append(point_in_box(pp, box))
    return nn


def box_w_points(box, points):
    nn = 0
    for point in points:
        if point_in_box(point, box):
            nn += 1
    return nn


def boxes_per_point(point, bboxes, return_bboxes=True):
    nn = []
    bb = []
    for bbox in bboxes:
        nn.append(point_in_box(point, bbox))
        bb.append(bbox)

    if return_bboxes:
        return nn, bb
    else:
        return nn


def prec_recall(json_path):
    with open(json_path, "r") as f:
        data = json.load(f)

    for im in data.keys():
        fp = tp = fn = tn = 0

        bboxes = list(data[im]["bboxes"])
        pos_pp = list(data[im]["pos_points"])
        neg_pp = list(data[im]["neg_points"])

        for pp in neg_pp:
            in_a_box = 0
            last_bb = []
            for bb in bboxes:
                if point_in_box(pp, bb):
                    in_a_box += 1
                    last_bb = [bb]
            if in_a_box == 0:
                tn += 1
            else:
                fp += 1
                bboxes.remove(last_bb[0])

        for pp in pos_pp:
            last_bb = []
            for bb in bboxes:
                if point_in_box(pp, bb):
                    last_bb = [bb]
            if last_bb:
                tp += 1
                bboxes.remove(last_bb[0])
            else:
                fn += 1

        for pp in neg_pp:
            for bb in bboxes:
                if point_in_box(pp, bb):
                    fp += 1

        print("False Positives: {}, True Positives: {}, False Negatives: {}, True Negatives: {}             ".format(fp, tp, fn, tn))
        sys.stdout.flush()

        data[im]["relevance"] = {"fp": fp, "tp": tp, "fn": fn, "tn": tn}

    with open("./output.json", "w") as f:
        json.dump(data, f)

def prec_recall_complete_labels(json_path):
    with open(json_path, "r") as f:
        data = json.load(f)

    for im in data.keys():
        fp = tp = fn = tn = 0

        bboxes = list(data[im]["bboxes"])
        pos_pp = list(data[im]["locations"])

        for pp in pos_pp:
            last_bb = []
            for bb in bboxes:
                if point_in_box(pp, bb):
                    last_bb = [bb]
            if last_bb:
                tp += 1
                bboxes.remove(last_bb[0])
            else:
                fn += 1

        fp = len(bboxes)

        print("False Positives: {}, True Positives: {}, False Negatives: {}, True Negatives: {}             ".format(fp, tp, fn, tn))
        sys.stdout.flush()

        data[im]["relevance"] = {"fp": fp, "tp": tp, "fn": fn, "tn": tn}

    with open(json_path, "w") as f:
        json.dump(data, f)


def bootstrapsummary(json_path, iters=100, sample_size=20):
    np.random.seed(1)
    with open(json_path, "r") as f:
        data = json.load(f)
    fp_tot = list()
    tn_tot = list()
    tp_tot = list()
    fn_tot = list()
    pos_tot = list()
    neg_tot = list()
    dets_tot = list()
    for _ in range(iters):
        fp_sum = tn_sum = tp_sum = fn_sum = pos = neg = dets = 0
        keys = random.sample(data.keys(), sample_size)
        for key in keys:
            fp_sum += data[key]["relevance"]["fp"]
            tn_sum += data[key]["relevance"]["tn"]
            tp_sum += data[key]["relevance"]["tp"]
            fn_sum += data[key]["relevance"]["fn"]
            dets += len(data[key]["bboxes"])
            pos += len(data[key]["locations"])
        fp_tot.append(float(fp_sum))
        tn_tot.append(float(tn_sum))
        tp_tot.append(float(tp_sum))
        fn_tot.append(float(fn_sum))
        pos_tot.append(float(pos))
        dets_tot.append(float(dets))

    print("""Bootstrapped Results (Means):
    Params: iters={0}, sample_size={1}
    Positive Labels: {2:.2f}, Detections: {3:.2f}
    False Positives: {4:.2f}, True Positives: {5:.2f}
    False Negatives: {6:.2f}, True Negatives: {7:.2f}
    Precision: {8:.2f}, Recall: {9:.2f}""".format(
    iters, sample_size,
    np.mean(pos_tot) / sample_size, np.mean(dets_tot) / sample_size,
    np.mean(fp_tot) / sample_size, np.mean(tp_tot) / sample_size,
    np.mean(fn_tot) / sample_size, np.mean(fp_tot) / sample_size,
    np.mean(tp_tot) / (np.mean(tp_tot) + np.mean(fp_tot)),
    np.mean(tp_tot) / (np.mean(tp_tot) + np.mean(fn_tot))))

    return {"iters": np.array(iters), "sample_size": np.array(sample_size),
            "detections": np.array(dets_tot), "fp": np.array(fp_tot),
            "tp": np.array(tp_tot), "fn": np.array(fn_tot), "fp": np.array(fp_tot),
            "prec": np.array(tp_tot) / (np.array(tp_tot) + np.array(fp_tot)),
            "rec": np.array(tp_tot) / (np.array(tp_tot) + np.array(fn_tot))}


def summary(json_path, subset_file=False):
    with open(json_path, "r") as f:
        data = json.load(f)

    if subset_file != False:
        with open(subset_file, "r") as f:
            text = f.readlines()
            kk = [x[:-1] + ".jpg" for x in text]
        tmp = {}
        for k in kk:
            tmp[k] = data[k]
        data = tmp

    fp_sum = tn_sum = tp_sum = fn_sum = pos = neg = dets = 0
    for im in data.keys():
        fp, tn, tp, fn =  data[im]["relevance"].values()
        fp_sum += fp
        tn_sum += tn
        tp_sum += tp
        fn_sum += fn
        if "neg_points" in data[im].keys():
            neg += len(data[im]["neg_points"])
            pos += len(data[im]["pos_points"])
            dets += len(data[im]["bboxes"])
        else:
            neg = 0
            pos += len(data[im]["locations"])
            dets += len(data[im]["bboxes"])

    print ("False Positives: {}, True Positives: {}, False Negatives: {}, True Negatives: {}".format(fp_sum, tp_sum, fn_sum, tn_sum))
    print ("Positive Labels: {}, Negative Labels: {}".format(pos, neg))
    print ("Detections: {}".format(dets))


def plot_im(key, json_file, img_folder):
    neg_xx = neg_yy = pos_xx = pos_yy = bboxes = []
    img = os.path.join(img_folder, key)
    vv = json_file[key]
    neg_coords = vv["neg_points"]
    pos_coords = vv["pos_points"]
    try:
        neg_xx, neg_yy = zip(*neg_coords)
        pos_xx, pos_yy = zip(*pos_coords)
        bboxes = vv["bboxes"]
    except:
        pass
    fp = vv["relevance"]["fp"]
    tp = vv["relevance"]["tp"]
    fn = vv["relevance"]["fn"]
    tn = vv["relevance"]["tn"]

    fig, ax = plt.subplots(nrows=1, ncols=1)
    fig.subplots_adjust(left=0,right=1,bottom=0,top=1)
    rr = ax.scatter(neg_xx, neg_yy, s=80, c="r", alpha=0.5)
    cc = ax.scatter(pos_xx, pos_yy, s=80, c="cyan", alpha=0.5)
    for box in bboxes:
        rect = ax.add_patch(patches.Rectangle((box[0], box[1]), box[2] - box[0],
                                               box[3] - box[1], fill=False,
                                               edgecolor="yellow", lw=2))
    ax.imshow(plt.imread(img), aspect="equal")
    ax.grid(False)
    ax.set_xticks([])
    ax.set_yticks([])

    if len(bboxes) == 0:
        leg = ax.legend([cc, rr], ["Positive Label", "Negative Label"],
                        frameon=True, fontsize=14, loc="upper right", cols=3)
    else:
        leg = ax.legend([rect, cc, rr], ["Pedestrian Detection", "Positive Label",
                                         "Negative Label"], frameon=True,
                        fontsize=14, loc="upper right")
    leg.get_frame().set_alpha(0.8)
    tt = ax.text(5, 5, "FP: {}, TP: {}\nFN: {}, TN: {}".format(fp, tp, fn, tn), fontsize=14, va="top")
    tt.set_bbox(dict(alpha=0.8, edgecolor="w", facecolor="white", boxstyle="round,pad=0.1"))
    plt.show()


# -----------------------------------------------------------------------------
# All training/testing data:
# Detections: 12283, Positive Labels: 16022, Negative Labels: 41449
# False Positives: 99, True Positives: 10833,
# False Negatives: 5189, True Negatives: 41350
#
# Training data:
# Detections: 8565, Positive Labels: 11071, Negative Labels: 29079
# False Positives: 20, True Positives: 7949,
# False Negatives: 3122, True Negatives: 29059
#
# Testing data:
# Detections: 3701, Positive Labels: 4948, Negative Labels: 12363
# False Positives: 78, True Positives: 2881,
# False Negatives: 2067, True Negatives: 12363
# -----------------------------------------------------------------------------
# Camera 717
# Detections: 209, Positive Labels: 292, Negative Labels: 0
# False Positives: 42, True Positives: 167,
# False Negatives: 125, True Negatives: 0
# Precision: 80%, Recall: 57%
#
# Camera 899
# Detections: 1015, Positive Labels: 2581, Negative Labels: 0
# False Positives: 36, True Positives: 979,
# False Negatives: 1602, True Negatives: 0
# Precision: 96%, Recall: 38%
#
# Camera 398
# Detections: 378, Positive Labels: 652, Negative Labels: 0
# False Positives: 44, True Positives: 334,
# False Negatives: 318, True Negatives: 0
# Precision: 88%, Recall: 51%.
#
# All 3
# Detections: 1602, Positive Labels: 3525, Negative Labels: 0
# False Positives: 122, True Positives: 1464
# False Negatives: 2061, True Negatives: 0
# Precision: 92%, Recall: 42%
#
# Bootstrapped Results (Means):
#     Params: iters=10000, sample_size=20
#     Positive Labels: 12.31, Detections: 5.60
#     False Positives: 0.43, True Positives: 5.18
#     False Negatives: 7.13, True Negatives: 0.43
#     Precision: 0.92, Recall: 0.42
# Precision (95% Conf Interval): 0.9202 - 0.9214
# Recall (95% Conf Interval): 0.4247 - 0.4265
