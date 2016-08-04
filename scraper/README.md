# Scraping images of NYC DOT camera

To run this web scraper two things are needed. First a **links.txt** file that has, for each row, a unique NYC DOT webcam url. Second, the **runScrape.py** script that will run the scraper. To run the scraper pass this command in terminal.

```
python runScrape.py
```

This will run the scraper in the starting at 7:30 am for 720 mins (12 hours). To run the scraper for a fixed amount of time and with a instant start time, run this command in terminal

```
python runScrape.py -f -limit 60
```

Here the `-f` flag runs the scraper instantly after executing the command. The `-limit` flag assigns the number of minutes to run the scraper. In the example above, the scraper will be run for 60 mins. 

### Output from the scraper
By default the scraper will create a directory with the current date as the directory name. If the scraper is run multiple times in a single day an unique uuid value will be concatenated to the directory name. Image names will be assigned based on the time of scraping and the camera name. For example `year-month-day-hour-minute-second_CAMERA_NAME.jpg`.

### links.txt file content
Inside the **links.txt** each row is a unique camera link. For example, http://dotsignals.org/google_popup.php?cid=717. To find the relevant or new camera urls visit http://dotsignals.org/, click on the camera icon of interest and search the html of the camera webpage to file the direct link to the traffic camera. 



