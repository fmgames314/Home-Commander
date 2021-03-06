#!/usr/bin/env python
# -*- coding: utf-8 -*-import re
# using https://pypi.org/project/pythonping/


import asyncio
import websockets
import subprocess
import json
import os
import socket
import time
import pickle
import traceback
#import other files in same directory
import basicDevices as BD
import homeCommanderDevices as HCD
import socketEvents as SE




# global variables
state = {}
def getState():
    return state
#setup state to manage imports
state["SE"] = SE   
state["BD"] = BD    
state["HCD"] = HCD 
#setup state to manage websocket connections
state["list_of_websockets"] = []
state["dict_of_devAddress"] = {}
#setup state to manage objects
state["list_of_basicDevs"] = []
state["list_of_basicSens"] = []
state["Service_ID_to_Name"] = {}
state["list_of_HCDs"] = [] #HCD is Hoem Commander Devices

def register(websocket):
    state["list_of_websockets"].append(websocket)
def unregister(websocket):
    state["list_of_websockets"].remove(websocket)


async def consumer_handler(websocket):
    async for message in websocket:
        try:
            packet = json.loads(message)
            # print(packet)
            try:
                await SE.process_websocket_event(websocket,packet,packet["event"],getState())
            except Exception as e:               
                traceback.print_exc()
        except Exception as e:
            print("failed to packet.loads: " + str(e))
            print("Here is the failed message: " + str(message))


async def producer_handler(websocket):
    while True:
        # print("producer loop but...")
        # for basic_dev in state["list_of_basicDevs"]:
        #     device_home = basic_dev.get_device_home()
        #     device_name = basic_dev.get_device_name()
        #     device_state = basic_dev.get_device_state()
        #     print([device_home,device_name,device_state])
        await asyncio.sleep(10)
        # output_dict = {}
        # output_dict["power_state"] = "0"
        # output_dict["device_name"] = "Lab Fan"
        # await SE.sendPacketToWSClient(websocket,"control",output_dict)




async def handler(websocket, path) -> None:
    #read in global value state 
    state = getState()
    #await SE.sendPacketToWSClient(websocket,"updateFields",state) #send a packet here to do it one time on client connect
    register(websocket)
    # make the handlers
    consumer_task = asyncio.ensure_future(consumer_handler(websocket))
    producer_task = asyncio.ensure_future(producer_handler(websocket))
    done, pending = await asyncio.wait(
        [consumer_task, producer_task], return_when=asyncio.FIRST_COMPLETED,
    )
    for task in pending:
        task.cancel()
    unregister(websocket)



def load_HCD(state):
    #read the config file
    with open('HomeCommanderDevices.txt', 'rb') as config_dictionary_file:
        config_dictionary = pickle.load(config_dictionary_file)
        #make HCDevs
        for devID, content in config_dictionary.items():
            #Extract the content from the file
            device_name = content[0]
            device_listOfBDs = content[1]
            device_state = content[2]
            device_id = content[3]
            alexa_control = content[4]
            #create the HCD
            new_HCD = state["HCD"].HCDevice(device_name)
            #Load the values into it 
            new_HCD.device_name = device_name
            new_HCD.device_listOfBDs = device_listOfBDs
            new_HCD.device_state = device_state
            new_HCD.device_id = device_id
            new_HCD.alexa_control = alexa_control
            #Add it to the list of HCDS
            state["list_of_HCDs"].append(new_HCD)
            


print("Loading HCDs")
try:
    load_HCD(state)
    print("Done Loading")
except:
    print("Failed to load HCDS")
print("Starting SANM")
start_server = websockets.serve(handler, "0.0.0.0", 1997)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()