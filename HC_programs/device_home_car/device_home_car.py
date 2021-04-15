import os.path
import asyncio
import time
import websockets
import json
import requests

state = {}
def getState():
    return state

state["ID"] = 900 #car
state["NAME"] = "Matrix Sensor"
state["sensor_data"] = {}
#local variables
state["fileChangeTime"] = "0"



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
                    # FOR A SENSOR WE DONT CARE WHAT SERVER SAYS
                    # if packet["event"] == "control":
                    #     device_name = packet["device_name"]
                    #     power_state = packet["power_state"]
                    #     await power_device(state,device_name,power_state)
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
        lastModtime = str(os.path.getmtime("car_location.txt"))
        if lastModtime != state["fileChangeTime"]:
            with open("car_location.txt", 'r') as locationFile:
                try:
                    car_data = locationFile.read()
                    car_data = car_data.split(",")
                    state["sensor_data"]["lat"] = car_data[0]
                    state["sensor_data"]["lon"] = car_data[1]
                    state["sensor_data"]["alt"] = car_data[2]
                    state["sensor_data"]["spd"] = car_data[3]
                    state["sensor_data"]["dis"] = car_data[4]
                    #send packet
                    print("sending packet")
                    output_dict = {}
                    output_dict["event"] = "list_of_sensor_data"
                    output_dict["MyID"] = state["ID"]
                    output_dict["device_table"] = state["sensor_data"]
                    json_out = json.dumps(output_dict)
                    string_of_data = str(json_out)
                    await websocket.send(string_of_data)
                except:
                    print("Failed to do location file sensor")
        await asyncio.sleep(3)
        state["fileChangeTime"] = lastModtime


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
    await sendPacketToWSClient(websocket,"connect",{ "MyID":state["ID"],"Name":state["NAME"] }) #send my ID on startup
    consumer_task = asyncio.ensure_future(consumer_handler(websocket,state))
    producer_task = asyncio.ensure_future(producer_handler(websocket,state))
    done, pending = await asyncio.wait([consumer_task, producer_task],return_when=asyncio.FIRST_COMPLETED,)
    for task in pending:
        task.cancel()
        return 0
        

{"event": "list_of_sensor_data", "MyID": 1005, "device_table": {"lat": "212", "lon": "231", "alt": "5626.345", "spd": "34534523"}}

tempState = getState()
loop = asyncio.get_event_loop()
loop.create_task(websocket_connection(tempState))
loop.run_forever()


