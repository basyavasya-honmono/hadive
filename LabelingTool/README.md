## TOOL DESCRIPTION

This is the Labeling tool for the Hadive - 
[FixedRectLabeling.py](https://github.com/gdobler/hadive/blob/master/LabelingTool/FixedRectLabeling.py) to draw patches around humans (positive) and non-human (negative) examples per image for training 
our HOG based SVM and Convolution Neural Network. They are of fixed aspect ratio (3/4). 

## WORKING 

1. Center your mouse around the object you want to draw the patch around and click (one click). 
   This will create a patch (blue by default for humans) of aspect ratio 3/4.

2. If you want to change the color of the patch - enter 'r' key to change the color of the following patch you will draw.
   This will change color to 'red' - reserved for labeling non-human examples

3. If you want to remove the previous patch you drew (because you are a Perfectionist!) - enter 'd'. This will delete the previous 
   patch you drew. 

4. If you just want your canvas back and remove all patched. Enter 'c' - this will clear the screen.

5. RESIZING
    ##### NOTE: Increase and Decrease of the patch will happen maintaining the same aspect ratio.
It will not be by increase in width alone or height alone (The draggable rectangle vertices feature is not present). 
And it works on your current patch only (the latest one you just drew). So make your current patch perfect and then move forward, unless you want to come back again by entering 'c' and redoing it (You don't want to do that!). Wondering why we did that ? Go read [Hick's Law](https://en.wikipedia.org/wiki/Hick%27s_law) !

    *  Enter 'tab' to increase the the aspect ratio of the current patch

    *  Enter 'control' to decrease the aspect ratio of the current patch

    *  But if you person is too small ( DOT camera shy! ) and you still want to catch them, draw the patch (click) and enter '2'.
Suggested Usage For: Humans in usually the middle of the image, a little farther from the camera 
    *  But there are too small (at the corner of images) - enter '3' after you draw the     patch.
Suggested Usage For: Humans farthest from the camera (at the corners) and your Eagle Eyes caught them!

    *  Didn't get it perfect (Picasso, are't you :D ?) - Enter 'tab' and increase the patch aspect ratio or 'control' to decrease the patch aspect ratio. 

    * The key here is in you choosing the right center of the patch (Step 1 in Working)! All action goes around it.

    * All this works in the same way for non-human labeled data you want to generate (red color patch). 


6. ##### Please enter 'q' at the end to quit the plot . Basically this will store all the patch co-ordinates, and patch information in the database.
*This is how all your art will get saved into sweet little numpy files( and .hdr file)*


That is almost it - any changes/suggestions - slack it/or change them yourself! 
(update the readme.md once finalized)
