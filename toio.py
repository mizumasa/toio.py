#!/usr/bin/env python
# -*- coding: utf-8 -*-
#toio BLE sample (with Adafruit_BluefruitLE)
#auther: mizumasa

import os
import time
import toio_util
import toio_message
from toio_config import *

class TOIO:
    def __init__(self):
        self.tc = toio_util.TOIO_COMMUNICATOR()

    def noToio(self):
        return self.tc.noToio()

    def connect(self, num=1, port=50000):
        return self.tc.connect(num, port)

    def disconnect(self):
        return self.tc.disconnect()

    def send(self, data, wait=True):
        return self.tc.send(data,wait=wait)

    ################
    #### MOTOR #####
    ################

    def write_data_motor(self,cid,l,r):
        cmd = "{0}:{1}:{2}".format(cid, MSG_ID_MOTOR, toio_message.write_data_motor(l,r))
        return self.send(cmd,False)

    def write_data_motor_timer(self,cid,l,r,t):
        cmd = "{0}:{1}:{2}".format(cid, MSG_ID_MOTOR, toio_message.write_data_motor_timer(l,r,t))
        return self.send(cmd,False)

    ################
    #### LIGHT #####
    ################

    def write_data_light(self,cid,t,r,g,b):
        cmd = "{0}:{1}:{2}".format(cid, MSG_ID_LIGHT, toio_message.write_data_light(t,r,g,b))
        return self.send(cmd,False)

    def write_data_light_seq(self,cid,n,t1,r1,g1,b1,t2,r2,g2,b2):
        cmd = "{0}:{1}:{2}".format(cid, MSG_ID_LIGHT, toio_message.write_data_light_seq(n,t1,r1,g1,b1,t2,r2,g2,b2))
        return self.send(cmd,False)

    def write_data_light_off(self,cid):
        cmd = "{0}:{1}:01".format(cid, MSG_ID_LIGHT)
        return self.send(cmd,False)

    ################
    #### SOUND #####
    ################

    def write_data_sound(self,cid,sid,vol):
        cmd = "{0}:{1}:{2}".format(cid, MSG_ID_SOUND, toio_message.write_data_sound(sid,vol))
        print(cmd)
        return self.send(cmd,False)

    ################
    ####   ID   ####
    ################

    def get_data_id(self,cid):
        cmd = "{0}:{1}:".format(cid, MSG_ID_ID)
        return self.send(cmd,True)

    ################
    #### SENSOR ####
    ################

    def get_data_sensor(self,cid):
        cmd = "{0}:{1}:".format(cid, MSG_ID_SENSOR)
        return self.send(cmd,True)

    ################
    #### BUTTON ####
    ################

    def get_data_button(self,cid):
        cmd = "{0}:{1}:".format(cid, MSG_ID_BUTTON)
        return self.send(cmd,True)

    ################
    #### BATTERY ###
    ################

    def get_data_battery(self,cid):
        cmd = "{0}:{1}:".format(cid, MSG_ID_BATTERY)
        return self.send(cmd,True)


def main():
    toio = TOIO()
    #toio.noToio()
    toio.connect(1,50000)
    count = 0
    while 1:
        count += 1
        print("loop")
        time.sleep(1)
        toio.write_data_sound(0,count,255)
        if count > 9:
            break
    toio.disconnect()
    print("Finished")

if __name__ == '__main__':
    main()


