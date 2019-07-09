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

SERVICE_UUID = uuid.UUID('10B20100-5B3B-4571-9508-CF3EFCD7BBAE')
MOTOR_UUID = uuid.UUID('10B20102-5B3B-4571-9508-CF3EFCD7BBAE')

"""
import toio_util as tu
TT = tu.TOIO_COMMUNICATOR()
TT.start(50006)
def h(i):
    return hex(i)[2:].zfill(2)
for i in range(10,200,5):
    TT.send("0:0:010101"+h(i)+"0201"+h(i))
"""
class DEVICE:
    def __init__(self,obj):
        self.obj = obj
    def connect(self):
        print('Connecting to device...')
        self.obj.connect()
        print('Discovering services...')
        self.obj.discover([SERVICE_UUID], [MOTOR_UUID])
        self.uart = self.obj.find_service(SERVICE_UUID)
        self.chara_motor = self.uart.find_characteristic(MOTOR_UUID)
    def write_motor(self,commandStr):
        print("motor write command:{0}".format(commandStr))
        self.chara_motor.write_value(binascii.a2b_hex(commandStr))
    def disconnect(self):
        self.obj.disconnect()


class TOIO_COMMUNICATOR:
    def __init__(self):
        self.clear()
        self.vmode = False

    def clear(self):
        self.active = False
        self.end = False

    def noToio(self):
        self.vmode = True

    def stop(self):
        if self.active:
            self.send(b'_')
            self.s.close()
            self.p.join()
            self.active = False
            print("Process joined.")

    def start(self, num=1, port=50000):
        self.clear()
        self.socketPort = port
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

    def send(self,data):
        if self.active:
            self.conn.sendall(str(self.mid)+':'+data+',')
            loop = True
            while loop:
                recv = self.conn.recv(1024)
                m = message(recv,self.buf)
                for i in m:
                    self.log.append(i[1])
                    if self.mid == int(i[0]):
                        loop = False

    def ble_process(self):
        self.ble = Adafruit_BluefruitLE.get_provider()
        self.ble.initialize()
        self.ble.run_mainloop_with(self.ble_main)

    def ble_main(self):
        print("ble main start")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect(('127.0.0.1', self.socketPort))
        except:
            print("socket error (use another port)")
            return
        ble_buf = [""]

        adapter = self.ble.get_default_adapter()
        print('Using adapter: {0}'.format(adapter.name))

        print('Disconnecting any connected devices...')
        self.ble.disconnect_devices([SERVICE_UUID])

        found = False
        print('Searching device...')
        devices = []
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
                    devices.append(DEVICE(device))

        finally:
            adapter.stop_scan()

        if not found:
            if self.vmode:
                print("Virtual mode")
            else:
                print("switch on toio")
                s.close()
                return

        try:
            if found:
                for device in devices:
                    device.connect()

            count = 0
            while 1:

                recv = s.recv(1024)
                if b'_' in recv:
                    print(recv,"rect")
                    s.sendall(recv)
                    break
                m = message(recv,ble_buf)
                print('BLE Loop Receive: {0}'.format(repr(recv)))

                for i in m:
                    print(i)
                    s.sendall(i[0]+':'+i[1]+',')
                    if len(i)==4:
                        useId = int(i[1])
                        actionId = int(i[2])
                        commandStr = i[3]
                        if useId < len(devices):
                            if actionId == 0:#motor
                                devices[useId].write_motor(commandStr)

                if found and 0:
                    CommandStr = "01010164020164"
                    print('Move forward: {0}'.format(CommandStr))
                    self.device.write_motor(CommandStr)
                time.sleep(1)

        finally:
            if found:
                for device in devices:
                    device.disconnect()
            print("Disconnected")
            s.sendall(b'close')
            s.close()
            time.sleep(2)


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


