#! /usr/bin/python
import sys
sys.path.append(sys.path[0] + "/../")

from PyQt4.QtGui import QImage
from common.board import loadBoard

def calculateCenter(image):
    leftX = None
    for x in range(image.width()):
        for y in range(image.height()):
            if image.pixel(x, y) != 0:
                leftX = x
                break
        if leftX:
            break
    rightX = None
    for x in range(image.width() - 1, -1, -1):
        for y in range(image.height()):
            if image.pixel(x, y) != 0:
                rightX = x
                break
        if rightX:
            break
    topY = None
    for y in range(image.height()):
        for x in range(image.width()):
            if image.pixel(x, y) != 0:
                topY = y
                break
        if topY:
            break
    bottomY = None
    for y in range(image.height() - 1, -1, -1):
        for x in range(image.width()):
            if image.pixel(x, y) != 0:
                bottomY = y
                break
        if bottomY:
            break
    return [(rightX + leftX) / 2, (bottomY + topY) / 2]

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Please specify a board name."
    fileName = sys.argv[1]
    board = loadBoard(fileName)
    for t in board.territories.values():
        image = QImage(t.image)
        print t.name, calculateCenter(image)
