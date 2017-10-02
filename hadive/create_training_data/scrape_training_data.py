import os
import time
import urllib
import random
import sqlite3
import argparse
import datetime as dt

def parse_args():
    """Parse input arguments."""
    parser = argparse.ArgumentParser(description="Scrape training images.")
    parser.add_argument("--count", dest="count", help="How many images to scrape?", default=1)
    parser.add_argument("--cam", dest="cam", help="Specifc camera to scrape (cam_id).", default="")
    return parser.parse_args()


def download_image(cctv_id, description, cursor):
    """Downloads images from DOT camera and adds data to db.
    cctv_id - camera cctv_id
    description - camera location description
    cursor - sqliet3 cursor
    """
    location = description.replace(" ", "_").replace("@", "").replace(".", "").replace("-", "")
    url = 'http://207.251.86.238/cctv{}.jpg'.format(cctv_id)

    now = dt.datetime.now()
    timestamp = now.strftime("%Y-%m-%d-%H-%M-") + str(now.second).zfill(2)
    filename = "{}_{}.jpg".format(timestamp, location)
    data = [filename, False, location, timestamp]

    try:
        urllib.urlretrieve(url, os.path.join("../../data/training/img/", filename))
        return data
    except:
        pass


def scrape_images(count, cam=""):
    """Scrape images at random or from a specific camera (cam_id).
    Args:
        cam (str) - cam_id to scrape (default= "")"""

    conn = sqlite3.connect("../../data/results/ped-count.db")
    c = conn.cursor()
    cams = c.execute("""SELECT cam_id, cctv_id, description FROM cameras
    WHERE cctv_id != 'image' and cctv_id != 'No Response'""").fetchall()

    conn = sqlite3.connect("../../data/training/training.db")
    c = conn.cursor()

    for _ in range(count):
        try:
            if cam == "":
                cam_id, cctv_id, description = random.choice(cams)
                data = download_image(cctv_id, description, c)
                c.execute("INSERT INTO images VALUES(?,?,?,?)", data)
            else:
                cam_id, cctv_id, description = filter(lambda x: x[0] == cam, cams)[0]
                data = download_image(cctv_id, description, c)
                c.execute("INSERT INTO images VALUES(?,?,?,?)", data)
            time.sleep(1)
        except:
            print "Error : {}".format(data)
    conn.commit()


if __name__ == '__main__':
    args = parse_args()
    scrape_images(int(args.count), args.cam)
