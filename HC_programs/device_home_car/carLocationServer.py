import socketserver
import re
import urllib
import os.path
from http.server import BaseHTTPRequestHandler,HTTPServer
import time
from math import sin, cos, sqrt, atan2, radians
import traceback
import requests 

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


def goodGpsPacket(car_location):
    lat_abs = abs(float(car_location["lat"]))
    lon_abs = abs(float(car_location["lon"]))
    if len(car_location["lat"]) > 0 and lat_abs > 0 and lat_abs < 200:
        if len(car_location["lon"]) > 0 and lon_abs > 0 and lon_abs < 200:
            return True
    return False

def traccarUpdateCords(ip, car_location):
    thisEpoch = round(time.time())
    URL = "http://"+str(ip) +":5055/?id="+str(10) \
            +"&timestamp="+str(thisEpoch) \
            +"&lat="+str(car_location["lat"]) \
            +"&lon="+str(car_location["lon"]) \
            +"&speed="+str(car_location["spd"]) \
            +"&bearing="+str(0) \
            +"&altitude="+str(car_location["alt"]) \
            +"&accuracy=7&batt="+str(0) \
            +"&mock=false"
    #URL = "http://localhost:5055/?id=123456&timestamp=1559930664&lat=21.943960422522565&lon=-82.5231837383169&speed=0.426437438413918&bearing=0.0&altitude=65.29470825195312&accuracy=7.548887252807617&batt=88.0&mock=true"
    r = requests.get(url = URL) 

class MyHandler(BaseHTTPRequestHandler):  
    def do_GET(self):
        try:
            self.send_response(200)   
            self.send_header("Content-type", "text/html")
            self.end_headers()  
            car_data = self.path
            print("got data: "+str(car_data) )
            try:
                car_data = car_data[1:]
                car_data_list = car_data.split(",")
                car_location["lat"] = car_data_list[0]
                car_location["lon"] = car_data_list[1]
                car_location["alt"] = car_data_list[2]
                car_location["spd"] = str(float(car_data_list[3])*0.621371)
                if goodGpsPacket(car_location) == True:
                    #calculate distance to house
                    car_location["dis"] = distance_between(car_location["lat"],car_location["lon"],house_location[0],house_location[1])
                    csvs = car_location["lat"]+","+car_location["lon"]+","+car_location["alt"]+","+car_location["spd"]+","+car_location["dis"] 
                    write_location_file(csvs)
                    traccarUpdateCords("127.0.0.1",car_location)
            except Exception:
                traceback.print_exc()
        except:
            print("Failed to http")


house_location = readHomeLocation()
httpd = socketserver.TCPServer(("", 5497), MyHandler)
httpd.allow_reuse_address = True
print("starting http server")
httpd.serve_forever()





