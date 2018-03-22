#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime
from time import sleep
import durham_localized
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

# only want to update weather once an hour (500/day API limit)
second_counter = 0
while 1:
    # GoTriangle API Usage Limit: unknown!
    if (second_counter % 60) == 0:
        current_time = datetime.now()
        current_hour = current_time.hour
        current_minute = str(current_time.minute)
        if len(current_minute) == 1:
            current_minute = '0' + current_minute
        try:
            next_bus, bus_number, stop_code = durham_localized.update_gotriangle(stop_id="4049762", route_id="4000088")
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
                    (bus_number, next_bus, current_hour, current_minute, current_temp, conditions_today))

#    if (current_hour >= 6 and current_hour <= 9) and (current_minute == 0 or current_minute == 30) and error_check == 0:
#        result = update_result(current_temp, high_today, conditions_today, wind, trip_time_bus, trip_time_subway)
#        move_servo(result)
    second_counter = (second_counter + 60) % 86400
    sleep(60)
