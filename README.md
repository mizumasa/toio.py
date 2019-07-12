# toio.py
Library for controlling toio™Core Cube using Python

## Usage
```
>>> import toio
>>> T = toio.TOIO()
>>> T.connect()

>>> cubeID = 0
>>> T.write_data_motor(cubeID,100,0)
    
>>> r,g,b = 255,0,0
>>> T.write_data_light(cubeID,0,r,g,b)

>>> T.write_data_sound(cubeID,0)

>>> T.get_data_sensor(cubeID)
{'slope': 1, 'collision': 0}

>>> T.get_data_button(cubeID)
{'button': 128}

>>> T.disconnect()
```


## Requirement

* macOS (not supported on Windows or Linux)
* tested on macOS(10.14) python=2.7
* Adafruit Python BluefruitLE (Python library for BLE) https://github.com/adafruit/Adafruit_Python_BluefruitLE

## install

You need to install "Adafruit Python BluefruitLE"
Please look https://github.com/adafruit/Adafruit_Python_BluefruitLE

## Example
python example.py [number of cubes]


## Low Level API Example
| Name | Cube | Description |
| ----------- | ------------------ | ------ |
| sample_1_simple.py |1| Moving forward 1 second |
| sample_2_act.py |1| Test for moving, sound, and light|
| sample_3_sensor.py |1| Push button or shake cube |
| sample_4_multi.py |2| 2 cubes moving sample|


## Movie
https://twitter.com/_mizumasa/status/1146791049957789697
