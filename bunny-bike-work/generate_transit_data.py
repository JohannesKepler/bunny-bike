# -*- coding: utf-8 -*-
"""
Created on Thu Mar 22 09:42:37 2018

@author: bw5177
"""
import requests

try:
    api_file = open("waldbauer_api.txt", "r")
    for line in api_file:
        current_line = line.split(",")
        if current_line[0] == "x_mashape_key":
            x_mashape_key = current_line[1].strip('\r\n')
    api_file.close()
except:
    wunderground_key = ""
    x_mashape_key = ""

def generate_agency_data(lat1="35.69212",lon1="-79.1111",lat2="36.08725",lon2="-78.32349"):
    """Function to generate agency list and output to csv.
    Input latitude and longitude boxing the area you want data for
    lat1,lon1 defining top left corner of box
    lat2,lon2 defining bottom right corner of box
    Default is the bounding box for Triangle Transit
    """
    response = requests.get("https://transloc-api-1-2.p.mashape.com/agencies.json?callback=call&geo_area=" + lat1 + "%2C" + lon1 + "%7C" + lat2 + "%2C" + lon2,
  headers={
    "X-Mashape-Key": x_mashape_key,
    "Accept": "application/json"
    }
    )
    
    transit_data_json = response.json()
    
    body = transit_data_json['data']
    f = open("agency_info.csv", "w+")
    f.write("Agency ID, Short Name, Lat1, Lon1, Lat2, Lon2\n")
    for agency in body:
        line_write = [agency["agency_id"],agency["short_name"],
                      str(agency["bounding_box"][0]["lat"]),
                      str(agency["bounding_box"][0]["lng"]),
                      str(agency["bounding_box"][1]["lat"]),
                      str(agency["bounding_box"][1]["lng"])]
        f.write(','.join(line_write) + '\n')
    f.close()

def generate_route_data(agency_list=['12','24']):
    """Input is a list of agency codes. Creates two csv files:
        route_info.csv has the route ID associated with the common name,
        as well as a list of stops on that route
        stop_info.csv has the stop ID associated with the common name
    """
    agencies = '%2C'.join(agency_list)
    response = requests.get("https://transloc-api-1-2.p.mashape.com/routes.json?agencies=" + agencies + "&callback=call", headers={
        "X-Mashape-Key": x_mashape_key,
        "Accept": "application/json"
        }
        )
    transit_data_json = response.json()
    # create a CSV file with the following headers: Route ID, Short Name, Long Name, Stops
    # Stops will extend into as many columns as necessary for each route
    f = open("route_info.csv", "w+")
    f.write("Route ID,Short Name,Long Name,Stops\n")
    for agency in agency_list:
        for bus_route in transit_data_json['data'][agency]:
            line_write = [bus_route['route_id'], bus_route['short_name'],
                          bus_route['long_name'].encode('ascii','ignore')]
            for stop in bus_route['stops']:
                line_write.append(stop)
            #print line_write
            f.write(','.join(line_write) + '\n')

    f.close()

    # need a separate unirest call to associate common names to stop IDs
    response2 = requests.get("https://transloc-api-1-2.p.mashape.com/stops.json?agencies=" + agencies + "&callback=call", headers={
        "X-Mashape-Key": x_mashape_key,
        "Accept": "application/json"
        }
        )

    stop_list = response2['data']
    f2 = open("stop_info.csv", "w+")
    f2.write("Stop ID,Stop Code,Stop Name\n")
    for stop in stop_list:
        line_write = [stop['stop_id'], stop['code'], stop['name']]
        #print line_write
        f2.write(','.join(line_write) + '\n')

    f2.close()