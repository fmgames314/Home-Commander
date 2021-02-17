import socketserver
import re
import urllib
import os.path
import pickle
from http.server import BaseHTTPRequestHandler,HTTPServer

path_to_HCDs = "/home/pi/home_commander/HC_programs/SANM/HomeCommanderDevices.txt"
dictOfNames = {}

def load_HCD():
    #read the config file
    with open(path_to_HCDs, 'rb') as config_dictionary_file:
        config_dictionary = pickle.load(config_dictionary_file)
        #make HCDevs
        for devID, content in config_dictionary.items():
            #Extract the content from the file
            device_name = content[0]
            device_listOfBDs = content[1]
            device_state = content[2]
            device_id = content[3]
            alexa_control = content[4]
            dictOfNames[int(device_id)] = device_name

class MyHandler(BaseHTTPRequestHandler):  
    def do_GET(self):
        try:
            self.send_response(200)   
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()  
            load_HCD()
            print((self.path) )
            for x in range(0, 100 ):
                if ("/"+str(x)+"?") in self.path:
                    try:
                        output = dictOfNames[x].encode(encoding='UTF-8')
                    except:
                        output = "NULL".encode(encoding='UTF-8')
                    self.wfile.write(output)
        except:
            print("Failed to http")

httpd = socketserver.TCPServer(("", 7001), MyHandler)
httpd.serve_forever()