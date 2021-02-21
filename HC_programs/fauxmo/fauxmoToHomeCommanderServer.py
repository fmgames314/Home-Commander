import asyncio
import websockets
from aiohttp import web
import json 
import time 

path_to_HCDs = "/home/pi/home_commander/HC_programs/SANM/HomeCommanderDevices.txt"
state = {}
state["lastPowState"] = {}
for i in range(100):
    state["lastPowState"][str(i)] = "0"

def getPowerPacket(state,device_id,device_state):
    bufferDict = {}
    bufferDict["event"] = "HCD_power"
    bufferDict["device_id"] = device_id
    bufferDict["device_state"] = device_state
    json_out = json.dumps(bufferDict)
    return str(json_out)


async def processWS(state):
    print("Starting Websocket Loop")
    uri = "ws://127.0.0.1:1997"
    async with websockets.connect(uri) as websocket:
        state["ws"] = websocket
        while True:
            await asyncio.sleep(1)
    # await websocket.send(name)
    # greeting = await websocket.recv()


async def handle(request):
    device_id = request.match_info.get('name', "NULL")
    device_state = request.match_info.get('state', "NULL")
    packet = getPowerPacket(state,device_id,device_state)
    await state["ws"].send(packet)
    # Return text back to teh connector
    device_state = int(device_state)
    if device_state == 2:
        try:
            device_state = state["lastPowState"][str(device_id)]
        except:
            print("bad devive key")
    else:
        try:
            state["lastPowState"][str(device_id)] = device_state
        except:
            print("bad device key")
    return web.Response(text=str(device_state))

#http://192.168.1.101:8080/deviceName/state


async def main():
    app = web.Application()
    app.add_routes([web.get('/', handle),
                    web.get('/{name}/{state}', handle)])
    await asyncio.gather(
        web._run_app(app, port=1998),
        processWS(state),
    )

asyncio.run(main())



# class socketServerToArdunio:
#     # variables
#     ServerIP = "127.0.0.1"
#     ServerPort = 7001
#     sendBuffer = ""

#     def __init__(self,ServerIP,ServerPort):
#         self.ServerIP = ServerIP
#         self.ServerPort = ServerPort
#         threading.Thread(target=self.startConnection, args=()).start()

#     def sendToServer(self,message):
#         self.sendBuffer+=str(message)

#     # connectionBuffer
#     def startConnection(self):
#         while True:
#             time.sleep(0.5)
#             if len(self.sendBuffer) > 0:
#                 try:
#                     print("Connecting")
#                     GML = socket.socket(socket.AF_INET, socket.SOCK_STREAM)        # Create a socket object
#                     GML.connect((self.ServerIP, self.ServerPort))
#                     GML.send(str.encode(self.sendBuffer))
#                     GML.close()    
#                     self.sendBuffer = "" 
#                 except Exception as e:
#                      print("Caught it! "+str(e) )


# class MyHandler(BaseHTTPRequestHandler):  
#     def do_GET(self):
#         self.send_response(200)   
#         self.send_response(200)
#         self.send_header("Content-type", "text/html")
#         self.end_headers()   
        
#         params = (self.path).split("/")
#         try:
#             print(params)
#             deviceID = int(params[1])
#             deviceState = int(params[2])

#             if deviceState == 0:
#                 listOfDevStates[deviceID] = 0
#                 ardServerCon.sendToServer("@PDS"+str(deviceID)+"?0?")
#                 self.wfile.write(str.encode("0")) 
                
#             if deviceState == 1:
#                 listOfDevStates[deviceID] = 1   
#                 ardServerCon.sendToServer("@PDS"+str(deviceID)+"?1?")
#                 self.wfile.write(str.encode("1"))  

#             if deviceState == 2:
#                 state = listOfDevStates[deviceID]
#                 self.wfile.write(str.encode(str(state))) 
#         except Exception as e:
#             print("error parsing url params: "+str(e))
#             self.wfile.write(str.encode("0")) 

        
    
# selfServerURL = "http://127.0.0.1:1998/"   

# configFileOutput = ""

# for switch in listOfSwitches:
#     if switch != "NULL":
#         configFileOutput += """{
#             "port": \""""+str(12340+i)+"""\",
#             "on_cmd": \""""+selfServerURL+str(i)+"/1"+"""\",
#             "off_cmd": \""""+selfServerURL+str(i)+"/0"+"""\",
#             "method": "GET",
#             "name": \""""+str(switch)+"""\",
#             "state_cmd": \""""+selfServerURL+str(i)+"/2"+"""\",
#             "state_method": "GET",
#             "state_data": {
#             "get_switch_state": "I want the switch state"
#             },
#             "state_response_on": "1",
#             "state_response_off": "0"
#         },"""
#     i+=1
# configFileOutput = configFileOutput[:-1]
# configFileData = """{
#     "FAUXMO": {
#         "ip_address": "auto"
#     },
#     "PLUGINS": {
#         "SimpleHTTPPlugin": {
#             "DEVICES": [
#                 """+configFileOutput+"""
#             ]
#         }
#     }
# }"""

# with open('/home/pi/config.json', 'w+') as the_file:
#     the_file.write(configFileData)


# ardServerCon = socketServerToArdunio("127.0.0.1",7000)


# httpd = socketserver.TCPServer(("", 7002), MyHandler)
# httpd.serve_forever()








