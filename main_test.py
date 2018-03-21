# -*- coding: utf-8 -*-
"""
Created on Tue Mar 20 08:10:46 2018

@author: bw5177
"""

# test bike clock program with stdout rather than LCD screen
from __future__ import print_function
from datetime import datetime
from time import sleep
import durham_localized

# use second_counter to decide when to update certain things
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

    if bus_error > 0 and weather_error == 0:
        print('NO BUS %d:%s\n%d deg %s' % (current_hour, current_minute, current_temp, conditions_today))
    elif weather_error > 0 and bus_error == 0:
        print("Bus: %dm %d:%s\nNO WEATHER DATA" % (next_bus, current_hour, current_minute))
    elif weather_error > 0 and bus_error > 0:
        print("NO BUS %d:%s\nNO WEATHER DATA" % (current_hour, current_minute))
    elif type(next_bus) == str:
        print("%s %d:%s\n%d deg %s" % (next_bus, current_hour, current_minute, current_temp, conditions_today))
    else:
        # \x01F is the marker for the degree symbol created earlier
        print("%s ARR: %dm %d:%s -- %d deg %s" %
                    (bus_number, next_bus, current_hour, current_minute, current_temp, conditions_today), end='\r')

#    if (current_hour >= 6 and current_hour <= 9) and (current_minute == 0 or current_minute == 30) and error_check == 0:
#        result = update_result(current_temp, high_today, conditions_today, wind, trip_time_bus, trip_time_subway)
#        move_servo(result)
    second_counter = (second_counter + 1) % 86400
    sleep(1)
