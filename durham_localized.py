# -*- coding: utf-8 -*-
"""
Created on Sun Jun 19 15:36:03 2016
@author: kwatz
"""

import requests
#import unirest
from datetime import datetime

# consider pulling this info from a csv file
# need to incorporate numpy?

# add your private API keys here. you can use a text file to store them like me, or just add them directly
try:
    api_file = open("waldbauer_api.txt", "r")
    for line in api_file:
        current_line = line.split(",")
        if current_line[0] == "wunderground_key":
            wunderground_key = current_line[1].strip('\r\n')
        elif current_line[0] == "x_mashape_key":
            x_mashape_key = current_line[1].strip('\r\n')
    api_file.close()
except:
    wunderground_key = ""
    x_mashape_key = ""

def update_weather():
    """API call to Weather Underground for the local (Durham) weather.
    Takes no inputs, outputs a tuple:
    (today's weather, current temp, today's high temp, today's windspeed)
    """
    f = requests.get('http://api.wunderground.com/api/' + wunderground_key + '/forecast/q/NC/Durham.json')
    f2 = requests.get('http://api.wunderground.com/api/' + wunderground_key + '/geolookup/conditions/q/NC/Durham.json')

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

# is it better to search a lat/long coordinate system and search results by the "name" key? need to learn how to search results by key!
def update_gotriangle(stop_id, route_id, current_hour, current_minute):
    """API call to the Mashape OpenAPI transit API used by transloc
    Takes as inputs: (stop ID, route ID, the hour now, the minute now)
    Returns as output an integer of minutes until the next bus arrives at the stop
    """
    # see stop_id.csv for list of stops
    # see route_id.csv for list of routes
    # requests not currently working with gotriangle?
    f = requests.get("https://transloc-api-1-2.p.mashape.com/arrival-estimates.json?agencies=12%2C24&callback=call&routes=" + route_id, headers={
    "X-Mashape-Key": x_mashape_key,
    "Accept": "application/json"
    }
    )
    
    gotriangle_json = f.json()
    
    # sometimes current minute is a string
    current_minute = int(current_minute)
    # default arrival_time to an error message. it will be overwritten if possible, otherwise
    # function will return the error message
    # this needs work lol

    stop_list = gotriangle_json['data']
    for stop in stop_list:
        if stop['stop_id'] == stop_id:
            for arrival in stop['arrivals']:
                if arrival['route_id'] == route_id:
                    arrival_time = datetime.strptime(arrival['arrival_at'], '%Y-%m-%dT%H:%M:%S-04:00')
                    arrival_minute = arrival_time.minute + 60 * (arrival_time.hour - current_hour)
                    next_bus = arrival_minute - current_minute
                    return next_bus
    return "NO BUS ARR"
#            else:
#                # in main.py, check if type(next_bus) == string
#                return "ERR: NO BUS"
#            break
#        else:
#            # in durham_main.py, check if type(next_bus) == string
#            return "ERR: NO BUS"

def update_result(current_temp, high_today, conditions_today, wind, next_bus):
    # parameters:
    # current_temp - check for coldness
    # high_today - check for hotness
    # conditions_today - check for rain
    # wind - check for high wind
    # next_bus - check for delays

    result = 100 # 100 means ride your bike
    # deduct a point for each degree it is colder than 60
    if current_temp < 60:
        result -= (60 - current_temp)

    # deduct a point for each degree it is hotter than 90
    if high_today > 90:
        result -= (high_today - 90)

    # deduct points for conditions
    if "Drizzle" in conditions_today:
        result -= 15

    if "Rain" in conditions_today:
        result -= 30

    if "Snow" in conditions_today:
        result -= 50

    if "Heavy" in conditions_today:
        result -= 25

    bads = ("Ice", "Hail", "Volcanic Ash", "Sandstorm", "Thunderstorm", "Funnel Cloud", "Unknown Precipitation")
    for bad in bads:
        if bad in conditions_today:
            result -= 100

    # deduct points for high wind
    if wind >= 10 and wind < 15:
        result -= 10

    if wind >= 15 and wind < 20:
        result -= 25

    if wind >= 20:
        result -= 75

    # add points for delays
    if next_bus > 30:
        result += 5 * (next_bus - 30)

    # restrict result to be between 0 and 100
    if result < 0:
        result = 0
    elif result > 100:
        result = 100

    #print "Result: %d" % result
    return result
