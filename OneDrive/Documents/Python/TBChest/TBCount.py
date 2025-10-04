import autoit
import cv2
import datetime
import os
import pyautogui
from time import sleep
import pytesseract
import re
import pandas
import random
import sys

qlist = []

def initialize():
    #activate the game
    autoit.win_activate("Total Battle: Tactical War Game")
    sleep(.2)
    createList()


def getOcrText(x, y, l, h):
    screenshot = pyautogui.screenshot(region=[x, y, l, h])

    try:
        text = pytesseract.image_to_string(screenshot, lang='eng', config='--psm 12 --oem 1')
    except:
        text = ""
    return text


def clickIt(x, y, delay=.1):
    # click and wait(add it some random movement)
    pos = autoit.mouse_get_pos()
    autoit.mouse_move(pos[0] + random.randint(-5, 5), pos[1] + random.randint(-5, 5))
    
    autoit.mouse_click("left", x, y)
    sleep(delay + random.random())


def getImage(knd, sub, amt):
    img = cv2.imread(knd + '_' + sub + '_' + amt + '.jpg')
    a = cv2.imread(knd + '_' + sub + '_' + amt + '.jpg')
    b = cv2.imread('.\\' + knd + '_' + sub + '_' + amt + '.jpg')
    c = cv2.imread('search_clan_1.jpg')

    return img


# find an image on the screen
def findImgonScreen(searchfor_img, threshold):
    try:
        res = pyautogui.locateOnScreen(searchfor_img, confidence = threshold, grayscale=True)
        return (round (res.left + res.width / 2), round (res.top + res.height / 2))
    except:
        return None


def runClick(part1, part2, part3, delay=.1, threshold=.8):
    try:
        img = getImage(part1, part2, part3)
        place = findImgonScreen (img, threshold)
        clickIt(place[0], place[1], delay)
        return place
    except:
        pass


# create the list
def createList():
    dt = datetime.datetime.now()
    qlist.append([100, dt])

    dt2 = datetime.datetime(dt.year, dt.month, dt.day, 0, 0, 0)
    qlist.append([200, dt2])
   
    dt2 = datetime.datetime(dt.year, dt.month, dt.day, 23, 59, 0)
    #dt2 = datetime.datetime(dt.year, dt.month, dt.day, 10, 33, 0)
    qlist.append([300, dt2])


# clean the chest text
def cleanChestText(txt1):
    txt2 = txt1.replace('\n', ',')
    txt3 = re.sub(r'[^a-zA, -Z0-9]', '', txt2)
    txt4 = txt3.replace(',,', ',')

    #txt2 = txt1.replace('\n', ',')
    #txt4 = txt3.replace('~', '')
    
    txt5 = txt4.replace('),', '')
    txt6 = txt5[:-1]
    txt7 = txt6.replace('From: ', '')

    txt8 = txt7.replace('Source: ', '')
    txt9 = txt8 + "\n"

    return txt9


def doWrite(score_file, error_file, txt):
        commas = txt.count(",")
        if commas == 2:
            score_file.writelines(txt)
            score_file.flush()  # Flushes the internal buffer
            os.fsync(score_file.fileno()) # Forces OS to write to disk
        else:
            error_file.writelines(txt)
            error_file.flush()  # Flushes the internal buffer
            os.fsync(error_file.fileno()) # Forces OS to write to disk



def doOpenButtons(score_file, error_file, place, img):
# loop thru all of the open buttons
    while place is not None:
        txt = getOcrText(place[0] - 567, place[1] - 73, 380, 75)
        txt2 = cleanChestText(txt)
        if txt2 != None:
            doWrite(score_file, error_file, txt2)

        clickIt(place[0], place[1], .1)
        place = findImgonScreen(img, .6)


def doSummary(score_file):
    score_file.close()

    details_file = open(score_file.name, 'r')
    df = pandas.read_csv(details_file)

    group_counts = df.groupby('Person')['Person'].size()
    details_file.close()

    sname = score_file.name[:-12] + '_Summary.txt'
    group_counts.to_csv(sname)


def createFile(ext = None):
    dt = datetime.datetime.now()
    dname = dt.strftime('%b %d %Y') + ext
    if os.path.exists(dname):
        sfile = open(dname,'a')
    else:
        sfile = open(dname,'w')
        sfile.writelines('Chest,Person,Crypt\n')

    sfile.flush()  # Flushes the internal buffer
    os.fsync(sfile.fileno()) # Forces OS to write to disk

    return sfile


def clanGifts(score_file, error_file):
    runClick('search', 'clan', '1')
    gplace = runClick('search', 'gifts', '1')
    
# loop thru all of the delete buttons
    while runClick('search', 'delete', '1', .1) is not None:
        autoit.mouse_move(100, 100)

    img = getImage('search', 'open', '1')
    place = findImgonScreen(img, .6)

    doOpenButtons(score_file, error_file, place, img)
    runClick('search', 'tgifts', '1')

# loop thru all of the delete buttons
    while runClick('search', 'delete', '1', .1) is not None:
        autoit.mouse_move(100, 100)

# loop thru all of the open buttons 
    place = findImgonScreen(img, .6)
    doOpenButtons(score_file, error_file, place, img)

# close the jobs dialog
    runClick('search', 'close', '1')
    runClick('search', 'close', '2')
    runClick('search', 'close', '3')


# Start of the program
initialize()

#sys.argv

score_file = createFile('_Details.txt')
err_file = createFile('_Error.txt')
doSummary(score_file)

now = []
now.append(datetime.datetime.now())

# loop thru the queue
while len(qlist) > 0:
    qitem = qlist[0]
    tm = qitem[1]

    now.append(datetime.datetime.now())
    difference = datetime.timedelta.total_seconds(now[0] - tm)
    now.remove(now[0])

    task = 0
    if difference >= 0:
        task = qitem[0]

    match task:
        case 0:
            task = qlist[0][0] 
            dt = qlist[0][1] 
            qlist.remove(qitem)
            qlist.append([task, dt])
            sleep(5)
            pass

        case 100: 
            pos = autoit.mouse_get_pos()
            autoit.mouse_move(pos[0] + random.randint(-5, 5), pos[1] + random.randint(-5, 5))
            qlist.remove(qitem)
            dt = datetime.datetime.now() + datetime.timedelta(seconds = 15)
            qlist.append([100, dt])

        case 200:
            clanGifts (score_file, err_file)
            qlist.remove(qitem)
            dt = datetime.datetime.now() + datetime.timedelta(minutes = 5)
            qlist.append([200, dt])

# fix this the day maybe wrong
        case 300:
            doSummary(score_file)
            while qlist.remove(qlist[0]):
                pass
            createList()
            score_file = createFile('_Details.txt')
            err_file = createFile('_Error.txt')