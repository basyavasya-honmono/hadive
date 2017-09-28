from __future__ import print_function
import os
import sys
from PIL import Image, ImageStat

def brightness(im_file):
    """Calculate the brightness of an image.
    Args:
        im_file (str): path to img file.
    Return:
        (float) - brighness."""
    try:
        im = Image.open(im_file).convert('L')
        stat = ImageStat.Stat(im)
        return stat.mean[0]
    except:
        pass

def get_well_lit_ims(path):
    """Find characteristic images for each camera with a brightness between 100-
    115 (well-lit).
    Args:
        path (str): path to folder containing imgs.
    Returns:
        bright_ims (dict): dictiaonry of characteristic images (value) for each
            camera (key)."""

    ims = os.listdir(path)
    cams = set(map(lambda x: x.split("_")[0], ims))
    bright_ims = {}
    for ix, cam in enumerate(cams):
        bright_ims[cam] = ("file", 0)
        cam_ims = filter(lambda x: x.startswith(cam + "_"), ims)
        for im in cam_ims:
            bb = brightness(os.path.join("./", im))
            if (bb > 110) and (bb < 115):
                bright_ims[cam] = (im, bb)
                break
        print("Completed cam: {}/{}".format(ix, len(cams)), end="\r")
        sys.stdout.flush()

    return bright_ims

def collect_ims(ims):
    """For each cahracteristic image, copy to an outside folder.
    Args:
        ims (dict): dictionary containing filenames."""

    os.system("mkdir {}".format(os.path.join("..", "collected_ims")))
    for key in ims.keys():
        mv_im = os.path.join("..", "collected_ims", key + ".jpg")
        if ims[key][0] == "file":
            os.system("cp {} {}".format(os.path.join(".", "988_1500765270.jpg"), mv_im))
        else:
            os.system("cp {} {}".format(os.path.join(".", ims[key][0]), mv_im))

def pull_ims(cam_id, path):
    """"For a given camera copy all relevant images to an outside folder.
    Args:
        cam_id (str): cam_id to copy.
        path (str): path to folder containing images."""

    ims = filter(lambda x: x.startswith(cam_id + "_"), os.listdir(path))
    os.system("mkdir {}_ims".format(cam_id))
    for im in ims:
        os.system("cp {} ./{}_ims/".format(os.path.join(path, im), cam_id))

# ims = get_well_lit_ims("./")
# collect_ims(ims)
#
# os.system("see {}".format(ims["899"][0]))
