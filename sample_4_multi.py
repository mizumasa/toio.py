#!/usr/bin/python
# -*- coding: utf-8 -*-
#toio BLE sample (with Adafruit_BluefruitLE)
#auther: mizumasa

import time
import uuid
import binascii
import Adafruit_BluefruitLE

SERVICE_UUID = uuid.UUID('10B20100-5B3B-4571-9508-CF3EFCD7BBAE')

MOTOR_UUID = uuid.UUID('10B20102-5B3B-4571-9508-CF3EFCD7BBAE')
LIGHT_UUID = uuid.UUID('10B20103-5B3B-4571-9508-CF3EFCD7BBAE')
SOUND_UUID = uuid.UUID('10B20104-5B3B-4571-9508-CF3EFCD7BBAE')

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

        ble.find_device(name="toio Core Cube")
        devices = ble.find_devices(service_uuids=[SERVICE_UUID])

        if devices is []:
            raise RuntimeError('Failed to find device!')
        else:
            for device in devices:
                print('Found device name: {0}'.format(device.name))
            if len(devices) != 2:
                raise RuntimeError('Use 2 toio cubes!')
    finally:
        # Make sure scanning is stopped before exiting.
        adapter.stop_scan()
    
    try:
        uarts = []
        chara_motor = []
        chara_light = []
        chara_sound = []

        for device in devices:
            print('Connecting to device...')
            device.connect()
            print('Discovering services...')
            device.discover([SERVICE_UUID], [MOTOR_UUID])

            # Find the service and its characteristics.
            uart = device.find_service(SERVICE_UUID)
            uarts.append(uart)
            chara_motor.append(uart.find_characteristic(MOTOR_UUID))
            chara_light.append(uart.find_characteristic(LIGHT_UUID))
            chara_sound.append(uart.find_characteristic(SOUND_UUID))

        time.sleep(0.5)
        CommandStr = "01010164020164"
        print('Move forward: {0}'.format(CommandStr))
        chara_motor[0].write_value(binascii.a2b_hex(CommandStr))
        chara_motor[1].write_value(binascii.a2b_hex(CommandStr))
        time.sleep(1)
        
        CommandStr = "02{:02x}FF".format(7)
        print('Sound: {0}'.format(CommandStr))
        chara_sound[0].write_value(binascii.a2b_hex(CommandStr))
        chara_sound[1].write_value(binascii.a2b_hex(CommandStr))
        
        CommandStr = "01010164020264"
        print('Turn: {0}'.format(CommandStr))
        chara_motor[0].write_value(binascii.a2b_hex(CommandStr))
        chara_motor[1].write_value(binascii.a2b_hex(CommandStr))
        time.sleep(1)

        CommandStr = "01010100020100"
        print('Stop: {0}'.format(CommandStr))
        chara_motor[0].write_value(binascii.a2b_hex(CommandStr))
        chara_motor[1].write_value(binascii.a2b_hex(CommandStr))

        CommandStr = "0400021E010100FF001E01010000FF"
        print('Light: {0}'.format(CommandStr))
        chara_light[0].write_value(binascii.a2b_hex(CommandStr))
        CommandStr = "0400021E0101FFFF001E0101FF00FF"
        chara_light[1].write_value(binascii.a2b_hex(CommandStr))

        CommandStr = "02{:02x}FF".format(5)
        print('Sound: {0}'.format(CommandStr))
        chara_sound[0].write_value(binascii.a2b_hex(CommandStr))
        chara_sound[1].write_value(binascii.a2b_hex(CommandStr))

        time.sleep(2)


    finally:
        for device in devices:
            device.disconnect()

if __name__=='__main__':
    ble = Adafruit_BluefruitLE.get_provider()
    ble.initialize()
    ble.run_mainloop_with(main)

