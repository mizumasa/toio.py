#!/usr/bin/env python
# -*- coding: utf-8 -*-
#toio BLE sample (with Adafruit_BluefruitLE)
#auther: mizumasa

import os
import time
import socket
from multiprocessing import Process

import uuid
import binascii
import Adafruit_BluefruitLE
import toio_message
from toio_config import *

"""
LOW LEVEL UTIL

import toio_util as tu
TT = tu.TOIO_COMMUNICATOR()
TT.connect(1,50000)
for i in range(10,200,5):
    cmd = "010101{:02x}0201{:02x}".format(i,i)
    TT.send("0:2:"+cmd)
"""

class DEVICE:
    def __init__(self,obj):
        self.obj = obj
        self.notify = []
        self.active = False
    def connect(self):
        print('Connecting to device...')
        self.obj.connect()
        print('Discovering services...')
        self.obj.discover([SERVICE_UUID], [MOTOR_UUID])
        self.uart = self.obj.find_service(SERVICE_UUID)
        self.chara_motor = self.uart.find_characteristic(MOTOR_UUID)
        self.chara_light = self.uart.find_characteristic(LIGHT_UUID)
        self.chara_sound = self.uart.find_characteristic(SOUND_UUID)
        self.chara_id = self.uart.find_characteristic(ID_UUID)
        self.chara_sensor = self.uart.find_characteristic(SENSOR_UUID)
        self.chara_button = self.uart.find_characteristic(BUTTON_UUID)
        self.chara_battery = self.uart.find_characteristic(BATTERY_UUID)
        self.chara_config = self.uart.find_characteristic(CONFIG_UUID)
        self.chara_sensor.start_notify(self.notify_sensor)
        self.chara_button.start_notify(self.notify_button)
        self.active = True

    def write_motor(self,commandStr):
        if DEBUG:print("motor write command:{0}".format(commandStr))
        self.chara_motor.write_value(binascii.a2b_hex(commandStr))
    def write_light(self,commandStr):
        if DEBUG:print("light write command:{0}".format(commandStr))
        self.chara_light.write_value(binascii.a2b_hex(commandStr))
    def write_sound(self,commandStr):
        if DEBUG:print("sound write command:{0}".format(commandStr))
        self.chara_sound.write_value(binascii.a2b_hex(commandStr))

    def read_id(self):
        idVal = self.chara_id.read_value()
        receivedStr = binascii.b2a_hex(idVal)
        if DEBUG:print('sensor Read: {0}'.format(receivedStr))
        return receivedStr
    def read_sensor(self):
        sensorVal = self.chara_sensor.read_value()
        receivedStr = binascii.b2a_hex(sensorVal)
        if DEBUG:print('sensor Read: {0}'.format(receivedStr))
        return receivedStr
    def read_button(self):
        buttonVal = self.chara_button.read_value()
        receivedStr = binascii.b2a_hex(buttonVal)
        if DEBUG:print('Button Read: {0}'.format(receivedStr))
        return receivedStr
    def read_battery(self):
        batteryVal = self.chara_battery.read_value()
        receivedStr = binascii.b2a_hex(batteryVal)
        if DEBUG:print('Battery Read: {0}'.format(receivedStr))
        return receivedStr
    def read_config(self):
        configVal = self.chara_config.read_value()
        receivedStr = binascii.b2a_hex(configVal)
        if DEBUG:print('Config Read: {0}'.format(receivedStr))
        return receivedStr
    def disconnect(self):
        if self.active == True:
            self.obj.disconnect()
            self.active = False

    def notify_sensor(self,data):
        receivedStr = binascii.b2a_hex(data)
        if DEBUG:print('sensor Notify Received: {0}'.format(receivedStr))
        self.notify.append({"sensor":receivedStr})
    def notify_button(self,data):
        receivedStr = binascii.b2a_hex(data)
        if DEBUG:print('Button Notify Received: {0}'.format(receivedStr))
        self.notify.append({"button":receivedStr})

    def read_notify(self):
        return self.notify


class TOIO_COMMUNICATOR:
    def __init__(self):
        self.clear()
        self.vmode = False
        self.port = 50000

    def clear(self):
        self.active = False
        self.end = False

    def noToio(self):
        self.vmode = True

    def disconnect(self):
        if self.active:
            self.send(b'_')
            self.s.close()
            self.p.join()
            self.active = False
            print("Process joined.")

    def connect(self, num = None, port = None):
        self.clear()
        self.socketPort = self.port
        if port is not None:
            self.socketPort = port
        self.port += 1
        self.connectNum = num
        self.p = Process(target=self.ble_process)
        self.p.start()
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except:
            print("start server error")
            return
        print('start : port: {}'.format(self.socketPort))
        self.s.bind(('127.0.0.1', self.socketPort))
        self.s.listen(1)
        self.buf = [""]
        self.conn, self.addr = self.s.accept()
        self.active = True
        self.mid = 0
        self.log = []
        return

    def send(self, data, wait=True):
        if self.active:
            self.conn.sendall(str(self.mid)+':'+data+',')
            if not wait:
                self.mid += 1
                return None
            loop = True
            while loop:
                recv = self.conn.recv(1024)
                m = message(recv,self.buf)
                for i in m:
                    self.log.append(i)
                    try:
                        if self.mid == int(i[0]):
                            loop = False
                    except:
                        print("error ",i)
            self.mid += 1
            return i[1]
        return None

    def ble_process(self):
        self.ble = Adafruit_BluefruitLE.get_provider()
        self.ble.initialize()
        self.ble.run_mainloop_with(self.ble_main)

    def ble_main(self):
        print("BLE main start")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect(('127.0.0.1', self.socketPort))
        except:
            print("Socket error (use another port)")
            return
        ble_buf = [""]

        adapter = self.ble.get_default_adapter()
        print('Using adapter: {0}'.format(adapter.name))

        print('Disconnecting any connected devices...')
        self.ble.disconnect_devices([SERVICE_UUID])

        found = False
        print('Searching device...')
        self.devices = []
        try:
            adapter.start_scan()
            self.ble.find_device(name="toio Core Cube",timeout_sec=3)
            deviceList = self.ble.find_devices(service_uuids=[SERVICE_UUID])
            if len(deviceList) == 0:
                print("Failed to find device!")
            else:
                found = True
                print('Detect num: {0}'.format(len(deviceList)))
                for device in deviceList:
                    print('Found device name: {0}'.format(device.name))
                    self.devices.append(DEVICE(device))

        finally:
            adapter.stop_scan()
        
        if not found:
            if self.vmode:
                print("Virtual mode")
            else:
                print("Switch on toio")
                s.close()
                return

        try:
            if found:
                for device in self.devices:
                    device.connect()

            count = 0
            while 1:    

                recv = s.recv(1024)
                if b'_' in recv:
                    if DEBUG:print(recv,"rect")
                    s.sendall(recv)
                    break
                m = message(recv,ble_buf)
                if DEBUG:print('BLE Loop Receive: {0}'.format(repr(recv)))

                for i in m:
                    if DEBUG:print(i)
                    ret = ""
                    if len(i)==4:
                        cubeId = int(i[1])
                        actionId = int(i[2])
                        commandStr = i[3]
                        if cubeId < len(self.devices) and self.devices[cubeId].active:
                            if actionId == MSG_ID_MOTOR:
                                self.devices[cubeId].write_motor(commandStr)
                            if actionId == MSG_ID_LIGHT:
                                self.devices[cubeId].write_light(commandStr)
                            if actionId == MSG_ID_SOUND:
                                self.devices[cubeId].write_sound(commandStr)
                            if actionId == MSG_ID_ID:
                                ret = self.devices[cubeId].read_id()
                            if actionId == MSG_ID_SENSOR:
                                ret = self.devices[cubeId].read_sensor()
                            if actionId == MSG_ID_BUTTON:
                                ret = self.devices[cubeId].read_button()
                            if actionId == MSG_ID_BATTERY:
                                ret = self.devices[cubeId].read_battery()
                            if actionId == MSG_ID_CONFIG:
                                ret = self.devices[cubeId].read_config()
                            if actionId == MSG_ID_NOTIFY:
                                ret = str(self.devices[cubeId].read_notify()).replace(":","^")
                            if actionId == MSG_ID_TOIONUM:
                                ret = str(len(self.devices))
                            if actionId == MSG_ID_DISCONNECT:
                                self.devices[cubeId].disconnect()
                                
                    s.sendall(i[0]+':'+ret+',')

        finally:
            if found:
                for device in self.devices:
                    device.disconnect()
            print("Disconnected")
            s.close()
            time.sleep(1)


def message(data, buf):
    buf[0] += data
    out = []
    while 1:
        ret = buf[0].find(',')
        if ret >= 0:
            out.append(buf[0][:ret].split(":"))
            buf[0] = buf[0][ret+1:]
        else:
            break
    return out

def main():
    toio = TOIO_COMMUNICATOR()
    toio.noToio()
    toio.connect()
    count = 0
    while 1:
        count += 1
        print("loop")
        time.sleep(1)
        toio.send("aaaaaaa")
        if count > 10:
            break
    toio.stop()
    print("Finished")


if __name__ == '__main__':
    main()


