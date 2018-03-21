# -*- coding: utf-8 -*-
"""
Created on Sun Jun 19 15:36:03 2016
@author: beck w
"""

import requests

# add your private wunderground and MBTA keys here
wunderground_key = ""
MBTA_key = ""

def update_weather():
    f = requests.get('http://api.wunderground.com/api/' + wunderground_key + '/forecast/q/MA/Boston.json')
    f2 = requests.get('http://api.wunderground.com/api/' + wunderground_key + '/geolookup/conditions/q/MA/Boston.json')

    forecast_json = f.json()
    conditions_json = f2.json()

    conditions_today = forecast_json['forecast']['simpleforecast']['forecastday'][0]['conditions']

    high_today = int(forecast_json['forecast']['simpleforecast']['forecastday'][0]['high']['fahrenheit'])

    wind = int(conditions_json['current_observation']['wind_mph'])

    #low_today = forecast_json['forecast']['simpleforecast']['forecastday'][0]['low']['fahrenheit']

    current_temp = int(conditions_json['current_observation']['temp_f'])

    # print "Current temp (F): %d" % current_temp
    # print "High temp (F): %d" % high_today
    # print "Weather conditions: %s" % conditions_today
    # print "Wind (mph): %d" % wind
    # print
    return (conditions_today, current_temp, high_today, wind)

def update_mbta():
    routes = requests.get('http://realtime.mbta.com/developer/api/v2/predictionsbyroutes?api_key=' + MBTA_key + '&routes=73,Red&format=json')
    routes_json = routes.json()

    bus_json = routes_json['mode'][1]['route'][0]
    subway_json = routes_json['mode'][0]['route'][0]

    closest_bus = 10000
    for trips in bus_json['direction'][1]['trip']:
        for stops in trips['stop']:
            if stops['stop_id'] == '2108': # 'Trapelo Rd @ Belmont St - Benton Square'
                check_closest_bus = int(stops['pre_away'])
                if check_closest_bus < closest_bus:
                    closest_bus = check_closest_bus
                    my_trip = trips
                break
            
    #print "Next bus: %d " % closest_bus

    for stops in my_trip['stop']:
        if 'Red Line' in stops['stop_name']:
            end_trip_time_bus = int(stops['pre_away'])
            break
    trip_time_bus = end_trip_time_bus - closest_bus
    #print "Bus Trip time: %d" % trip_time_bus


    def nested_loop(trips):
        for stops_idx in range(len(trips['stop'])-1):
            if trips['stop'][stops_idx]['stop_id'] == '70067': # 'Harvard - Inbound'
                harvard_eta = int(trips['stop'][stops_idx]['pre_away'])
                kendall_eta = int(trips['stop'][stops_idx+2]['pre_away'])
                trip_time_subway = kendall_eta - harvard_eta
                return trip_time_subway
        return 'False'

    for trips in subway_json['direction'][0]['trip']:
        trip_time_subway = nested_loop(trips)
        if trip_time_subway != 'False':
            break
            
    #print "Subway Trip time: %r" % trip_time_subway
    return (closest_bus, trip_time_bus, trip_time_subway)

def update_result(current_temp, high_today, conditions_today, wind, trip_time_bus, trip_time_subway):
    # parameters:
    # current_temp - check for coldness
    # high_today - check for hotness
    # conditions_today - check for rain
    # wind - check for high wind
    # trip_time_bus - check for delays
    # trip_time_subway - check for delays

    result = 100 # 100 means ride your bike
    # deduct a point for each degree it is colder than 60
    if current_temp < 50:
        result -= (55 - current_temp) * 5
        
    # deduct a point for each degree it is hotter than 90
    if high_today > 90:
        result -= (high_today - 90) * 5

    # deduct points for conditions
    if "Drizzle" in conditions_today:
        result -= 15
        
    if "Rain" in conditions_today:
        result -= 70
        
    if "Snow" in conditions_today:
        result -= 90
        
    if "Heavy" in conditions_today:
        result -= 25

    # add some back if it's just light
    if "Light" in conditions_today:
        result += 20
        
    bads = ("Ice", "Hail", "Volcanic Ash", "Sandstorm", "Thunderstorm", "Funnel Cloud", "Unknown Precipitation")
    for bad in bads:
        if bad in conditions_today:
            result -= 100

    # deduct points for high wind
    if wind >= 10 and wind < 15:
        result -= 50
        
    if wind >= 15 and wind < 20:
        result -= 75
        
    if wind >= 20:
        result -= 90

    # add points for delays
    if trip_time_bus >= 1300:
        result += 10 * ((trip_time_bus - 1000) // 60)

    if trip_time_subway >= 420:
        result += 10 * ((trip_time_subway - 360) // 60)

    # restrict result to be between 0 and 100
    if result < 0:
        result = 0
    elif result > 100:
        result = 100
        
    #print "Result: %d" % result
    # 100 is all the way right but the physical bike symbol is on the left so i have to reverse
    return 100 - result
