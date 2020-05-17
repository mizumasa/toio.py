#!/usr/bin/env python
# -*- coding: utf-8 -*-
#toio BLE sample (with Adafruit_BluefruitLE)
#auther: mizumasa

import sys
import toio
import numpy as np
import random

def main():
    T = toio.TOIO()
    T.connect()
    for i in range(4):
        T.turn_to(i,int(360*random.random()))
    for i in range(4):
        T.turn_to(i,int(360*random.random()))
    for i in range(4):
        T.turn_to(i,90)
    T.disconnect()
    return

if __name__ == '__main__':
    main()


