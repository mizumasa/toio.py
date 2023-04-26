# New Info!

Happily the official toio Python library has been published.
Please refer the official toio.py repository for further use. 

https://github.com/toio/toio.py


## toio.py (unofficial version)
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

## Update
20/3/28 turo_to コマンド追加
* Usage) T.turn_to(キューブID, 目標回転方向(0-360))
* clockオプションで回転方向指定可能
* デフォルト ease=True で目標近辺で減速する

20/3/28 move_to コマンド ease オプション追加
* Usage) T.move_to(キューブID, 目標X座標, 目標Y座標, ease=True) easeをTrueにすると止まる前に減速する  

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
