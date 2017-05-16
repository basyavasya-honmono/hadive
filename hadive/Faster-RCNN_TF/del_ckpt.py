import os
import time

p = 'Faster-RCNN_TF/output/faster_rcnn_end2end/voc_2007_trainval'
iters = '70000'
running = True

while running == True:
    f_list = sorted(os.listdir(p))
    if len(f_list) > 4:
        for f in f_list[0:3]:
            os.remove(os.path.join(p, f))

    for f in f_list:
        if iters in f:
            running = False

    time.sleep(60)
