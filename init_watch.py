import os
import mysql.connector
from datetime import date as DATE
from datetime import time as TIME
from datetime import datetime as DATETIME
import time
import atexit

# global variables
path_gif = '/home/pi/gifs/'
path_imageviewer = '/home/pi/DigitalLEDWatch/led-image-viewer'
start_service = 'systemctl start watch.service'
stop_service = 'systemctl stop watch.service'
brightness_std = 50
brightness_sunset = 8
# is for gif -> just show gif once per minute and not in loop
temp_minute = 999

# load database
mydb = mysql.connector.connect(
    host='localhost',
    user='pi',
    password='<enter password>',
    database='watch'
)

mycursor = mydb.cursor()
table_gif = 'select * from gifs'
mycursor.execute(table_gif)
gifs = mycursor.fetchall()

table_sunrise_sunset = 'select * from sunrise_sunset'
mycursor.execute(table_sunrise_sunset)
sunrise_sunset = mycursor.fetchall()

# functions
def change_brightness(brightness):
    configfile = '/etc/watch_args'

    with open(configfile, "w") as f:
        f.write('ARG1=-b {}'.format(brightness))

def start_stop_gif(gifname):
    os.system(stop_service)
    os.system('{} -t15 {}{}'.format(path_imageviewer, path_gif, gifname))
    os.system(start_service)
    temp_minute = DATETIME.now().minute

# start watch service once
os.system(start_service)

while 1:

    for row in sunrise_sunset:

        entry_year = row[0].year
        entry_month = row[0].month
        entry_day = row[0].day
        entry_hour_sunrise = row[1].seconds // 3600
        entry_minute_sunrise = (row[1].seconds % 3600) // 60
        entry_hour_sunset = row[2].seconds // 3600
        entry_minute_sunset = (row[2].seconds % 3600) // 60

	#sunrise
        if entry_year == DATETIME.now().year and \
           entry_month == DATETIME.now().month and \
           entry_day == DATETIME.now().day and \
           entry_hour_sunrise == DATETIME.now().hour and \
           entry_minute_sunrise == DATETIME.now().minute and \
           temp_minute != DATETIME.now().minute:
            change_brightness(brightness_std)
            start_stop_gif('sunrise.gif')

	#sunset
        if entry_year == DATETIME.now().year and \
           entry_month == DATETIME.now().month and \
           entry_day == DATETIME.now().day and \
           entry_hour_sunset == DATETIME.now().hour and \
           entry_minute_sunset == DATETIME.now().minute and \
           temp_minute != DATETIME.now().minute:
            change_brightness(brightness_sunset)
            start_stop_gif('sunset.gif')

    # search for entries in database and corelate them with time
    for row in gifs:

        # check if everyday (date == NULL) or one a year (9999-month-day) or a special day (2021-08-19)
        # everyday -> date == NULL/None
        if None == row[0]:

            # convert entry time to hour and minutes
            entry_hour = row[1].seconds // 3600
            entry_minute = (row[1].seconds % 3600) // 60
            entry_second = row[1].seconds % 60

            if DATETIME.now().hour == entry_hour and \
               DATETIME.now().minute == entry_minute and \
               temp_minute != DATETIME.now().minute:
                start_stop_gif(row[2])

        else:

            # convert entry to year, month, day, hour, minute
            entry_year = row[0].year
            entry_month = row[0].month
            entry_day = row[0].day
            entry_hour = row[1].seconds // 3600
            entry_minute = (row[1].seconds % 3600) // 60
            entry_second = row[1].seconds % 60

            # every year on this date, display the gif every full hour e.g birthday
            if entry_year == 9999 and \
               entry_month == DATETIME.now().month and \
               entry_day == DATETIME.now().day and \
               entry_hour == 0 and \
               entry_minute == 0 and \
               temp_minute != DATETIME.now().minute:
                if DATETIME.now().minute == 0:
                    start_stop_gif(row[2])

            # every year on this date, display once on defined time e.g
            elif entry_year == 9999 and \
                 entry_month == DATETIME.now().month and \
                 entry_day == DATETIME.now().day and \
                 entry_hour == DATETIME.now().hour and \
                 entry_minute == DATETIME.now().minute and \
                 temp_minute != DATETIME.now().minute:
               start_stop_gif(row[2])

            # defined date and time
            elif entry_year == DATETIME.now().year and \
                 entry_month == DATETIME.now().month and \
                 entry_day == DATETIME.now().day and \
                 entry_hour == DATETIME.now().hour and \
                 entry_minute == DATETIME.now().minute and \
                 temp_minute != DATETIME.now().minute:
                start_stop_gif(row[2])

        # chill a little bit till checking again
        time.sleep(0.25)
