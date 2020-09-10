import os
import mysql.connector
from datetime import date as DATE
from datetime import time as TIME
from datetime import datetime as DATETIME
import time

path_gif = '/home/pi/gifs/'
path_imageviewer = '/home/pi/DigitalLEDWatch/led-image-viewer'
start_service = 'systemctl start watch.service'
stop_service = 'systemctl stop watch.service'

# load database

mydb = mysql.connector.connect(
	host='localhost',
	user='pi',
	password='digitalwatch2020',
	database='watch'
)

mycursor = mydb.cursor()
sql = 'select * from gifs'
mycursor.execute(sql)
whole_table = mycursor.fetchall()

#start watch service
os.system(start_service)

# x is for gif -> just show gif once per minute and not in loop
x = 0
temp_minute = 0

while 1:
	# search for entries in database and corelate them with time
	for row in whole_table:

		#check if everyday (date == NULL) or one a year (9999-month-day) or a special day (2021-08-19)
		if None == row[0]:

			#convert entry time to hour and minutes
			entry_hour = row[1].seconds // 3600
			entry_minute = (row[1].seconds % 3600) // 60
			entry_second = row[1].seconds % 60

			if DATETIME.now().hour == entry_hour and DATETIME.now().minute == entry_minute and x == 0:
				os.system(stop_service)
				os.system('{} -t15 {}{}'.format(path_imageviewer, path_gif, row[2]))
				os.system(start_service)
				temp_minute = DATETIME.now().minute
				x = 1


		else:

			#convert entry to year, month, day, hour, minute
			entry_year = row[0].year
			entry_month = row[0].month
			entry_day = row[0].day
			entry_hour = row[1].seconds // 3600
			entry_minute = (row[1].seconds % 3600) // 60
			entry_second = row[1].seconds % 60

			if entry_year == 9999 and entry_month == DATETIME.now().month and entry_day == DATETIME.now().day and entry_hour == DATETIME.now().hour and entry_minute == DATETIME.now().minute:
				os.system(stop_service)
				os.system('{} -t15 {}{}'.format(path_imageviewer, path_gif, row[2]))
				os.system(start_service)
				temp_minute = DATETIME.now().minute
				x = 1
			elif entry_year == DATETIME.now().year and entry_month == DATETIME.now().month and entry_day == DATETIME.now().day and entry_hour == DATETIME.now().hour and entry_minute == DATETIME.now().minute:
				os.system(stop_service)
				os.system('{} -t15 {}{}'.format(path_imageviewer, path_gif, row[2]))
				os.system(start_service)
				temp_minute = DATETIME.now().minute
				x = 1

		#check if gif already displayed this minute otherwise change x back to 0
		if temp_minute != DATETIME.now().minute:
			x = 0

		#chill a little bit till checking again
		time.sleep(5)


#os.system('/home/pi/DigitalLEDWatch/led-image-viewer ' + path)
