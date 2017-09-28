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
    """Read all .xml files in a given folder storing data following the PASCAL
    VOC format, and return the centroids for all positive and negative labels
    Args:
        xml_folder (str): path to folder containing xml files.
    Returns:
        img_points (dict): Dictionary of all label centroids (e.g., {key:
        {pos_points:[], neg_points:[]}}).
    """

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

        img_points[filename] = {"pos_points": pos_points,
                                "neg_points": neg_points}

    return img_points


def combine_json(files, filename):
    """"Combine two json files with shared keys.
    Args:
        files (list): list of paths to the two json files.
        filename (str): output string name (e.g., filename='filename' will
        result in filename.json being written in the current dir)."""

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
    """Deteremine if a given coordinate falls within a box (where the boxes
    axes are parallel to the x and y axis).
    Args:
        point (list): [x, y]
        box (list): [x0, y0, x1, y1, conf]
    Returns:
        (bool)"""

    xx, yy = [float(i) for i in point]
    x0, y0, x1, y1, _ = [float(i) for i in box]
    if xx >= x0 and xx <= x1 and yy >= y0 and yy <= y1:
        return True
    else:
        return False


def points_in_box(points, box):
    """For a list of points, which fall in a given box?
    Args:
        points (list): [[x, y], [x, y]]
        box (list): [x0, y0, x1, y1, conf]
    Returns:
        nn (list): [True, False]"""

    nn = []
    for pp in points:
        nn.append(point_in_box(pp, box))
    return nn


def boxes_per_point(point, bboxes, return_bboxes=True):
    """For a given point, what boxes does it fall in?
    Args:
        point (list): [x, y]
        bboxes (list): [[x0, y0, x1, y1, conf], [x0, y0, x1, y1, conf]]
        return_bboxes (bool): if the function returns the paired boxes
    Returns:
        nn (list): [True, False]
        bb (list): [[x0, y0, x1, y1, conf]]"""

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
    """For a given json file with both label points, and detection boxxes, where
    the positive labels is not exhaustive, classify the number of false
    positives, false negatives, true positives, and true negatives, and add
    results to json.
    Args:
        json_path (str): json file to read and write.
    """
    with open(json_path, "r") as f:
        data = json.load(f)

    for im in data.keys():
        fp = tp = fn = tn = 0

        bboxes = list(data[im]["bboxes"])
        pos_pp = list(data[im]["pos_points"])
        neg_pp = list(data[im]["neg_points"])

        # -- For each neg label, if in a detection fp += 1 and pull a detection,
        # -- otherwise, tn += 1.
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

        # -- For each pos label, if in a detection tp += 1 and pull a detection,
        # -- if not in a box fn += 1.
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

        # -- For each negative point, if it falls in a remaining detection
        # -- fp += 1.
        for pp in neg_pp:
            for bb in bboxes:
                if point_in_box(pp, bb):
                    fp += 1

        # -- Print output for each image.
        print("False Positives: {}, True Positives: {}, False Negatives: {}, True Negatives: {}             ".format(fp, tp, fn, tn))
        sys.stdout.flush()

        # -- Add node storing counts.
        data[im]["relevance"] = {"fp": fp, "tp": tp, "fn": fn, "tn": tn}

    # -- Write to file.
    with open("./output.json", "w") as f:
        json.dump(data, f)

def prec_recall_complete_labels(json_path):
    """For a given json file with both label points, and detection boxxes, where
    the positive labels are exhaustive, classify the number of false
    positives, false negatives, true positives, and true negatives, and add
    results to json.
    Args:
        json_path (str): file to read and write."""

    with open(json_path, "r") as f:
        data = json.load(f)

    for im in data.keys():
        fp = tp = fn = tn = 0

        bboxes = list(data[im]["bboxes"])
        pos_pp = list(data[im]["locations"])

        # -- If the positive label falls within a detection tp += 1 and pull a
        # -- box. If a positive label does not fall in detection fn += 1. For
        # -- each remaining detection fp += 1.
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

        # -- Print output for each image.
        print("False Positives: {}, True Positives: {}, False Negatives: {}, True Negatives: {}             ".format(fp, tp, fn, tn))
        sys.stdout.flush()

        # -- Add node storing counts.
        data[im]["relevance"] = {"fp": fp, "tp": tp, "fn": fn, "tn": tn}

    # -- Write to file.
    with open(json_path, "w") as f:
        json.dump(data, f)


def chunks(l, n):
    """Yield successive n-sized chunks from l.
    Args:
        l (list) - list to split.
        n (int) - size of each split.
    Yields:
        (list)"""

    for i in xrange(0, len(l), n):
        yield l[i:i + n]


def bootstrapsummary(json_path, sample_size=20):
    """Bootstrap results where positive labels are exhaustive to estimate
    confidence intervals.
    Args:
        json_path (str): path to json file.
        sample_size (int): how many samples to include in each Bootstrapped
            subsample.
    Returns:
        (dict): stored lists for values from each bootstrapped subsample."""

    np.random.seed(1)
    with open(json_path, "r") as f:
        data = json.load(f)

    # -- Create empty variables.
    fp_tot = list()
    tn_tot = list()
    tp_tot = list()
    fn_tot = list()
    pos_tot = list()
    neg_tot = list()
    dets_tot = list()
    samples = 0

    # -- Subsample the total number of images per the sample_size and pull data.
    for ix, keys_sample in enumerate(chunks(data.keys(), sample_size)):
        fp_sum = tn_sum = tp_sum = fn_sum = dets = pos = 0
        if len(keys_sample) == sample_size:
            samples = ix + 1
            for key in keys_sample:
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

    # -- Print summary table.
    print("""Bootstrapped Results (Means):
    Params: iters={0}, sample_size={1}
    Positive Labels: {2:.2f}, Detections: {3:.2f}
    False Positives: {4:.2f}, True Positives: {5:.2f}
    False Negatives: {6:.2f}, True Negatives: {7:.2f}
    Precision: {8:.2f}, Recall: {9:.2f}""".format(
    samples, sample_size,
    np.mean(pos_tot) / sample_size, np.mean(dets_tot) / sample_size,
    np.mean(fp_tot) / sample_size, np.mean(tp_tot) / sample_size,
    np.mean(fn_tot) / sample_size, np.mean(fp_tot) / sample_size,
    np.mean(tp_tot) / (np.mean(tp_tot) + np.mean(fp_tot)),
    np.mean(tp_tot) / (np.mean(tp_tot) + np.mean(fn_tot))))

    # -- Return dictioanry of data for each bootstrapped sample.
    return {"iters": np.array(samples), "sample_size": np.array(sample_size),
            "detections": np.array(dets_tot), "fp": np.array(fp_tot),
            "tp": np.array(tp_tot), "fn": np.array(fn_tot), "fp": np.array(fp_tot),
            "prec": np.array(tp_tot) / (np.array(tp_tot) + np.array(fp_tot)),
            "rec": np.array(tp_tot) / (np.array(tp_tot) + np.array(fn_tot))}


def conf_ints(bootstrap_results):
    """Calculate and print confidence intervals for the resulting bootstrapped
    data.
    Args:
        bootstrap_results (dict): output from bootstrapping."""

    prec = bootstrap_results["prec"]
    reca = bootstrap_results["rec"]
    mean_prec = prec.mean()
    mean_reca = reca.mean()
    prec_95 = (prec.std() / np.sqrt(len(prec))) * 1.96
    reca_95 = (reca.std() / np.sqrt(len(reca))) * 1.96

    print("""Confidence Intervals:
    Mean Precision {:.4f} | +/- {:.4f} | {:.4f} - {:.4f}
    Mean Recall    {:.4f} | +/- {:.4f} | {:.4f} - {:.4f}
    """.format(mean_prec, prec_95, mean_prec - prec_95, mean_prec + prec_95,
    mean_reca, reca_95, mean_reca - reca_95, mean_reca + reca_95))


def summary(json_path, subset_file=False):
    """ For a given json file return the sums for false positives, false
    negatives, true positives, true negatives.
    Args:
        json_path (str): path to json file.
        subset_file (bool/str): path to .txt file with keys to subset the data.""""

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
    """Plot an image with it's labels, detections, and confusion matrix.
    Args:
        key (str): key (i.e., filename) in json.
        json_file (str): path to json file storing data.
        img_folder (str): path to file with img files."""

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
    tt = ax.text(5, 5, "FP: {}, TP: {}\nFN: {}, TN: {}".format(fp, tp, fn, tn),
                 fontsize=14, va="top")
    tt.set_bbox(dict(alpha=0.8, edgecolor="w", facecolor="white",
                     boxstyle="round,pad=0.1"))
    plt.show()


# -----------------------------------------------------------------------------
# RESULTS
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
#     Params: iters=14, sample_size=20
#     Positive Labels: 12.48, Detections: 5.66
#     False Positives: 0.42, True Positives: 5.23
#     False Negatives: 7.25, True Negatives: 0.42
#     Precision: 0.92, Recall: 0.42
# Confidence Intervals:
#     Mean Precision 0.9207 | +/- 0.0166 | 0.9041 - 0.9373
#     Mean Recall    0.4250 | +/- 0.0192 | 0.4058 - 0.4442
