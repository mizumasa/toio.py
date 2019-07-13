#!/usr/bin/env python
# -*- coding: utf-8 -*-
#toio BLE sample (with Adafruit_BluefruitLE)
#auther: mizumasa

import binascii
from toio_config import *

################
#### MOTOR #####
################

def write_data_motor(l,r):
    assert -100 <= l and l<= 100
    assert -100 <= r and r<= 100
    l = int(l)
    r = int(r)
    return "0101{:02x}{:02x}02{:02x}{:02x}".format( (l<0)+1, abs(l), (r<0)+1, abs(r) )

def write_data_motor_timer(l,r,t):
    #l = -100 ~ 100
    #r = -100 ~ 100
    #t = 0 ~ 2550
    # time to stop (t ms)
    assert -100 <= l and l<= 100
    assert -100 <= r and r<= 100
    assert 0 <= t and t<= 2550
    l = int(l)
    r = int(r)
    t = int(t)
    return "0201{:02x}{:02x}02{:02x}{:02x}{:02x}".format( (l<0)+1, abs(l), (r<0)+1, abs(r), int(t/10) )

################
#### LIGHT #####
################

def hsv_to_rgb(h,s,v):
#    h = 0 ~ 360
#    s = 0 ~ 255
#    v = 0 ~ 255

    i = int(h / 60.0)
    mx = v
    mn = v - ((s / 255.0) * v)
    
    if h is None:
        return(0,0,0)
    
    if i == 0:
        (r1,g1,b1) = (mx,(h/60.0)*(mx-mn)+mn,mn)
    elif i == 1:
        (r1,g1,b1) = (((120.0-h)/60.0)*(mx-mn)+mn,mx,mn)
    elif i == 2:
        (r1,g1,b1) = (mn,mx,((h-120.0)/60.0)*(mx-mn)+mn)
    elif i == 3:
        (r1,g1,b1) = (mn,((240.0-h)/60.0)*(mx-mn)+mn,mx)
    elif i == 4:
        (r1,g1,b1) = (((h-240.0)/60.0)*(mx-mn)+mn,mn,mx)
    elif 5 <= i:
        (r1,g1,b1) = (mx,mn,((360.0-h)/60.0)*(mx-mn)+mn)

    return (int(r1), int(g1), int(b1))

def write_data_light(t,r,g,b):
    assert 0 <= t and t<= 2550
    assert 0 <= r and r<= 255
    assert 0 <= g and g<= 255
    assert 0 <= b and b<= 255
    t = int(t)
    r = int(r)
    g = int(g)
    b = int(b)
    return "03{:02x}0101{:02x}{:02x}{:02x}".format( int(t/10), r, g, b )

def write_data_light_seq(n,t1,r1,g1,b1,t2,r2,g2,b2):
    assert 0 <= n and n<= 255
    assert 0 <= t1 and t1<= 2550
    assert 0 <= r1 and r1<= 255
    assert 0 <= g1 and g1<= 255
    assert 0 <= b1 and b1<= 255
    assert 0 <= t2 and t2<= 2550
    assert 0 <= r2 and r2<= 255
    assert 0 <= g2 and g2<= 255
    assert 0 <= b2 and b2<= 255
    t1 = int(t1)
    r1 = int(r1)
    g1 = int(g1)
    b1 = int(b1)
    t2 = int(t2)
    r2 = int(r2)
    g2 = int(g2)
    b2 = int(b2)
    return "04{:02x}02{:02x}0101{:02x}{:02x}{:02x}{:02x}0101{:02x}{:02x}{:02x}".format( 
        n, int(t1/10), r1, g1, b1, int(t2/10), r2, g2, b2)

def write_data_light_off():
    return "01"

################
#### SOUND #####
################

def write_data_sound(sid,vol):
    assert 0 <= sid and sid<= 10
    assert 0 <= vol and vol<= 255
    return "02{:02x}{:02x}".format( sid, vol )

################
####   ID   ####
################

def get_data_id(data):
    l = hexD2list(data[2:])
    return {"cx":l[0],"cy":l[1],"cr":l[2],"sx":l[3],"sy":l[4],"sr":l[5]}

################
#### SENSOR ####
################

def get_data_sensor(data):
    l = hex2list(data)
    return {"slope":l[1],"collision":l[2]}

################
#### BUTTON ####
################

def get_data_button(data):
    l = hex2list(data)
    return {"button":l[1]}

################
#### BATTERY ###
################

def get_data_battery(data):
    l = hex2list(data)
    return {"battery":l[0]}


def hex2list(data):
    assert len(data) % 2 == 0
    out = []
    for i in range(0,len(data),2):
        out.append(int(data[i:i+2],16))
    return out

def hexD2list(data):
    assert len(data) % 4 == 0
    out = []
    for i in range(0,len(data),4):
        out.append(int(data[i+2:i+4]+data[i:i+2],16)) #Little Endian
    return out

def main():
    return

if __name__ == '__main__':
    main()


