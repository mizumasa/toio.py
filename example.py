#!/usr/bin/env python
# -*- coding: utf-8 -*-
#toio BLE sample (with Adafruit_BluefruitLE)
#auther: mizumasa

import sys
import time
import toio
import toio_message

def main(toio_num):
    T = toio.TOIO()
    #T.noToio(4)
    T.connect()
    toio_num = min(toio_num, T.toio_num)
    
    for i in range(toio_num):
        T.write_data_motor(i,100,0)
    time.sleep(1)

    for i in range(toio_num):
        print(T.get_data_id(i))
        print(T.get_data_sensor(i))
        print(T.get_data_button(i))
        print(T.get_data_battery(i))

    for i in range(toio_num):
        T.write_data_motor(i,0,100)
    time.sleep(1)

    for i in range(toio_num):
        T.write_data_motor(i,0,-100)
    time.sleep(1)

    for i in range(toio_num):
        T.write_data_motor(i,-100,0)
    time.sleep(1)

    for i in range(toio_num):
        T.write_data_motor(i,0,0)
        h = 360 * i / toio_num
        r,g,b = toio_message.hsv_to_rgb(h,255,255)
        T.write_data_light(i,0,r,g,b)
    time.sleep(1)

    for i in range(toio_num):
        T.write_data_motor(i,0,0)
        h = 360 * i / toio_num
        r,g,b = toio_message.hsv_to_rgb(h,255,255)
        T.write_data_light_seq(i,0,100,r,g,b,100,0,0,0)
    time.sleep(1)

    for i in range(toio_num):
        T.write_data_sound(i,i)
        time.sleep(1)

    T.disconnect()

    return

if __name__ == '__main__':
    print("[Usage] python toio_test.py 1~(n)")
    args = sys.argv
    toio_num = 1
    if len(args) > 1:
        toio_num = int(args[1])
    main(toio_num)


