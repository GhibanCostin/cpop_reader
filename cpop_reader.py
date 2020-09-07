from bs4 import BeautifulSoup
import requests
import csv
from datetime import datetime
import os
import tkinter as tk

# get user input in format <325CC>; check validity 
valid_input = False

def char_range(start, end):
    ret = []
    while ord(start) <= ord(end):
        ret.append(start)
        start = chr(ord(start) + 1)
    return ret

year_no = None
group_no = None
series = None

while valid_input == False:
    print("Type your group in the format <000>C/A<X>. Eg. 325CC or 331AA")
    grupaSerie = input()

    if len(grupaSerie) != 5:
        print("<Error> Wrong input")
        continue
    elif grupaSerie[0] != '3': 
        print("<Error> Wrong input")
        continue
    elif grupaSerie[1] not in char_range('1', '4'):
        print("<Error> Wrong input")
        continue
    elif grupaSerie[2] not in char_range('0', '6'):
        print("<Error> Wrong input")
        continue
    elif grupaSerie[3] not in ['C', 'A'] or grupaSerie[4] not in char_range('A', 'D'):
        print("<Error> Wrong input")
        continue
    else:
        year_no = grupaSerie[1]
        group_no = grupaSerie[2]
        series = grupaSerie[3:]
        valid_input = True    


# parse the shrine of cpop
main_url = "https://acs.pub.ro/~cpop"
source = requests.get(main_url).text
main_soup = BeautifulSoup(source, "lxml")

# get last modified dates from site
links = main_soup.find_all('a')
links = filter(lambda link : True if link.text in ["orare_sem1/", "orare_sem2/"] else False, links)
links = list(links)
sem_links = map(lambda l : l.get("href"), links)
sem_links = list(sem_links)

dates = []

for link in links:
    dates.append(link.parent.findNext("td").text)

#last modified dates for orare_sem_1 and orare_sem_2
last_dates_sem = []

# file to store the last time we checked the schedule
first_use = False

try:
    f = open("./last_modified.csv")
    f.close()
except FileNotFoundError:
    first_use = True

if not first_use:
    with open("./last_modified.csv", newline = '') as last_mod_file:
        file_reader = csv.reader(last_mod_file, delimiter = ',')
        for row in file_reader:
            last_dates_sem = row
            # read only the first line in file
            break
else:
    # write last modified dates to file
    last_dates_sem = dates
    with open("./last_modified.csv", "w", newline = '') as last_mod_file:
        file_writer = csv.writer(last_mod_file, delimiter = ',')
        file_writer.writerow(last_dates_sem)

if last_dates_sem == []:
    # the file was empty
    first_use = True

# compare semester (overall) dates
if last_dates_sem != dates or first_use:
    # check which date changed
    i = 1 if last_dates_sem[0] == dates[0] else 0

    if last_dates_sem[0] != dates[0] and last_dates_sem[1] != dates[1]:
        # both changed, take the closest date to now
        now = datetime.now().strftime("%d-%b-%Y %H:%M  ")
        dts = list(map(lambda d : datetime.strptime(d, "%d-%b-%Y %H:%M  "), dates))
        i = 0 if now - dts[0] < now - dts[1] else 1    

    # follow the corresponding link
    sem_source = requests.get(main_url + '/' + sem_links[i]).text
    sem_soup = BeautifulSoup(sem_source, "lxml")
    series_schedule = sem_soup.findAll('a')
    series_schedule = list(filter(lambda sch : True if sch.get("href").find("Orar" + year_no + series) != -1 else False, series_schedule))
    sch_last_date = series_schedule[0].parent.findNext("td").text
    saved_dates = []
    to_download = False

    with open("./last_modified.csv", newline = '') as last_mod_file:
        file_reader = csv.reader(last_mod_file, delimiter = ',')
        for row in file_reader:
            for el in row:
                saved_dates.append(el)
        # saved_dates is a list of lists
        saved_dates = saved_dates[2:]

    # find the last modified date saved for the user's input
    saved_dates = list(filter(lambda d : True if d.find('3' + year_no + group_no + series) != -1 else False, saved_dates))

    if len(saved_dates) == 0:
        with open("./last_modified.csv", "a", newline = '') as last_mod_file:
            # append group last modified date
            to_download = True
            saved_dates = ['3' + year_no + group_no + series + " : " + sch_last_date]
            file_writer = csv.writer(last_mod_file)
            file_writer.writerow(saved_dates)
            
    sch_last_date = datetime.strptime(sch_last_date, "%d-%b-%Y %H:%M  ")
    saved_date = datetime.strptime(saved_dates[0][8:], "%d-%b-%Y %H:%M  ")

    if sch_last_date > saved_date:
        to_download = True

    if to_download:
        schedule = requests.get(main_url + '/' + sem_links[i] + '/' + series_schedule[0].get("href"), allow_redirects = True)
        open("Orar" + year_no + series + "sem" + str(i+1) +  ".xls", "wb").write(schedule.content)
    else:
        print("<Info> Orarul seriei nu s-a modificat")

    # write the new dates at the beginning of the file
    data = []
    with open("./last_modified.csv", newline = '') as last_mod_file:
        file_reader = csv.reader(last_mod_file)
        data = [row for row in file_reader]
    with open("./last_modified.csv", "w", newline = '') as last_mod_file:
        file_writer = csv.writer(last_mod_file)
        file_writer.writerow(dates)
        file_writer.writerows(data[1:])
else:
    print("<Info> Niciun orar nu s-a modificat")

# last_mod_file.close()
input("Press any key to exit...")
