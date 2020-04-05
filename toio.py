#!/usr/bin/env python
# -*- coding: utf-8 -*-
#toio BLE sample (with Adafruit_BluefruitLE)
#auther: mizumasa

import os
import math
import time
import threading
import numpy as np
import toio_util
import toio_message
from toio_config import *
from toio_tracer import TOIO_TRACER, SPEED_BALANCER, FPS_CONTROL, PID
from toio_debug import TOIO_DEBUG

class TOIO:
    def __init__(self):
        self.tc = toio_util.TOIO_COMMUNICATOR()
        self.vmode = False
        self.active = False
        self.assign = {}
        self.assign_edited = False
        self.tracer = None
        self.pid = None

    def noToio(self,virtual_num = 1):
        self.tc.noToio()
        self.vmode = virtual_num
        return

    def connect(self, num=None, port=None,osc_control=False):
        if not self.active:
            self.tc.connect(num, port)
            self.connect_num = num
            self.toio_num = self.get_connected_num()
            print("Connected num :{0}".format(self.toio_num))
            if num is not None and self.toio_num > num:
                print("Please change assign ( edit_assign() )")
            self.active = True
            self.motor_pre = {}
            for i in range(self.toio_num):
                self.motor_pre[i] = [0,0]
                self.assign[i] = i
        self.pid = PID()
        if osc_control:
            self.pid.setOscControler()
        return 

    def disconnect(self):
        self.active = False
        self.pid.closeOscControler()
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
    def stop(self,cid):
        self.write_data_motor(cid,0,0)

    def write_data_motor(self,cid,l,r):
        self.motor_pre[cid][0] = l
        self.motor_pre[cid][1] = r
        _cid = self.assign[cid]
        cmd = "{0}:{1}:{2}".format(_cid, MSG_ID_MOTOR, toio_message.write_data_motor(l,r))
        return self.send(cmd,False)

    def write_data_motor_smooth(self,cid,l,r):
        _cid = self.assign[cid]
        d = 30
        for i in range(d):
            ll = (0. + l * (i + 1) + self.motor_pre[cid][0] * (d - 1 - i))/ d
            rr = (0. + r * (i + 1) + self.motor_pre[cid][1] * (d - 1 - i))/ d
            cmd = "{0}:{1}:{2}".format(_cid, MSG_ID_MOTOR, toio_message.write_data_motor(ll,rr))
            print(cmd)
            if i == (d - 1):
                self.motor_pre[cid][0] = l
                self.motor_pre[cid][1] = r
                return self.send(cmd,False)
            self.send(cmd,False)
            time.sleep(0.01)

    def write_data_motor_timer(self,cid,l,r,t):
        self.motor_pre[cid][0] = l
        self.motor_pre[cid][1] = r
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
        if self.vmode:return None
        _cid = self.assign[cid]
        cmd = "{0}:{1}:".format(_cid, MSG_ID_ID)
        return toio_message.get_data_id(self.send(cmd,True))

    ################
    #### SENSOR ####
    ################

    def get_data_sensor(self,cid):
        if self.vmode:return None
        _cid = self.assign[cid]
        cmd = "{0}:{1}:".format(_cid, MSG_ID_SENSOR)
        return toio_message.get_data_sensor(self.send(cmd,True))

    ################
    #### BUTTON ####
    ################

    def get_data_button(self,cid):
        if self.vmode:return None
        _cid = self.assign[cid]
        cmd = "{0}:{1}:".format(_cid, MSG_ID_BUTTON)
        return toio_message.get_data_button(self.send(cmd,True))

    ################
    #### BATTERY ###
    ################

    def get_data_battery(self,cid):
        if self.vmode:return None
        _cid = self.assign[cid]
        cmd = "{0}:{1}:".format(_cid, MSG_ID_BATTERY)
        return toio_message.get_data_battery(self.send(cmd,True))

    ################
    ### FUNCTION  ##
    ################

    def move_to(self,cid,x,y,speed = 80,thr = 50,ease=True,enableBack=False,key_wait = False):
        if key_wait:
            th = threading.Thread(target=wait_input)
            th.start()
        while not key_wait or input_flag:
            cPos = self.get_data_id(cid)
            if cPos is None:return
            cPos["diffX"] = x - cPos["cx"]
            cPos["diffY"] = y - cPos["cy"]
            distance = math.sqrt(cPos["diffX"]**2 + cPos["diffY"]**2)
            if distance < thr:
                self.stop(cid)
                return
            if ease:
                _speed = self.easing(distance,speed,50)
            else:
                _speed = speed
            self.move_step(cid,cPos,_speed,enableBack)
        if key_wait:
            self.stop(cid)
            th.join()

    def move_step(self,cid,pos,speed,enableBack):
        back = False
        relAngle = (math.atan2(pos["diffY"], pos["diffX"]) * 180) / math.pi - pos["cr"]
        relAngle = relAngle % 360
        if relAngle < -180:
            relAngle += 360
        elif relAngle > 180:
            relAngle -= 360
        if enableBack and relAngle>90:
            back = True
            relAngle = relAngle - 180
        if enableBack and relAngle<-90:
            back = True
            relAngle = relAngle + 180
        f = self.pid.update(cid,relAngle)
        ratio = 1 - (abs(f) / 90.)
        if back:
            if f < 0:
                self.write_data_motor(cid, - speed * ratio, - speed)
            else:
                self.write_data_motor(cid, - speed, - speed * ratio)
        else:
            if f < 0:
                self.write_data_motor(cid, speed, speed * ratio)
            else:
                self.write_data_motor(cid, speed * ratio, speed)


    def turn_to(self,cid,r,clock = None,speed = 80,thr = 3,ease=True):
        while 1:
            cPos = self.get_data_id(cid)
            if cPos is None:return
            diffR = (r - cPos["cr"])%360
            if diffR > 180:
                direction = -1
                dist = 360 - diffR
            else:
                direction = 1
                dist = diffR
            if clock is True:
                direction = 1
                dist = diffR
            if clock is False:
                direction = -1
                dist = 360 - diffR
            if dist < thr:
                self.stop(cid)
                return
            if ease:
                _speed = self.easing(dist,speed) * direction
            else:
                _speed = speed * direction
            self.write_data_motor(cid, _speed, - _speed)

    def easing(self,value,speed,max_value = 180.0):
        #change speed with value (slow to stop)
        MIN_SPEED = 10
        ratio = min(1,value/max_value)
        return int(MIN_SPEED + (speed - MIN_SPEED)*ratio)

    #####################
    ### Trace Function ##
    #####################

    def setup_tracer(self):
        if not self.active:return
        if self.tracer is None:
            self.tracer = TOIO_TRACER()
            self.tracer.setup(self.get_connected_num())

    def set_tracer_code(self,code,cid=None):
        if cid is None:
            for i in self.tracer.tracer:
                i.set_code(code)
        else:
            self.tracer.tracer[cid].set_code(code)
        return

    def set_tracer_time_offset(self,t,cid=None):
        if cid is None:
            for i in self.tracer.tracer:
                i.set_time_offset(t)
        else:
            self.tracer.tracer[cid].set_time_offset(t)
        return

    def set_tracer_speed(self,speed,cid=None):
        if cid is None:
            for i in self.tracer.tracer:
                i.set_speed(speed)
        else:
            self.tracer.tracer[cid].set_speed(speed)
        return

    def run_tracer_init(self, key_wait=False, speed = 80,thr = 5):
        for i in self.tracer.tracer:
            i.set_time(0)
        status = np.ones(self.tracer.num)
        if key_wait:
            th = threading.Thread(target=wait_input)
            th.start()
        while not key_wait or input_flag:
            if max(status) == 0:break
            print(status)
            for cid,j in enumerate(self.tracer.tracer):
                if status[cid]:
                    x,y = j.get_pos()
                    print(x,y)
                    cPos = self.get_data_id(cid)
                    print(cPos)
                    if cPos is None:continue
                    cPos["diffX"] = x - cPos["cx"]
                    cPos["diffY"] = y - cPos["cy"]
                    distance = math.sqrt(cPos["diffX"]**2 + cPos["diffY"]**2)
                    if distance < thr:
                        self.stop(cid)
                        status[cid] = 0
                        continue
                    self.move_step(cid,cPos,self.easing(distance,speed,thr),True)
        if key_wait:
            for cid,j in enumerate(self.tracer.tracer):
                self.stop(cid)
            th.join()
        return

    def run_tracer(self, key_wait=False, speed = 30, follow_distance = 20, thr = 5, fps = None, debug = False, balance_speed = True, enableBack = True, test=False):
        if self.tracer is None:
            print("setup tracer")
            return
        if test and fps==None:
            print("use fps option when to use test option")
            return
        if fps is not None:
            self.tracer.fps_control.set_fps(fps)
        if key_wait:
            th = threading.Thread(target=wait_input)
            th.start()
        if debug:window = TOIO_DEBUG()
        if balance_speed:
            balancer = []
            for cid,j in enumerate(self.tracer.tracer):
                balancer.append(SPEED_BALANCER(follow_distance,speed))
        while not key_wait or input_flag:
            self.pid.updateParam()
            self.tracer.fps_control.update()
            if debug:window.clear()
            for cid,j in enumerate(self.tracer.tracer):
                j.update()
                x,y = j.get_pos()
                if debug:window.point(x,y,1)
                cPos = self.get_data_id(cid)
                if cPos is None:continue
                cPos["diffX"] = x - cPos["cx"]
                cPos["diffY"] = y - cPos["cy"]
                distance = math.sqrt(cPos["diffX"]**2 + cPos["diffY"]**2)
                if balance_speed:
                    _speed = balancer[cid].update(distance)
                else:
                    if distance < thr:
                        self.stop(cid)
                        continue
                    _speed = self.easing(distance,speed,thr)
                if debug:window.comment('[{}]({},{}) -> ({},{}), speed = {}'.format(cid,cPos["cx"],cPos["cy"],x,y,_speed))
                if not test:self.move_step(cid,cPos,_speed,enableBack)
            if debug:window.comment('FPS = {}'.format(self.tracer.fps_control.get_fps()))
            if debug:window.draw()
            if fps is not None:self.tracer.fps_control.sleep()
        if key_wait:
            for cid,j in enumerate(self.tracer.tracer):
                self.stop(cid)
            th.join()



    ################
    #### OTHER  ####
    ################

    def get_connected_num(self):
        if self.vmode:return self.vmode
        cmd = "{0}:{1}:".format(0, MSG_ID_TOIONUM)
        return int(self.send(cmd,True))


    def edit_assign(self):
        if self.vmode:return
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

input_flag = True
def wait_input():
    global input_flag
    input_flag = True
    raw_input()
    input_flag = False

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


