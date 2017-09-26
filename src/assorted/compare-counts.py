import os
import json
import numpy as np
import seaborn as sns
import statsmodels.api as sm
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def compare_counts(path, img_file):
    with open(os.path.join(path, "detections.json")) as f:
        rcnn_dets = json.load(f)
    with open(os.path.join(path, "peds_{}.json".format(img_file.split("_")[0]))) as f:
        hand_counts = json.load(f)

    xx, yy = [], []
    for im in rcnn_dets.keys():
        xx.append(hand_counts[im]["count"])
        yy.append(rcnn_dets[im]["count"])

    fig, [ax1, ax2] = plt.subplots(nrows=1, ncols=2, figsize=(14, 5))
    m = sm.OLS(yy, xx).fit().params[0]

    mxx = max(xx)
    ax1.scatter(xx, yy, s=60, c="k", alpha=0.6, label="Images")
    ax1.plot([0, mxx + 5], [0 * m, (mxx + 5) * m ], c="r", label="Linear Reg.")
    ax1.plot([0, mxx], [0, mxx], c="g", alpha=0.4, ls="dashed", label="1:1")

    ax1.text(mxx + 3, 2, "y ~ {:.2f} x".format(m), ha="right", fontsize=14)
    ax1.set_ylabel("Faster RCNN Pedestrian Count", fontsize=16)
    ax1.set_xlabel("Hand Pedestrian Count", fontsize=16)
    ax1.set_title("Relative Accuracy", fontsize=16)
    ax1.tick_params(labelsize=14)
    ax1.set_ylim(0, max(yy) + 5)
    ax1.set_xlim(0, max(xx) + 5)

    px, py = zip(*hand_counts[img_file]["locations"])
    for box in rcnn_dets[img_file]["bboxes"]:
        ax2.add_patch(patches.Rectangle((box[0], box[1]), box[2] - box[0],
                                         box[3] - box[1], fill=False,
                                         edgecolor="yellow", lw=2))
    ax2.imshow(plt.imread(os.path.join(path, img_file)), aspect="equal")
    ax2.scatter(px, py, c="cyan", s=80, alpha=0.5)
    ax2.set_title("Example Image", fontsize=16)
    ax2.set_xticks([])
    ax2.set_yticks([])
    ax2.grid("off")

    plt.tight_layout()
    plt.show()
