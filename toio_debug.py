#!/usr/bin/env python
# -*- coding: utf-8 -*-
#toio BLE sample (with Adafruit_BluefruitLE)
#auther: mizumasa

import os
import time
import numpy as np

CHAR = ['　','＊','｜','ー']

class TOIO_DEBUG:
    def __init__(self):
        self.boundX = [270,420]
        self.boundY = [70,230]
        self.boundX = [0,550]
        self.boundY = [0,550]
        self.windowW = 40
        self.windowH = 40
        self.map = np.zeros((self.windowH,self.windowW),dtype="uint8")
        self.log = []
    def clear(self):
        self.map *= 0
        self.log = []

    def point(self,x,y,value):
        posX = int(min(self.windowW - 1,self.windowW * (x - self.boundX[0]) / (self.boundX[1] - self.boundX[0])))
        posY = int(min(self.windowH - 1,self.windowH * (y - self.boundY[0]) / (self.boundY[1] - self.boundY[0])))
        self.map[posY,posX] = value

    def comment(self,comment):
        self.log.append(comment)

    def draw(self):
        os.system('clear')
        for i in range(self.windowH):
            line = ""
            for j in range(self.windowW):
                line += CHAR[self.map[i,j]]
            print(line)
        for i in self.log:
            print(i)

def main():
    return

if __name__ == '__main__':
    main()


