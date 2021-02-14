import asyncio
import time
import websockets
import json
import requests

state = {}
def getState():
    return state

state["ID"] = 1000 #weather service
state["NAME"] = "Weather Sensor"
state["sensor_data"] = {}


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
        try:
            api_key = "664150edd23b3811d159024d8617d598"
            base_url = "http://api.openweathermap.org/data/2.5/weather?"
            city_name = "Land O Lakes"
            complete_url = base_url + "appid=" + api_key +"&units=imperial&q=" + city_name 
            response = requests.get(complete_url) 
            x = response.json() 
            y = x["main"] 
            z = x["weather"] 
            #load dictionary
            state["sensor_data"] = {}
            state["sensor_data"]["temp"] = y["temp"] 
            state["sensor_data"]["pressure"] = y["pressure"] 
            state["sensor_data"]["humidity"] = y["humidity"] 
            state["sensor_data"]["weather"] = x["weather"][0]["main"]
            state["sensor_data"]["description"] = z[0]["description"] 
            #send packet
            print("sending packet")
            output_dict = {}
            output_dict["MyID"] = state["ID"]
            output_dict["device_table"] = state["sensor_data"]
            await sendPacketToWSClient(websocket,"list_of_sensor_data",output_dict)
            await asyncio.sleep(30)
        except Exception as e:
            print("failed to send a websocket packet: " + str(e))
            await asyncio.sleep(30)




async def websocket_connection(state):
    while True:
        print("starting websocket connection")
        try:
            uri = "ws://localhost:1997"
            async with websockets.connect(uri) as websocket:
                status = await handler(websocket,state)
        except Exception as e:
            print("Problem with websocket: error: "+str(e))


async def handler(websocket,state):
    await sendPacketToWSClient(websocket,"connect",{ "MyID":state["ID"],"Name":state["NAME"] }) #send my ID on startup
    consumer_task = asyncio.ensure_future(consumer_handler(websocket,state))
    producer_task = asyncio.ensure_future(producer_handler(websocket,state))
    done, pending = await asyncio.wait([consumer_task, producer_task],return_when=asyncio.FIRST_COMPLETED,)
    for task in pending:
        task.cancel()
        return 0

        


tempState = getState()
loop = asyncio.get_event_loop()
# loop.create_task(kasa_discover_loop(tempState))
# loop.create_task(kasa_update_loop(tempState))
loop.create_task(websocket_connection(tempState))
loop.run_forever()




