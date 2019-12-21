#!/usr/bin/env python
# -*- coding: utf-8 -*-
#toio BLE sample (with Adafruit_BluefruitLE)
#auther: mizumasa

import sys
import time
import toio
import toio_osc

def main():
    T = toio.TOIO()
    C = toio_osc.TOIO_OSC()
    C.workAsLocalServer(7000)
    T.connect()
    T.write_data_light(0,0,255,0,0)
    C.setServerFunc("light",T.write_data_light)
    C.setup()
    buf = input()
    T.disconnect()
    C.kill()
    return

if __name__ == '__main__':
    main()


