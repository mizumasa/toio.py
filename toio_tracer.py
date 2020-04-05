#!/usr/bin/env python
# -*- coding: utf-8 -*-
#auther: @_mizumasa

import os
import time
import numpy as np
from multiprocessing import Process
from math import sin,cos


SAMPLE_CODE="""
x = sin(t*0.1) * 50 + 350
y = cos(t*0.1) * 50 + 140
"""

class TOIO_TRACER:
    def __init__(self):
        self.active = False
        self.tracer = []
        self.num = 0
        self.fps_control = FPS_CONTROL()
        return
        
    def setup(self,toio_num):
        for i in range(toio_num):
            self.tracer.append(TRACER(i))
        self.num = toio_num
        print("setup tracer num="+str(toio_num))
        return
    

class TRACER:
    def __init__(self,cid):
        self.code = SAMPLE_CODE
        self.input = "t"
        #self.boundX = [270,420]
        #self.boundY = [70,230]
        self.boundX = [0,550]
        self.boundY = [0,550]
        self.t = 0
        self.t_offset = 0
        self.cid = cid
        self.speed = 0.5

    def set_speed(self,speed):
        self.speed = speed

    def set_time(self,t):
        self.t = t

    def set_time_offset(self,t):
        self.t_offset = t

    def set_code(self,code):
        try:
            t = 0
            i = self.cid
            exec(code)
            print("set code done (parametric equation)",code)
            self.code = code
            self.input = "t"
        except:
            try:
                x = 0
                i = self.cid
                exec(code)
                print("set code done",code)
                self.code = code
                self.input = "x"
            except:
                print("code error")

    def update(self):
        self.t += self.speed

    def get_pos(self):
        if self.input == "t":
            t = self.t + self.t_offset
            i = self.cid
            exec(self.code)
            return self.bound(x,y)
        if self.input == "x":
            x = self.t + self.t_offset
            i = self.cid
            exec(self.code)
            return self.bound(x,y)
    def bound(self,x,y):
        width_x = self.boundX[1] - self.boundX[0]
        _x = (x - self.boundX[0]) % (width_x * 2)
        if _x > width_x: _x = width_x*2 - _x
        width_y = self.boundY[1] - self.boundY[0]
        _y = (y - self.boundY[0]) % (width_y * 2)
        if _y > width_y: _y = width_y*2 - _y
        return _x + self.boundX[0] , _y + self.boundY[0]


class PID:
    def __init__(self,P=1.0, I=0.94, D=0.05):
        self.Kp = P
        self.Ki = I
        self.Kd = D
        self.clear()
        self.delta_time = 0.1
        self.windup_guard = 20.0
        self.osc = None
        self.num = 1
        self.limit = 90.0

    def clear(self):
        self.target = [0.0]
        self.PTerm = [0.0]
        self.ITerm = [0.0]
        self.DTerm = [0.0]
        self.last_error = [0.0]
        self.delta_time = 0.1
        self.windup_guard = 20.0

    def set_limit(self,l):
        self.limit = l

    def set_pid(self,P,I,D):
        self.Kp = P
        self.Ki = I
        self.Kd = D

    def setOscControler(self):
        from toio_osc import TOIO_OSC
        self.osc = TOIO_OSC()
        self.osc.workAsLocalServer(9000)
        self.osc.setup()
    def closeOscControler(self):
        if self.osc is not None:
            self.osc.kill()
    
    def updateParam(self):
        if self.osc is not None:
            param = self.osc.param
            if "p1" in param.keys():
                self.Kp = param["p1"] / 100.
            if "p2" in param.keys():
                self.Ki = param["p2"] / 100.
            if "p3" in param.keys():
                self.Kd = param["p3"] / 100.
            if "p4" in param.keys():
                self.delta_time = param["p4"] / 500.
            if "p5" in param.keys():
                self.windup_guard = param["p5"]

    def update(self,cid,value):
        if cid >= self.num:
            addnum = cid - self.num + 1
            self.target += [0.0,] * addnum
            self.PTerm += [0.0,] * addnum
            self.ITerm += [0.0,] * addnum
            self.DTerm += [0.0,] * addnum
            self.last_error += [0.0,] * addnum
            
        error = self.target[cid] - value
        delta_error = error - self.last_error[cid]  
        self.PTerm[cid] = self.Kp * error  #PTermを計算
        self.ITerm[cid] += error * self.delta_time  #ITermを計算

        if (self.ITerm[cid] > self.windup_guard):  #ITermが大きくなりすぎたとき様
            self.ITerm[cid] = self.windup_guard
        if(self.ITerm[cid] < -self.windup_guard):
           self.ITerm[cid] = -self.windup_guard
           
        self.DTerm[cid] = delta_error / self.delta_time  #DTermを計算
        self.last_error[cid] = error
        output = self.PTerm[cid] + (self.Ki * self.ITerm[cid]) + (self.Kd * self.DTerm[cid])
        output = min(self.limit,max(- self.limit,output))
        if self.osc is not None:
            print(output,"from PID",self.Kp,self.Ki,self.Kd,value)
        return output

class SPEED_BALANCER:
    def __init__(self,distance,speed):
        self.speed = speed
        self.distance = distance
    def update(self,distance):
        if self.distance > distance:
            self.speed -= 1
        else:
            self.speed += 1
        self.speed = min(max(self.speed,0),90)
        return int(self.speed)

class FPS_CONTROL:
    def __init__(self):
        self.count = 0
        self.log = []
        self.start = None
    def set_fps(self,fps):
        self.fps = fps
        self.spf = 1.0 / fps
    def update(self):
        self.count+=1
        if self.start is not None:
            self.log.append(time.time()-self.start)
        self.start = time.time()
        return
    def get_fps(self):
        if self.log == []:
            return None
        else:
            return 1 / np.average(self.log[-3:])
    def sleep(self):
        time.sleep(max(0,self.spf - time.time() + self.start))
        return

def main():
    return

if __name__ == '__main__':
    main()


