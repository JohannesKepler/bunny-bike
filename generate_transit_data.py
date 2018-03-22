# -*- coding: utf-8 -*-
"""
Created on Thu Mar 22 09:42:37 2018

@author: bw5177
"""
import unirest

def generate_transit_data(agency_list=['12','24']):
    """Input is a list of agency codes. Creates two csv files:
        route_info.csv has the route ID associated with the common name,
        as well as a list of stops on that route
        stop_info.csv has the stop ID associated with the common name
    """
    agencies = '%2C'.join(agency_list)
    x_mashape_key = "eJk1qrVGOMmshO6N3GVpq7b9rHkrp1Ofplxjsn66TP1Hw5OkFt"
    response = unirest.get("https://transloc-api-1-2.p.mashape.com/routes.json?agencies=" + agencies + "&callback=call", headers={
        "X-Mashape-Key": x_mashape_key,
        "Accept": "application/json"
        }
        )

    # create a CSV file with the following headers: Route ID, Short Name, Long Name, Stops
    # Stops will extend into as many columns as necessary for each route
    f = open("route_info.csv", "w+")
    f.write("Route ID,Short Name,Long Name,Stops\n")
    for agency in agency_list:
        for bus_route in response.body['data'][agency]:
            line_write = [bus_route['route_id'], bus_route['short_name'],
                          bus_route['long_name'].encode('ascii','ignore')]
            for stop in bus_route['stops']:
                line_write.append(stop)
            #print line_write
            f.write(','.join(line_write) + '\n')

    f.close()

    # need a separate unirest call to associate common names to stop IDs
    response = unirest.get("https://transloc-api-1-2.p.mashape.com/stops.json?agencies=" + agencies + "&callback=call", headers={
        "X-Mashape-Key": x_mashape_key,
        "Accept": "application/json"
        }
        )

    stop_list = response.body['data']
    f = open("stop_info.csv", "w+")
    f.write("Stop ID,Stop Code,Stop Name\n")
    for stop in stop_list:
        line_write = [stop['stop_id'], stop['code'], stop['name']]
        #print line_write
        f.write(','.join(line_write ) + '\n')

    f.close()