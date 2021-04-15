import socketserver
import re
import urllib
import os.path
from http.server import BaseHTTPRequestHandler,HTTPServer
import time
from math import sin, cos, sqrt, atan2, radians
import traceback

car_location = {}
house_location = [0,0]

def readHomeLocation():
    try:
        with open("home_location.txt", 'r') as home_location:
            house_data = home_location.read()
            house_data = house_data.split(",")
            return house_data
    except:
        print("no home_location.txt file found")
        return [0,0]

def write_location_file(car_data):
    f = open("car_location.txt", "w")
    f.write(car_data)
    f.close()


def distance_between(lat1,lon1,lat2,lon2):
    # approximate radius of earth in km
    R = 6373.0
    lat1 = radians(float(lat1))
    lon1 = radians(float(lon1))
    lat2 = radians(float(lat2))
    lon2 = radians(float(lon2))
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    conv_fac = 0.621371
    miles = distance * conv_fac
    miles = round(miles,3)
    return str(miles)



class MyHandler(BaseHTTPRequestHandler):  
    def do_GET(self):
        try:
            self.send_response(200)   
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()  
            car_data = self.path
            try:
                car_data = car_data[1:]
                car_data_list = car_data.split(",")
                car_location["lat"] = car_data_list[0]
                car_location["lon"] = car_data_list[1]
                car_location["alt"] = car_data_list[2]
                car_location["spd"] = car_data_list[3]
                #calculate distance to house
                car_location["dis"] = distance_between(car_location["lat"],car_location["lon"],house_location[0],house_location[1])
                csvs = car_location["lat"]+","+car_location["lon"]+","+car_location["alt"]+","+car_location["spd"]+","+car_location["dis"] 
                write_location_file(csvs)
            except Exception:
                traceback.print_exc()
        except:
            print("Failed to http")


house_location = readHomeLocation()
httpd = socketserver.TCPServer(("", 5497), MyHandler)
httpd.allow_reuse_address = True
print("starting http server")
httpd.serve_forever()





