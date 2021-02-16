import asyncio
from kasa import Discover
import time
import websockets
import json

state = {}
def getState():
    return state

state["ID"] = 1 #kasa ID group
state["devices"] = {}

async def power_device(state,device_name,power_state):
    try:
        #itterate over devices and search for a name
        for addr, dev in state["devices"].items():
            if dev.alias == device_name: #name matches 
                if str(power_state) == "0":
                    await dev.turn_off()    
                if str(power_state) == "1":
                    await dev.turn_on()
                await dev.update()
                state["outlet_dict"][str(dev.alias)] = dev.is_on
    except Exception as e:
        print("couldn't control outlet, probably doesn't exist yet" + str(e))

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
                    # print(packet)
                    if packet["event"] == "control":
                        device_name = packet["device_name"]
                        power_state = packet["power_state"]
                        await power_device(state,device_name,power_state)
                        await sendOutletsToServer(websocket,state)
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
    output_dict["device_table"] = state["outlet_dict"]
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
    await sendPacketToWSClient(websocket,"connect",{ "MyID":state["ID"],"Name":"Kasa Controller" }) #send my ID on startup
    consumer_task = asyncio.ensure_future(consumer_handler(websocket,state))
    producer_task = asyncio.ensure_future(producer_handler(websocket,state))
    done, pending = await asyncio.wait([consumer_task, producer_task],return_when=asyncio.FIRST_COMPLETED,)
    for task in pending:
        task.cancel()
        return 0

        
async def dicoverBS(state,i):
    possibleDevice = await Discover.discover(target="192.168.5."+str(i))
    state["devices"].update(possibleDevice)

async def kasa_discover_loop(state):
    while True:
        print("about to run a discovery")
        state["kasa_disc_state"] = True 
        for i in range(255):
            loop.create_task(dicoverBS(state,i))
        state["kasa_disc_state"] = False
        await asyncio.sleep(3600)


async def kasa_update_loop(state):
    while True:
        try:
            if state["kasa_disc_state"] == False: #don't update if discovering kasa
                await update_kasas(state)
                await asyncio.sleep(6)     
            else:
                print("waiting for discovery before updating")
                await asyncio.sleep(2)

        except Exception as e:
            print("Issue with devices update, Error: "+str(e))
            await asyncio.sleep(1)

async def update_kasas(state):
    if state["kasa_disc_state"] == False: #don't update if discovering kasa
        state["outlet_dict"] = {}
        for addr, dev in state["devices"].items():
            await dev.update()
            state["outlet_dict"][str(dev.alias)] = dev.is_on


tempState = getState()
loop = asyncio.get_event_loop()
loop.create_task(kasa_discover_loop(tempState))
loop.create_task(kasa_update_loop(tempState))
loop.create_task(websocket_connection(tempState))
loop.run_forever()




