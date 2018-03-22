#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
from time import sleep
import os
import numpy as np
import durham_localized
import generate_transit_data
#from subprocess import *
import Adafruit_CharLCD as LCD

# Raspberry Pi LCD pin configuration:
lcd_rs        = 27
lcd_en        = 22
lcd_d4        = 25
lcd_d5        = 24
lcd_d6        = 23
lcd_d7        = 17 # changed to 17 to accommodate servo on 18
lcd_backlight = 4

# Define LCD column and row size for 16x2 LCD.
lcd_columns = 16
lcd_rows = 2

# Initialize the LCD using the pins above.
lcd = LCD.Adafruit_CharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7,
                           lcd_columns, lcd_rows, lcd_backlight)

# create the degree symbol, use with \x01F
lcd.create_char(1, [12, 18, 18, 12, 0, 0, 0, 0])

# initialize servo
p = LCD.PWM.get_platform_pwm()

# putting this function here because this program already imports GPIO from Adafruit_GPIO
def move_servo(angle):
    # input is 0-100, converted to 0-180, then to 2.5-20.5
    # yeah it makes no sense i don't know where 2.5-20.5 came from
    # but it works sooo :)
    p.start(18, 20.5, 100)
    angle *= 1.8
    sleep(1)
    duty = float(angle) / 10.0 + 2.5
    p.set_duty_cycle(18, duty)
    sleep(1)
    p.stop(18)

conditions_today, current_temp, high_today, wind = durham_localized.update_weather()

# servo test
#while True:
#    move_servo(0)
#    move_servo(50)
#    move_servo(100)
# iterable BUS_LIST allows button press to cycle through buses.
# STOP_DICT calls an iterable list of stops for each bus (given by BUS_LIST)
# consider loading all data pertaining to all routes and stops
# and then have a pick list, picked_stops = [], or picked_routes = []
# then only use those in the active lookups
# user input: manually enter agencies, route names and stops that you are interested in
AGENCIES = ["12", "24"]
BUS_PICK_LIST = ["5", "800", "805", "100", "105"]
STOP_PICK_LIST = ["5517", "5020", "5363", "1175"]

cwd = os.getcwd()
if not os.path.exists(cwd + '\\route_info.csv'):
    generate_transit_data.generate_transit_data(AGENCIES)
route_list = []
f = open("route_info.csv", "r")
for route in f:
    route_list.append(route)
f.close()

stop_list = []
f = open("stop_info.csv", "r")
for stop in f:
    stop_list.append(stop)
f.close()

STOP_DICT2 = {}
# incorporate numpy so the header row is ignored in this loop
for route in route_list:
    STOP_DICT2[route[0]] = route[3:]

# i should generate these with code rather than typing it all out
# use the lists generated from the csv files
# end goal is one dictionary that looks like STOP_DICT below, where the route is the key
# and the stops are the values. Also, each key and value is a list-pair tying the
# common name to the ID
BUS_LIST = [["4000088","5"], ["4003038","14"], ["4009216","100"], ["4009218","105"],
            ["4009224","300"], ["4009222","301"], ["4009226","305"], ["4009228","311"],
            ["4009242","700"], ["4009252","800"], ["4009244","805"]]
STOP_DICT = {["4000088","5"]: [["4213502","5517"], ["4049762","5020"]],
             ["4003038","14"]: [],
             ["4009216","100"]: [],
             ["4009218","105"]: [],
             ["4009224","300"]: [],
             ["4009222","301"]: [],
             ["4009226","305"]: [],
             ["4009228","311"]: [],
             ["4009242","700"]: [],
             ["4009252","800"]: [["4213502","5517"], ["4049762","5020"], ["4050718","5363"], ["4049498","1175"]],
             ["4009244","805"]: [["4213502","5517"], ["4049762","5020"], ["4050718","5363"], ["4049498","1175"]]}
#BUS_INFO = {"routes": {"4000088": "5", "4003038": "14", "4009216": "100", "4009218": "105",
#                       "4009224": "300", "4009222": "301", "4009226": "305", "4009228": "311",
#                       "4009242": "700", "4009252": "800", "4009244": "805"},
#            "stops": {"4213502": "5517", "4049762": "5020", "4050718": "5363", "4049498": "1175"}
#            }
#BUS_INFO2 = {"routes": [["4000088","5"], ["4003038","14"], ["4009216","100"], ["4009218","105"],
#                       ["4009224","300"], ["4009222","301"], ["4009226","305"], ["4009228","311"],
#                       ["4009242","700"], ["4009252","800"], ["4009244","805"]],
#            "stops": [["4213502","5517"], ["4049762","5020"], ["4050718","5363"], ["4049498","1175"]]}

# only want to update weather once an hour (500/day API limit)
second_counter = 0
button1 = 10 # 10 is 805
button2 = 0 # 0 is 5517
# initialize info
route_id = BUS_PICK_LIST[button1]
#route_name = BUS_LIST[button1]
# need to step through stops in the route_info.csv
stop_id = STOP_PICK_LIST[button2]
#stop_name = STOP_DICT[route_name][button2]

while 1:
#    # code for button presses
#    if button1_is_pressed:
#        button1 = (button1 + 1) % len(BUS_LIST)
#        route_id = BUS_LIST[button1][0]
#        route_name = BUS_LIST[button1][1]
#        # reset stop list
#        button2 = 0
#        stop_id = STOP_DICT[route_name][button2][0]
#        stop_name = STOP_DICT[route_name][button2][1]
#    if button2_is_pressed:
#        button2 = (button2 + 1) % len(STOP_DICT[route_name])
#        stop_id = STOP_DICT[route_name][button2][0]
#        stop_name = STOP_DICT[route_name][button2][1]

    # GoTriangle API Usage Limit: unknown!
    if (second_counter % 60) == 0:
        current_time = datetime.now()
        current_hour = current_time.hour
        current_minute = str(current_time.minute)
        if len(current_minute) == 1:
            current_minute = '0' + current_minute
        try:
            next_bus = durham_localized.update_gotriangle(stop_id, route_id,
                                                          current_hour, current_minute)
            bus_error = 0
        except:
            bus_error += 1
            if bus_error == 1:
                last_hour = current_hour
                last_minute = current_minute

    # WUnderground API Usage Limit: 500/day, 10/minute
    if (second_counter % 360) == 0:
        try:
            conditions_today, current_temp, high_today, wind = durham_localized.update_weather()
            weather_error = 0
        except:
            weather_error += 1

    lcd.clear()

    if bus_error > 0 and weather_error == 0:
        lcd.message('NO BUS %d:%s\n%d\x01F %s' % (current_hour, current_minute, current_temp, conditions_today))
    elif weather_error > 0 and bus_error == 0:
        lcd.message("Bus: %dm %d:%s\nNO WEATHER DATA" % (next_bus, current_hour, current_minute))
    elif weather_error > 0 and bus_error > 0:
        lcd.message("NO BUS %d:%s\nNO WEATHER DATA" % (current_hour, current_minute))
    elif type(next_bus) == str:
        lcd.message("%s %d:%s\n%d\x01F %s" % (next_bus, current_hour, current_minute, current_temp, conditions_today))
    else:
        # \x01F is the marker for the degree symbol created earlier
        lcd.message("%s: %dm %d:%s\n%d\x01F %s" %
                    (route_name, next_bus, current_hour, current_minute, current_temp, conditions_today))

#    if (current_hour >= 6 and current_hour <= 9) and (current_minute == 0 or current_minute == 30) and error_check == 0:
#        result = update_result(current_temp, high_today, conditions_today, wind, trip_time_bus, trip_time_subway)
#        move_servo(result)
    second_counter = (second_counter + 60) % 86400
    sleep(60)
