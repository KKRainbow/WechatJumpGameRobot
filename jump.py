#!/usr/bin/env python3
import numpy as np
import cv2
import sys
import os
import os.path
import datetime as dt
import math
import itertools

class Pos:
    LEFT= 1
    RIGHT = 2

def callShell(cmd):
    if os.system(cmd) != 0:
        print("Failed to call comd: ", cmd)
        sys.exit(1)

def getScreenShot():
    fname = str(dt.datetime.now()) + '.png'
    callShell('adb shell /system/bin/screencap -p /sdcard/screenshot.png && adb pull /sdcard/screenshot.png "./%s"' % fname)
    return fname

def makeJump(ydiff):
    callShell('adb shell input touchscreen swipe 250 323 250 323 %d' % int(ydiff / 550 * 800))

def getScaledImage(img, frag):
    h,w = img.shape[:2]
    return cv2.resize(img, (round(w * frag), round(h * frag)))

res = False
def getStartPoint(img, bodyImg):
    global res
    if res != False:
        return res
    bh, bw = bodyImg.shape[:2]
    ret = cv2.matchTemplate(img, body, cv2.TM_SQDIFF_NORMED)
    info = cv2.minMaxLoc(ret)
    minVal,maxVal,minLoc,maxLoc = info

    h, w = img.shape[:2]
    x, y = minLoc
    x += int(bh * 0.5)
    y += int(bh * 1.0)
    pos = Pos.RIGHT
    if x < w / 2:
        pos = Pos.LEFT
    res = (x, y, pos)

    return res

def getGray(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    chans = cv2.split(hsv)
    return chans[1], chans[2]

def getStopPoint(img, method=1):
    # gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY if method == 1 else cv2.COLOR_RGB2GRAY)
    sx, sy, pos = getStartPoint(img, body)
    iImg, off = getInterest(img, sx, sy, pos)
    graya, grayb = getGray(iImg)

    getBinaryImage = lambda x : cv2.adaptiveThreshold(~x, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 3, -2);
    bImga = getBinaryImage(graya)
    bImgb = getBinaryImage(grayb)

    ibImg = cv2.bitwise_or(bImga, bImgb)

    nonZero = cv2.findNonZero(ibImg)

    l = [item[0] for item in nonZero]
    gIter = itertools.groupby(l, lambda x: x[1])
    endx = next(next(gIter)[1])[0]
    prevx = endx
    endy = None
    for y, x in gIter:
        maxx = max(x, key=lambda item: item[0])[0]
        if maxx <= prevx:
            endy = y
            break
        else:
            prevx = maxx
    if endy == None:
        endy = max(nonZero, key=lambda item: item[0][0])[0][1]

    return np.array([endx, endy]) + off
    

def getInterest(img, sx, sy, pos):
    r, c = img.shape[:2]

    ignore = 400
    if pos == Pos.LEFT:
        offset = np.array([c // 2 + 15, ignore])
        img = img[offset[1]:sy, offset[0]:c-30]
    else:
        offset = np.array([0, ignore])
        img = img[offset[1]:sy, :c//2 - 15]
    return img, offset

body = cv2.imread("%s/body.png" % (os.path.dirname(sys.argv[0]),))
bodyGray = cv2.cvtColor(body, cv2.COLOR_RGB2GRAY)

if len(sys.argv) > 1:
    fname = sys.argv[1]
else:
    fname = getScreenShot()

img = cv2.imread(fname)
start = getStartPoint(img, body)
end = getStopPoint(img, 1)

ydiff = abs(end[1] - start[1]) ** 2
xdiff = abs(end[0] - start[0]) ** 2
dist = math.sqrt(xdiff + ydiff)

print(start, end, dist)

cv2.circle(img, (start[0], start[1]), 10, (255,0,0), 10)
cv2.circle(img, (end[0], end[1]), 10, (0,0,255), 10)
cv2.imwrite(fname + '-marked.png', getScaledImage(img, 0.4))

makeJump(dist)

