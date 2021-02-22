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

# @PDS10?0?
# @PDS3?0?
# @PDS21?0?

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

async def handle_client(client,state):
    request = None
    while request != 'quit':
        request = (await loop.sock_recv(client, 255)).decode('utf8')
        if request == "":
            print("Client Dissconnected")
            client.close()
        else:
            listOfMessages = request.split("@")
            for splits in listOfMessages:
                try:
                    if splits != "":
                        if "PDS" in splits:
                            splits = splits.replace('PDS','') #remove the flag name
                            packet = splits.split("?")
                            device_id = packet[0]
                            device_state = packet[1]
                            await power_device(state,device_id,device_state)
                        if "KEY" in splits:
                            splits = splits.replace('KEY','') #remove the flag name
                            packet = splits.split("?")
                            key = packet[0]
                            bufferDict = {}
                            bufferDict["event"] = "key"
                            bufferDict["key"] = key
                            json_out = json.dumps(bufferDict)
                            await state["ws"].send(json_out)

                except:
                    print("Bad packet")
            response = ""

    #client.close()
async def brodcast_socket(client,state):
    connected = True
    while connected == True:
        try:
            #send the crap to the client
            response = ""
            #device states
            HDP_string = "@HDP"
            for device_id, device_state in state["dictOfStates"].items():
                HDP_string+=str(round(int(device_state)))
            HDP_string+="0?%"
            response+=HDP_string
            #sensors #ex @HAD0?153?1?82.78?1016.29?0?0?0?1?1?1?1?%
            HAD_string = "@HAD"
            for value in state["listOfSensors"]:
                HAD_string+=str(value)+"?"
            HAD_string+="%"
            response+=HAD_string
            # print(response)
            await loop.sock_sendall(client, response.encode('utf8'))
            await asyncio.sleep(.3)
        except:
            print("failed to brodcast to clients!?!?!")
            connected = False
            await asyncio.sleep(1)

async def run_server(state):
    
    while True:
        client, _ = await loop.sock_accept(server)
        loop.create_task(handle_client(client,state))
        loop.create_task(brodcast_socket(client,state))

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('0.0.0.0', 7000))
server.listen(8)
server.setblocking(False)



async def parse_packet(state,packet):
    try:
        # print(packet)
        if packet["event"] == "give_list_HCDs":
            device_table = packet["device_table"]
            for device in device_table:
                device_name = device[0]
                device_state = device[1]
                device_id = device[2]
                state["dictOfStates"][device_id] = device_state
        if packet["event"] == "give_list_basic_sensors":
            try:
                state["listOfSensors"] = []
                device_table = packet["device_table"]
                for device in device_table:
                    device_value = device[2]
                    device_trans = device[4]
                    if device_trans == 1:
                        state["listOfSensors"].append(device_value)   
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
loop.create_task(run_server(state))
loop.run_forever()


# @HAD0?153?1?82.78?1016.29?0?0?0?1?1?1?1?%
# @HDP11101000110100000010011000010000010010000000000000?%





# def getPowerPacket(state,device_id,device_state):
#     bufferDict = {}
#     bufferDict["event"] = "HCD_power"
#     bufferDict["device_id"] = device_id
#     bufferDict["device_state"] = device_state
#     json_out = json.dumps(bufferDict)
#     return str(json_out)


# async def processWS(state):
#     print("Starting Websocket Loop")
#     uri = "ws://127.0.0.1:1997"
#     async with websockets.connect(uri) as websocket:
#         state["ws"] = websocket
#         while True:
#             await asyncio.sleep(1)
#     # await websocket.send(name)
#     # greeting = await websocket.recv()


# async def handle(request):
#     device_id = request.match_info.get('name', "NULL")
#     device_state = request.match_info.get('state', "NULL")
#     packet = getPowerPacket(state,device_id,device_state)
#     await state["ws"].send(packet)
#     # Return text back to teh connector
#     device_state = int(device_state)
#     if device_state == 2:
#         device_state = state["lastPowState"][str(device_id)]
#     else:
#         state["lastPowState"][str(device_id)] = device_state
#     return web.Response(text=str(device_state))

# #http://192.168.1.101:8080/deviceName/state


# async def main():
#     app = web.Application()
#     app.add_routes([web.get('/', handle),
#                     web.get('/{name}/{state}', handle)])
#     await asyncio.gather(
#         web._run_app(app, port=1998),
#         processWS(state),
#     )

# asyncio.run(main())