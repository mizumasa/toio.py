#!/usr/bin/env python
# -*- coding: utf-8 -*-
#toio BLE sample (with Adafruit_BluefruitLE)
#auther: mizumasa

import os
import time
import numpy as np
import toio_util
import toio_message
from toio_config import *

class TOIO:
    def __init__(self):
        self.tc = toio_util.TOIO_COMMUNICATOR()
        self.active = False
        self.assign = {}
        self.assign_edited = False

    def noToio(self):
        if self.active:
            self.tc.noToio()
        return

    def connect(self, num=None, port=None):
        if not self.active:
            self.tc.connect(num, port)
            self.connect_num = num
            self.toio_num = self.get_connected_num()
            print("Connected num :{0}".format(self.toio_num))
            if num is not None and self.toio_num > num:
                print("Please change assign ( edit_assign() )")
            self.active = True
            for i in range(self.toio_num):
                self.assign[i] = i
        return 

    def disconnect(self):
        self.active = False
        return self.tc.disconnect()

    def disconnect_each(self, cid, not_change_assign = False):
        _cid = cid
        if not not_change_assign:
            _cid = self.assign[cid]
        cmd = "{0}:{1}:".format(_cid, MSG_ID_DISCONNECT)
        return self.send(cmd,False)

    def send(self, data, wait=True):
        return self.tc.send(data,wait=wait)

    ################
    #### MOTOR #####
    ################

    def write_data_motor(self,cid,l,r):
        _cid = self.assign[cid]
        cmd = "{0}:{1}:{2}".format(_cid, MSG_ID_MOTOR, toio_message.write_data_motor(l,r))
        return self.send(cmd,False)

    def write_data_motor_timer(self,cid,l,r,t):
        _cid = self.assign[cid]
        cmd = "{0}:{1}:{2}".format(_cid, MSG_ID_MOTOR, toio_message.write_data_motor_timer(l,r,t))
        return self.send(cmd,False)

    ################
    #### LIGHT #####
    ################

    def write_data_light(self,cid,t,r,g,b):
        _cid = self.assign[cid]
        cmd = "{0}:{1}:{2}".format(_cid, MSG_ID_LIGHT, toio_message.write_data_light(t,r,g,b))
        return self.send(cmd,False)

    def write_data_light_seq(self,cid,n,t1,r1,g1,b1,t2,r2,g2,b2):
        _cid = self.assign[cid]
        cmd = "{0}:{1}:{2}".format(_cid, MSG_ID_LIGHT, toio_message.write_data_light_seq(n,t1,r1,g1,b1,t2,r2,g2,b2))
        return self.send(cmd,False)

    def write_data_light_off(self,cid):
        _cid = self.assign[cid]
        cmd = "{0}:{1}:01".format(_cid, MSG_ID_LIGHT)
        return self.send(cmd,False)

    ################
    #### SOUND #####
    ################

    def write_data_sound(self,cid,sid,vol=255):
        _cid = self.assign[cid]
        cmd = "{0}:{1}:{2}".format(_cid, MSG_ID_SOUND, toio_message.write_data_sound(sid,vol))
        return self.send(cmd,False)

    ################
    ####   ID   ####
    ################

    def get_data_id(self,cid):
        _cid = self.assign[cid]
        cmd = "{0}:{1}:".format(_cid, MSG_ID_ID)
        return toio_message.get_data_id(self.send(cmd,True))

    ################
    #### SENSOR ####
    ################

    def get_data_sensor(self,cid):
        _cid = self.assign[cid]
        cmd = "{0}:{1}:".format(_cid, MSG_ID_SENSOR)
        return toio_message.get_data_sensor(self.send(cmd,True))

    ################
    #### BUTTON ####
    ################

    def get_data_button(self,cid):
        _cid = self.assign[cid]
        cmd = "{0}:{1}:".format(_cid, MSG_ID_BUTTON)
        return toio_message.get_data_button(self.send(cmd,True))

    ################
    #### BATTERY ###
    ################

    def get_data_battery(self,cid):
        _cid = self.assign[cid]
        cmd = "{0}:{1}:".format(_cid, MSG_ID_BATTERY)
        return toio_message.get_data_battery(self.send(cmd,True))

    ################
    #### OTHER  ####
    ################

    def get_connected_num(self):
        cmd = "{0}:{1}:".format(0, MSG_ID_TOIONUM)
        return int(self.send(cmd,True))


    def edit_assign(self):
        if self.assign_edited:
            print("Edit assign is allowed only once")
            return
        else:
            self.assign_edited = True
        if self.active and self.toio_num:
            for i in range(self.toio_num):
                h = 360 * i / self.toio_num
                r,g,b = toio_message.hsv_to_rgb(h,255,255)
                self.write_data_light(i,0,r,g,b)
                self.write_data_sound(i,0)
            time.sleep(1)
            setup_done = False
            while not setup_done:
                assign = []
                for i in range(self.toio_num):
                    h = 360 * i / self.toio_num
                    r,g,b = toio_message.hsv_to_rgb(h,255,255)
                    self.write_data_light_seq(i,0,500,r,g,b,500,0,0,0)
                    self.write_data_sound(i,1)
                    while 1:
                        print("Toio assign 0 ~ {0} (''=not assign):".format(self.toio_num-1))
                        key = raw_input()
                        try:
                            if key == "":
                                key = -1
                            else:
                                key = int(key)
                            if key >= self.toio_num:
                                continue
                            assign.append(key)
                            break
                        except:
                            print("Input error")
                    self.write_data_light(i,0,r,g,b)
                setup_done = self.set_assign(assign)
            time.sleep(0.5)
            for i in range(self.connect_num):
                self.write_data_light(i,0,0,0,0)
                self.write_data_sound(i,7)
        return

    def set_assign(self,assign):
        new_assign = {}
        if self.connect_num != np.sum(np.asarray(assign) >= 0):
            print("Invalid assign error (assign num)")
            return False
        for i in range(self.connect_num):
            if np.sum(np.asarray(assign) == i) != 1:
                print("Invalid assign error (duplicate)")
                return False
        for i in range(self.toio_num):
            if assign[i] == -1:
                self.disconnect_each(i, not_change_assign = True)
            else:
                new_assign[assign[i]] = i
        self.assign = new_assign
        return True

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


