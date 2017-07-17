### Pedestrian Detection Workflow:

data_scrape.py: scrape images from url addresses listed in cameras.json file & store detected count numbers in the output.csv file

data_scrape_db.py: version of data_scrape.py from a postgre database, where all the cameras information is stored in 1 table and the detected count numbers are continuously inserted into an existing table for output.

delete_extra_imgs.py: keeps the images crawled at a maximum number defined in the script.

get_time: get the direction information on the camera images.