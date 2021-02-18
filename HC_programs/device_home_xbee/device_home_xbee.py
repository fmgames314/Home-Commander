import aioserial
import asyncio
from kasa import Discover
import time
import websockets
import json
import pickle

state = {}
def getState():
    return state

state["ID"] = 2 #kasa ID group
state["program_name"] = "XBEE Controller"
state["devices"] = {}
state["device_file_location"] = "/home/pi/home_commander/HC_programs/device_home_xbee/xbee_devices.pickle"


def save_device_list(state):
    print("Saving Device List")
    with open(state["device_file_location"], 'wb') as config_dictionary_file:
        pickle.dump(state["devices"], config_dictionary_file)

async def power_device(state,device_name,power_state):
    command = ""
    for dev_name, values in state["devices"].items():
        if device_name == dev_name:
            if power_state == 0:
                command = values[2]
                state["devices"][dev_name][0] = "0" #update the state in the dict
            if power_state == 1:
                command = values[1]    
                state["devices"][dev_name][0] = "1" #update the state in the dict  
    packet = command
    packet = packet.encode()
    await state["serial_port"].write_async(packet)

async def sendPacketToWSClient(websocket,eventName,inputDict):
    try:
        inputDict["event"] = eventName
        json_out = json.dumps(inputDict)
        await websocket.send(str(json_out))
    except Exception as e:
        print("couldn't send data to websocket" + str(e))

async def consumer_handler(websocket,state):
    try:
        async for message in websocket:
            try:
                packet = json.loads(message)
                try:
                    print(packet)
                    if packet["event"] == "control":
                        device_name = packet["device_name"]
                        power_state = packet["power_state"]
                        await power_device(state,device_name,power_state)
                        await sendOutletsToServer(websocket,state)
                    if packet["event"] == "add_xbee_device":
                        device_name = packet["device_name"]
                        device_on_command = packet["device_on_command"]
                        device_off_command = packet["device_off_command"]
                        state["devices"][device_name] = [0,device_on_command,device_off_command]
                        save_device_list(state)
                except Exception as e:
                    print("bad websocket packet, probably no event name: "+str(e))
            except Exception as e:
                print("failed to packet.loads: " + str(e))
                print("Here is the failed message: " + str(message))
    except:
        print("websocket died? reset?")
        return 0


async def producer_handler(websocket,state):
    while True:
        try:
            await sendOutletsToServer(websocket,state)
            await asyncio.sleep(1)
        except Exception as e:
            print("failed to send a websocket packet: " + str(e))
            await asyncio.sleep(2)

async def sendOutletsToServer(websocket,state):
    output_dict = {}
    output_dict["MyID"] = state["ID"]
    #generate device_table
    output_dict["device_table"] = {}
    for dev_name, values in state["devices"].items():
        output_dict["device_table"][dev_name] = values[0] #makes a key/value pair of name and device state
    await sendPacketToWSClient(websocket,"list_of_devices",output_dict)

async def websocket_connection(state):
    while True:
        print("starting websocket connection")
        try:
            uri = "ws://localhost:1997"
            async with websockets.connect(uri) as websocket:
                status = await handler(websocket,state)
        except Exception as e:
            print("Problem with websocket: error: "+str(e))
            await asyncio.sleep(5)


async def handler(websocket,state):

    await sendPacketToWSClient(websocket,"connect",{ "MyID":state["ID"],"Name":state["program_name"] }) #send my ID on startup
    consumer_task = asyncio.ensure_future(consumer_handler(websocket,state))
    producer_task = asyncio.ensure_future(producer_handler(websocket,state))
    done, pending = await asyncio.wait([consumer_task, producer_task],return_when=asyncio.FIRST_COMPLETED,)
    for task in pending:
        task.cancel()
        return 0



#load the pickle file
def load_device_file(state):
    #read the config file
    with open(state["device_file_location"], 'rb') as config_dictionary_file:
        config_dictionary = pickle.load(config_dictionary_file)
        state["devices"] = config_dictionary

state["serial_port"] = aioserial.AioSerial(port='/dev/serial0')
try:
    load_device_file(state)
except:
    print("failed to load device file")
loop = asyncio.get_event_loop()
loop.create_task(websocket_connection(state))
loop.run_forever()




