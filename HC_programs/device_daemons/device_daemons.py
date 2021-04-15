
import asyncio
import websockets
from aiohttp import web
import socket
import json 
import time 

state = {}
state["dictOfStates"] = {}
state["lastTime"] = 0
state["listOfSensors"] = []


def millis():
    return time.time_ns() // 1_000_000 

def getPowerPacket(state,device_id,device_state):
    bufferDict = {}
    bufferDict["event"] = "HCD_power"
    bufferDict["device_id"] = device_id
    bufferDict["device_state"] = device_state
    json_out = json.dumps(bufferDict)
    return str(json_out)

async def power_device(state,device_id,device_state):
    packet = getPowerPacket(state,device_id,device_state)
    await state["ws"].send(packet)


async def parse_packet(state,packet):
    try:
        # print(packet)
        # parse house outlets
        if packet["event"] == "give_list_HCDs":
            try:
                state["dictOfStates"] = packet["device_table"]
                print(state["dictOfStates"])
            except Exception as e:
                print("Failed to device table"+str(e))    
        # parse sensors    
        if packet["event"] == "give_list_basic_sensors":
            try:
                state["listOfSensors"] = packet["device_table"]
                print(state["listOfSensors"])
            except Exception as e:
                print("Failed to sensor"+str(e))         
    except Exception as e:
        print("bad websocket packet, probably no event name: "+str(e))

async def processWS(state):
    print("Starting Websocket Loop")
    uri = "ws://127.0.0.1:1997"
    async with websockets.connect(uri) as websocket:
        state["ws"] = websocket
        while True:
            #send HCS request
            json_out = json.dumps({"event":"request_list_HCDs"})
            await state["ws"].send(json_out)
            #Receive HCDs
            packet = await websocket.recv()
            packet = json.loads(packet)
            await parse_packet(state,packet) 
            #Send Sensor Request           
            json_out = json.dumps({"event":"request_list_basic_sensors"})
            await state["ws"].send(json_out)                
            #Receive sensors
            packet = await websocket.recv()
            packet = json.loads(packet)
            await parse_packet(state,packet) 
            await asyncio.sleep(.2)
    # await websocket.send(name)
    # greeting = await websocket.recv()
   

loop = asyncio.get_event_loop()
loop.create_task(processWS(state))
# loop.create_task(run_server(state))
loop.run_forever()
