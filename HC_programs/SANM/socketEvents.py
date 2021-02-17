import json
import pickle

#for saving home commander Devices
def save_HCD(state):
    config_dictionary = {}
    #load the dictionary with the home Commander Devices
    for HC_Dev in state["list_of_HCDs"]:
        listOfVals = [HC_Dev.device_name,HC_Dev.device_listOfBDs,HC_Dev.device_state,HC_Dev.device_id,HC_Dev.alexa_control]
        config_dictionary[HC_Dev.device_id] = listOfVals
    #open the file and save
    with open('HomeCommanderDevices.txt', 'wb') as config_dictionary_file:
        pickle.dump(config_dictionary, config_dictionary_file)
    # now to write the alexa file
    configFileOutput = ""
    for HC_Dev in state["list_of_HCDs"]:
        # get each HCD alexa string, if it is off it returns ""
        configFileOutput+=HC_Dev.alexa_make_string()
    configFileOutput = configFileOutput[:-1]
    configFileData = """{
        "FAUXMO": {
            "ip_address": "auto"
        },
        "PLUGINS": {
            "SimpleHTTPPlugin": {
                "DEVICES": [
                    """+configFileOutput+"""
                ]
            }
        }
    }"""
    # print(configFileData)
    with open('/home/pi/home_commander/HC_programs/fauxmo/config.json', 'w+') as the_file:
        the_file.write(configFileData)

#--------------List management for a basic device---------------------------
def check_if_basic_device_in_list(state,device_home,device_name):
    for basic_dev in state["list_of_basicDevs"]:
        if basic_dev.get_device_home() == device_home and basic_dev.get_device_name() == device_name:
            return True
    return False

def get_basic_device_in_list(state,device_home,device_name):
    for basic_dev in state["list_of_basicDevs"]:
        if basic_dev.get_device_home() == device_home and basic_dev.get_device_name() == device_name:
            return basic_dev
    return False

def find_or_create_basic_device(state,device_home,device_name):
    basic_dev = None
    try:
        if check_if_basic_device_in_list(state,device_home,device_name):
            #update:
            basic_dev = get_basic_device_in_list(state, device_home,device_name)
        else:
            #create
            service_name = state["Service_ID_to_Name"][device_home]
            basic_dev = state["BD"].basicDevice(device_home, device_name, service_name)
            state["list_of_basicDevs"].append(basic_dev)
    except Exception as e:
        print("Problem updating or creating basic device "+str(e))
    return basic_dev

#--------------List management for a basic sensor device---------------------------
def check_if_basic_sensor_in_list(state,device_home,device_name):
    for basic_sen in state["list_of_basicDevs"]:
        if basic_sen.get_device_home() == device_home and basic_sen.get_device_name() == device_name:
            return True
    return False

def get_basic_sensor_in_list(state,device_home,device_name):
    for basic_sen in state["list_of_basicDevs"]:
        if basic_sen.get_device_home() == device_home and basic_sen.get_device_name() == device_name:
            return basic_sen
    return False

def find_or_create_basic_sensor(state,device_home,device_name):
    basic_sen = None
    try:
        if check_if_basic_sensor_in_list(state,device_home,device_name):
            #update:
            basic_sen = get_basic_sensor_in_list(state, device_home,device_name)
        else:
            #create
            service_name = state["Service_ID_to_Name"][device_home]
            basic_sen = state["BD"].basicSensor(device_home, device_name, service_name)
            state["list_of_basicSens"].append(basic_sen)
    except Exception as e:
        print("Problem updating or creating basic sensor "+str(e))
    return basic_sen

#send a packet to a webserver
async def sendPacketToWSClient(websocket,eventName,inputDict):
    try:
        inputDict["event"] = eventName
        json_out = json.dumps(inputDict)
        await websocket.send(str(json_out))
    except Exception as e:
        print("couldn't send data to websocket" + str(e))


#PROCESS THE EVENT DATA FROM A PACKET

async def process_websocket_event(websocket,packet,eventName,state):
    # print(packet)
    if eventName == "connect":
        try:
            MyID = packet["MyID"]
            Name = packet["Name"]
            state["Service_ID_to_Name"][MyID] = Name
            try:
                state["dict_of_devAddress"][MyID] = websocket
            except Exception as e:
                print("Couldn't set dict_of_devAddress: error: "+str(e))
        except:
            print("bad connect packet")
    #updated data from device homes aka services
    if eventName == "list_of_devices":
        try:
            device_home = packet["MyID"]
            device_table = packet["device_table"]
            for device_name, device_state in device_table.items():
                basic_dev = find_or_create_basic_device(state,device_home,device_name)
                if basic_dev != False:
                    basic_dev.set_device_state(device_state)
                else:
                    print("Some problem with device, it wouldn't find or create")
            #now that we updated basic devices lets let the Home commadner devices recalcualte staes
            for HC_device in state["list_of_HCDs"]:
                HC_device.calculate_state(state)
        except:
            print("Client sent bad device table")
    #updated data from sensor services 
    if eventName == "list_of_sensor_data":
        try:
            device_home = packet["MyID"]
            device_table = packet["device_table"]
            for device_name, device_state in device_table.items():
                basic_dev = find_or_create_basic_sensor(state,device_home,device_name)
                if basic_dev != False:
                    basic_dev.set_device_value(device_state)
                else:
                    print("Some problem with sensor, it wouldn't find or create")
        except:
            print("Client sent bad sensor table")


    # this even is when a client asks for and the server gives, the list of devices that includes name and state        
    if eventName == "request_list_basic_devices":
        output_dict = {}
        output_dict["device_table"] = []
        for basic_dev in state["list_of_basicDevs"]:
            device_home = basic_dev.get_device_home()
            device_name = basic_dev.get_device_name()
            device_state = basic_dev.get_device_state()
            service_name = basic_dev.get_service_name()
            output_dict["device_table"].append( [device_home,device_name,device_state,service_name] )
        await sendPacketToWSClient(websocket,"give_list_basic_devices",output_dict)
   # this even is when a client asks for and the server gives, the list of sensors that includes name and values        
    if eventName == "request_list_basic_sensors":
        output_dict = {}
        output_dict["device_table"] = []
        for basic_dev in state["list_of_basicSens"]:
            device_home = basic_dev.get_device_home()
            device_name = basic_dev.get_device_name()
            device_value = basic_dev.get_device_value()
            service_name = basic_dev.get_service_name()
            device_trans = basic_dev.get_trans()
            output_dict["device_table"].append( [device_home,device_name,device_value,service_name,device_trans] )
        await sendPacketToWSClient(websocket,"give_list_basic_sensors",output_dict)
    # this event makes a HCD device and adds it to the list
    if eventName == "add_a_HCD":
        print("adding a new HCD "+str(packet["HCD_Name"]))
        device_name = packet["HCD_Name"]
        new_HCD = state["HCD"].HCDevice(device_name)
        numberOfHCDs = len(state["list_of_HCDs"])
        new_HCD.device_id = numberOfHCDs+1
        state["list_of_HCDs"].append(new_HCD)
    
    # client is asking for list of HCDS
    if eventName == "request_list_HCDs":
        output_dict = {}
        output_dict["device_table"] = []
        for HC_device in state["list_of_HCDs"]:
            HCD_bd_list = []
            for bd_name,bd_id in HC_device.device_listOfBDs:
                HCD_bd_list.append([bd_id,bd_name])
            device_name = HC_device.device_name
            device_state = HC_device.device_state
            device_id = HC_device.device_id
            alexa_control = HC_device.alexa_control
            output_dict["device_table"].append( [device_name,device_state,device_id,alexa_control,HCD_bd_list] )
        await sendPacketToWSClient(websocket,"give_list_HCDs",output_dict)
    # client is asking to add a BD to a HCD
    if eventName == "add_a_BD_to_HCD":
        device_id = packet["device_id"]
        device_home = packet["device_home"]
        device_name = packet["device_name"]
        for HC_device in state["list_of_HCDs"]:
            if str(HC_device.device_id) == str(device_id): # we found a match for the HCD
                for basic_dev in state["list_of_basicDevs"]:
                    bd_device_home = basic_dev.get_device_home()
                    bd_device_name = basic_dev.get_device_name()
                    bd_device_home_name = state["Service_ID_to_Name"][bd_device_home] #this dumb line converts the ID to the name since the webpage sends the name
                    if(str(bd_device_home_name).lower() == str(device_home).lower() and str(bd_device_name).lower() == str(device_name).lower()):
                        #found a match for the requested basic device
                        if basic_dev not in HC_device.device_listOfBDs:
                            HC_device.add_BD(bd_device_name,bd_device_home)
                            save_HCD(state) #save HCDS to file
    # client is asking to REMOVE a BD to a HCD
    if eventName == "remove_a_BD_to_HCD":
        device_id = packet["device_id"]
        device_home = packet["device_home"]
        device_name = packet["device_name"]
        for HC_device in state["list_of_HCDs"]:
            if str(HC_device.device_id) == str(device_id): # we found a match for the HCD
                for basic_dev in state["list_of_basicDevs"]:
                    bd_device_home = basic_dev.get_device_home()
                    bd_device_name = basic_dev.get_device_name()
                    if(str(bd_device_home).lower() == str(device_home).lower() and str(bd_device_name).lower() == str(device_name).lower()):
                        #found a match for the requested basic device
                        if [bd_device_name,bd_device_home] in HC_device.device_listOfBDs:
                            HC_device.remove_BD(bd_device_name,bd_device_home)
                            save_HCD(state) #save HCDS to file
    # client is trying to power a HCD
    if eventName == "HCD_power":
        desired_id = packet["device_id"]
        desired_state = packet["device_state"]                  
        for HC_device in state["list_of_HCDs"]:
            if str(HC_device.device_id) == str(desired_id): # we found a match for the HCD
                await HC_device.power(state,desired_state)
    #client wants to rename a HCD
    if eventName == "renameHCD":
        desired_id = packet["device_id"]
        device_new_name = packet["device_new_name"]                  
        for HC_device in state["list_of_HCDs"]:
            if str(HC_device.device_id) == str(desired_id): # we found a match for the HCD
                HC_device.device_name = device_new_name
                save_HCD(state) #save HCDS to file
    if eventName == "setAlexaHCD":
        desired_id = packet["device_id"]
        alexa_control = packet["alexa_control"]                  
        for HC_device in state["list_of_HCDs"]:
            if str(HC_device.device_id) == str(desired_id): # we found a match for the HCD
                HC_device.alexa_control = alexa_control
                save_HCD(state) #save HCDS to file
                