#!/usr/bin/env python
# -*- coding: utf-8 -*-
#toio BLE sample (with Adafruit_BluefruitLE)
#auther: mizumasa

import sys
import toio
import numpy as np

def main():
    T = toio.TOIO()
    T.connect()
    T.setup_tracer()
    SAMPLE_CODE="""
    x = sin(t*0.2) * 50 + 350
    y = cos(t*0.1) * 50 + 140
    """
    T.set_tracer_code(SAMPLE_CODE)
    T.set_tracer_time_offset(0)
    T.set_tracer_time_offset(np.pi*10/2,0)
    T.run_tracer_init(speed=30)

    T.set_tracer_speed(0.5)
    T.run_tracer(key_wait=True,fps= 10,debug=True,enableBack=False)
    T.disconnect()
    return

if __name__ == '__main__':
    main()


