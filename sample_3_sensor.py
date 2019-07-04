#!/usr/bin/python
# -*- coding: utf-8 -*-
#toio BLE sample (with Adafruit_BluefruitLE)
#auther: mizumasa

import time
import uuid
import binascii
import Adafruit_BluefruitLE

SERVICE_UUID = uuid.UUID('10B20100-5B3B-4571-9508-CF3EFCD7BBAE')

MOTION_UUID = uuid.UUID('10B20106-5B3B-4571-9508-CF3EFCD7BBAE')
BUTTON_UUID = uuid.UUID('10B20107-5B3B-4571-9508-CF3EFCD7BBAE')

def main():
    ble.clear_cached_data()
    adapter = ble.get_default_adapter()
    adapter.power_on()
    print('Using adapter: {0}'.format(adapter.name))

    print('Disconnecting any connected devices...')
    ble.disconnect_devices([SERVICE_UUID])

    print('Searching device...')
    try:
        adapter.start_scan()

        device = ble.find_device(name="toio Core Cube")
        if device is None:
            raise RuntimeError('Failed to find device!')
        else:
            print('Found device name: {0}'.format(device.name))
    finally:
        # Make sure scanning is stopped before exiting.
        adapter.stop_scan()

    print('Connecting to device...')
    device.connect()
    
    try:
        print('Discovering services...')
        device.discover([SERVICE_UUID], [MOTION_UUID])

        # Find the service and its characteristics.
        uart = device.find_service(SERVICE_UUID)
        chara_motion = uart.find_characteristic(MOTION_UUID)
        chara_button = uart.find_characteristic(BUTTON_UUID)

        def received(data):
            receivedStr = binascii.b2a_hex(data)
            print('Notify Received: {0}'.format(receivedStr))

        # Turn on notification of characteristics using the callback above.
        chara_button.start_notify(received)
        chara_motion.start_notify(received)

        for i in range(3):
            time.sleep(1)

            motionVal = chara_motion.read_value()
            receivedStr = binascii.b2a_hex(motionVal)
            print('Motion Read: {0}'.format(receivedStr))

            buttonVal = chara_button.read_value()
            receivedStr = binascii.b2a_hex(buttonVal)
            print('Button Read: {0}'.format(receivedStr))

        print('Waiting...')
        time.sleep(10)

    finally:
        device.disconnect()

if __name__=='__main__':
    ble = Adafruit_BluefruitLE.get_provider()
    ble.initialize()
    ble.run_mainloop_with(main)

