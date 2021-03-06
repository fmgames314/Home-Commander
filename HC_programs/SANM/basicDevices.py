class basicDevice:
  

  def __init__(self, device_home, device_name, service_name):
    self.device_name = device_name
    self.device_home = device_home
    self.device_home_name = service_name
    self.device_state = 0

  def get_device_home(self):
    return self.device_home
  def get_device_name(self):
    return self.device_name

  def get_device_state(self):
    return self.device_state
  def set_device_state(self,device_state):
    self.device_state = device_state

  def get_service_name(self):
    return self.device_home_name 
   
  async def power(self,state,desired_state):
    #find the right websockets to send too
    websocket = state["dict_of_devAddress"][self.device_home]
    # load the json
    output_dict = {}
    output_dict["power_state"] = int(desired_state)
    output_dict["device_name"] = self.device_name
    #send packet
    await state["SE"].sendPacketToWSClient(websocket,"control",output_dict)

    



class basicSensor:
  

  def __init__(self, device_home, device_name, service_name):
    self.device_name = device_name
    self.device_home = device_home
    self.device_home_name = service_name
    self.device_value = 0
    self.transmit = 1

  def get_device_home(self):
    return self.device_home
  def get_device_name(self):
    return self.device_name

  def get_device_value(self):
    return self.device_value
  def set_device_value(self,device_value):
    self.device_value = device_value
    
  def get_service_name(self):
    return self.device_home_name 

  def get_trans(self):
    return self.transmit
  def set_trans(self):
    return self.transmit
