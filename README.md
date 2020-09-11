# DigitalLEDWatch
Watch for 64x64 LED-matrix with some fun features. Set up for raspberry 3B.

most of this code is copied from https://github.com/hzeller/rpi-rgb-led-matrix except watch.cc and init_watch.py

watch.cc -> only watch function. is implemented as service/daemon. in case init_watch.py is killed, watch is still displaying time.
led-image-viewer.cc -> only to display pictures and gifs. 
init_watch.py -> contains functions to connect to database and function to activate watch or led-image-viewer

Created a database with columns date, time and filename.

logic for date, time and filename
<ul>
  <li>if date is NULL means to display every day</li>
  <li>if date year is 9999 means to display every year on the same day (e.g birthday or christmas)</li>
  <li>if date is specific (e.g. 2021-07-15) means to display only on this specific day</li>
  <li>if time is 00:00:00 means to display every full hour</li>
    <li>in case date is 9999-04-23 and time 00:00:00 means to display every year on this day, every full hour</li>
  <li>if time is different than 00:00:00 means to display on specific time</li>
  <li>filename is the name of the file to display</li>
 <ul>
  
