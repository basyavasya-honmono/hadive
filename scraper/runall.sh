#!/bin/bash

echo 'Starting bash script'
nohup python vid_scrap.py -links links/224 -limit 480 -s output/ -r records_here.txt > nohup_224.out &
nohup python vid_scrap.py -links links/431 -limit 480 -s output/ -r records_here.txt > nohup_431.out &
nohup python vid_scrap.py -links links/456 -limit 480 -s output/ -r records_here.txt > nohup_456.out &
nohup python vid_scrap.py -links links/503 -limit 480 -s output/ -r records_here.txt > nohup_503.out &
nohup python vid_scrap.py -links links/511 -limit 480 -s output/ -r records_here.txt > nohup_511.out &
nohup python vid_scrap.py -links links/517 -limit 480 -s output/ -r records_here.txt > nohup_517.out &
nohup python vid_scrap.py -links links/519 -limit 480 -s output/ -r records_here.txt > nohup_519.out &
nohup python vid_scrap.py -links links/522 -limit 480 -s output/ -r records_here.txt > nohup_522.out &
nohup python vid_scrap.py -links links/527 -limit 480 -s output/ -r records_here.txt > nohup_527.out &
nohup python vid_scrap.py -links links/535 -limit 480 -s output/ -r records_here.txt > nohup_535.out &
nohup python vid_scrap.py -links links/716 -limit 480 -s output/ -r records_here.txt > nohup_716.out &
nohup python vid_scrap.py -links links/717 -limit 480 -s output/ -r records_here.txt > nohup_717.out &
nohup python vid_scrap.py -links links/741 -limit 480 -s output/ -r records_here.txt > nohup_741.out &
nohup python vid_scrap.py -links links/791 -limit 480 -s output/ -r records_here.txt > nohup_791.out &
nohup python vid_scrap.py -links links/827 -limit 480 -s output/ -r records_here.txt > nohup_827.out &
nohup python vid_scrap.py -links links/934 -limit 480 -s output/ -r records_here.txt > nohup_934.out &
nohup python vid_scrap.py -links links/937 -limit 480 -s output/ -r records_here.txt > nohup_937.out &

echo 'Ran'
