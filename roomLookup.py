# importing the requests library
import requests
from bs4 import BeautifulSoup
from urllib import parse
import pandas as pd
import datetime
import math as m
import pickle
import math as m1

roomList = []
roomData = {}


def refreshData(date):
    global roomData
    global roomList
    if not roomData == {}:
        if not dataUpToDate(date):
            updateData(date)
    else:
        try:
            pik = pickle.load(open("roomData.pkl", "rb"))
            roomList = pik[0]
            roomData = pik[1]

            if not dataUpToDate(date):
                updateData(date)

        except(OSError, IOError):
            updateData(date)
            pickle.dump([roomList, roomData], open("roomData.pkl", "wb"))

def dataUpToDate(date):
    table = roomData.get(list(roomData.keys())[0])
    day = 2 + datetime.datetime(int(date[2]), int(monthName(date[1])), int(date[0])).weekday()

    dayTable = table[day]
    esc = dayTable[0]
    res = str.endswith(esc, str(date[0]) + "." + monthName(date[1]))
    return res

def getRoomList():
    URL = "http://www.rauminfo.ethz.ch/IndexPre.do"

    # sending get request and saving the response as response object
    r = requests.get(url=URL)
    # extracting data
    soup = BeautifulSoup(r.content, 'html.parser')
    table = soup.find_all("table")[5]

    rows = table.find_all("tr")

    roomList = []

    for i in range(2, len(rows)):
        link = rows[i].find("td").find("a").get("href")
        params = parse.parse_qs(link)

        entry = []
        for value in params.values():
            entry.append(value[0])
        roomList.append(entry)

    return roomList

def monthName(written):
    return written.replace('Nov', '11').replace('Dez', '12').replace('Jan', '01').replace('Feb', '02')

def updateData(date):
    listR = getRoomList()
    
    for room in listR:
        updateRoom(date, room)
    
    pickle.dump([roomList, roomData], open("roomData.pkl", "wb"))

def updateRoom(date, room):
    URL = "http://www.rauminfo.ethz.ch/Rauminfo/Rauminfo.do"

    params = parse.parse_qs("region=Z&areal=Z&gebaeude=MM&geschoss=C&raumNr=78.1&rektoratInListe=true&raumInRaumgruppe=true&tag=01&monat=Dez&jahr=2019&checkUsage=anzeigen")

    params["region"] = room[0]
    params["areal"] = room[1]
    params["gebaeude"] = room[2]
    params["geschoss"] = room[3]
    params["raumNr"] = room[4]

    params["tag"] = date[0]
    params["monat"] = date[1]
    params["jahr"] = date[2]

    # sending get request and saving the response as response object
    r = requests.get(url=URL, params=params)

    try:
        # extracting data
        entryT = pd.read_html(r.content, index_col=0)
        entry = entryT[1]
        del entry[1]

        roomData.update({room[0] + " " + room[1] + " " + room[2] + " " + room[3] + " " + room[4]: entry})
        if not room in roomList:
            roomList.append(room)
    except(ValueError):
        pass    
    except(IndexError):
        pass

def roomEmptyAtTime(room, date, time, entries):
    refreshData(date)
    table = roomData.get(room[0] + " " + room[1] + " " + room[2] + " " + room[3] + " " + room[4])

    day = 2 + datetime.datetime(int(date[2]), int(date[1].replace('Nov', '11').replace('Dez', '12').replace('Jan', '1').replace('Feb', '2')), int(date[0])).weekday()

    dayTable = table[day]

    nowTime = time[0] * 60 + time[1]

    chkTime = int((nowTime + 15 - 7*60)/15)

    if not str(dayTable[chkTime]) == "nan":
        return
    
    isAvaible = False
    avaibleSince = 0
    i = 0

    while(i < len(dayTable) and nowTime + 30 > 7*60 + i * 15):

        if str(dayTable[i]) == "nan":
            if not isAvaible:
                avaibleSince = 7*60 + i * 15 - 15
            isAvaible = True
        else:
            isAvaible = False
        i += 1

    if not isAvaible:
        return

    while(i < len(dayTable)):

        if not str(dayTable[i]) == "nan":
            entries.append([avaibleSince, 7*60+i*15 - 15, room])
            return
        i += 1

    entries.append([avaibleSince, 7*60+len(dayTable)*15 - 15, room])
    return

def lookUpOn(date, time, filter):
    avaRooms = []
    refreshData(date)

    for room in roomList:
        if filter(room):
            roomEmptyAtTime(room, date, time, avaRooms)
            
    return avaRooms