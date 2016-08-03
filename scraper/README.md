# Scraping images of NYC DOT camera

To run this web scraper two things are needed. First a **links.txt** file that has, for each row, a unique NYC DOT webcam url. Second, the **runScrape.py** script that will run the scraper. To run the scraper pass this command in terminal.

```
python runScrape.py
```

This will run the scraper in the starting at 7:30 am. To run the scraper for a fixed amount of time and with a instant start time, run this command in terminal

```
python runScrape.py -f -limit 60
```

Here the `-f` flag runs the scraper instantly after executing the command. The `-limit` flag assigns the number of minutes to run the scraper. In the example above, the scraper will be run for 60 mins. 





