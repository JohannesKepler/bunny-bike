# -*- coding: utf-8 -*-
"""
Created on Tue Mar 20 08:10:46 2018

@author: bw5177
"""

# test bike clock program with stdout rather than LCD screen
# look up:
# http://raspi.tv/2013/how-to-use-interrupts-with-python-on-the-raspberry-pi-and-rpi-gpio
from datetime import datetime
from time import sleep
import os, sys
import durham_localized
import generate_transit_data

if 'win' in sys.platform:
    path_marker = '\\'
else:
    path_marker = '/'

# customize with your local data. use transloc or google maps or OpenAPI
# to get the codes for agencies, routes, and stops
AGENCIES = ["12", "24"]
BUS_PICK_LIST = ["5", "800", "805", "100", "105"]
STOP_PICK_LIST = ["5517", "5020", "5363", "1175", "1000", "1187", "8586"]

cwd = os.getcwd()
if not os.path.exists(cwd + path_marker + 'route_info.csv'):
    generate_transit_data.generate_route_data(AGENCIES)

# create route list from csv.
route_dict = {}
f = open("route_info.csv", "r")
for route in f:
    if route[0:8] == "Route ID":
        continue
    route_split = route.split(',')
    route_dict[route_split[0]] = route_split[1:]
    #route_list[-1][0] = [route_list[-1][0]]
    #route_list[-1][0].append(route_list[-1][1])
f.close()

# create stop list from csv
stop_dict = {}
f = open("stop_info.csv", "r")
for stop in f:
    if stop[0:7] == "Stop ID":
        continue
    stop_split = stop.split(',')
    stop_dict[stop_split[0]] = stop_split[1:]
f.close()


# combine stop ids (which are in route list) with their code
#for route_idx1 in range(len(route_list)):
#    for stops_in_route_list in range(3, len(route_list[route_idx1])):
#        for stop_idx in stop_list:
#            if stop_idx[0] == route_list[route_idx1][stops_in_route_list]:
#                route_list[route_idx1][stops_in_route_list] = [route_list[route_idx1][stops_in_route_list], stop_idx][1]

button1 = 3 # 3 is 100
button2 = 5 # 5 is 1187

# initialize and repeat if route button is pressed
route_name = BUS_PICK_LIST[button1]
for route in route_dict:
    if route_name == route_dict[route][0]:
        picked_route = route
        break

# pared dictionary with only picked stops.
pared_stop_dict = {}
for stop in stop_dict:
    if stop_dict[stop][0] in STOP_PICK_LIST:
        pared_stop_dict[stop_dict[stop][0]] = stop
# initialize and repeat if stop button is pressed
picked_stops_on_route = {}
for stop in pared_stop_dict:
    if pared_stop_dict[stop] in route_dict[picked_route]:
        picked_stops_on_route[stop] = pared_stop_dict[stop]
pared_stop_list = [key for key in picked_stops_on_route]
picked_stop = picked_stops_on_route[pared_stop_list[0]]


def button1_press():
    """GPIO input from user.
    Cycle through routes.
    """
    global button1
    global button2
    global picked_route
    # to-do: how much needs to be global?
    print("Select route:\n")
    for route in BUS_PICK_LIST:
        if BUS_PICK_LIST[button1] == route:
            print("*" + route + "*",end='\r')
        else:
            print(route,end='\r')
    print()
    # only want to increment button1 if button pressed again within these 5 seconds
    sleep(5)
    route_name = BUS_PICK_LIST[button1]
    for route in route_dict:
        if route_name == route_dict[route][0]:
            picked_route = route
            break
    button1 = (button1 + 1) % len(BUS_PICK_LIST)
    # call up new stop list? or default to first stop and don't ask until button 2 pressed?
    button2 = 0
    button2_press()

def button2_press():
    """GPIO input from user.
    Cycle through stops.
    """
    # to-do: how much needs to be global?
    global button2
    global pared_stop_list
    global picked_stop
    print("Select stop:\n")
    for stop in pared_stop_list:
        if pared_stop_list[button2] == stop:
            print("*" + stop + "*",end='\r')
        else:
            print(stop,end='\r')
    print()
    # only want to increment button2 if button pressed again within these 5 seconds
    sleep(5)
    picked_stops_on_route = {}
    for stop in pared_stop_dict:
        if pared_stop_dict[stop] in route_dict[picked_route]:
            picked_stops_on_route[stop] = pared_stop_dict[stop]
    pared_stop_list = [key for key in pared_stop_dict]
    picked_stop = picked_stops_on_route[STOP_PICK_LIST[button2]]
    button2 = (button2 + 1) % len(pared_stop_list)

second_counter = 0
bus_error = 0
weather_error = 0
while 1:
    # GoTriangle API Usage Limit: unknown!
    if (second_counter % 60) == 0:
        current_time = datetime.now()
        current_hour = current_time.hour
        current_minute = str(current_time.minute)
        if len(current_minute) == 1:
            current_minute = '0' + current_minute
        try:
            next_bus = durham_localized.update_gotriangle(picked_stop, picked_route, current_hour, current_minute)
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
        print('%d:%s BUS ERROR\n%d deg %s' % (current_hour, current_minute, current_temp, conditions_today))
    elif weather_error > 0 and bus_error == 0:
        print("%d:%s %s: %d\nWEATHER ERROR" % (current_hour, current_minute, picked_route[1], next_bus))
    elif weather_error > 0 and bus_error > 0:
        print("%d:%s BUS ERROR\nWEATHER ERROR" % (current_hour, current_minute))
    elif type(next_bus) == str:
        print("%d:%s %s\n%d deg %s" % (current_hour, current_minute, next_bus, current_temp, conditions_today))
    else:
        # \x01F is the marker for the degree symbol created earlier
        print("%d:%s %s: %dm\n%d deg %s" %
                    (current_hour, current_minute, route_name, next_bus, current_temp, conditions_today), end='\n')

#    if (current_hour >= 6 and current_hour <= 9) and (current_minute == 0 or current_minute == 30) and error_check == 0:
#        result = update_result(current_temp, high_today, conditions_today, wind, trip_time_bus, trip_time_subway)
#        move_servo(result)
    second_counter = (second_counter + 1) % 86400
    sleep(1)
