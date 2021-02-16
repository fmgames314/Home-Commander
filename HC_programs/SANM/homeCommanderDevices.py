
class HCDevice:

  def __init__(self, device_name):
    self.device_name = device_name
    self.device_listOfBDs = []
    self.device_state = False
    self.device_id = 0
    self.alexa_control = True

  def get_device_state(self):
    return self.device_state
  def set_device_state(self,device_state):
    self.device_state = device_state

  def add_BD(self,bd_name,bd_id):
    self.device_listOfBDs.append([bd_name,bd_id])
  def remove_BD(self,bd_name,bd_id):
    self.device_listOfBDs.remove([bd_name,bd_id])

  async def power(self,state,desired_state):
    for bd_name,bd_id in self.device_listOfBDs:
      try:
        basic_dev = state["SE"].find_or_create_basic_device(state,bd_id,bd_name)
        await basic_dev.power(state,desired_state)
      except:
        print("FAILED TO POWER DEVICE")
          

    
  def calculate_state(self,state):
    numOfItems = len(self.device_listOfBDs)
    if numOfItems > 0:
      countTheOn = 0
      for bd_name,bd_id in self.device_listOfBDs:
        basic_dev = state["SE"].find_or_create_basic_device(state,bd_id,bd_name)
        countTheOn+=int(basic_dev.get_device_state())
      self.device_state = round((countTheOn/numOfItems),2)
    else:
      self.device_state = 0

  def alexa_make_string(self):
    configFileOutput = ""
    if self.alexa_control == 1:
      selfServerURL = "http://127.0.0.1:1998/"   
      configFileOutput += """{
          "port": \""""+str(12340+self.device_id)+"""\",
          "on_cmd": \""""+selfServerURL+str(self.device_id)+"/1"+"""\",
          "off_cmd": \""""+selfServerURL+str(self.device_id)+"/0"+"""\",
          "method": "GET",
          "name": \""""+str(self.device_name)+"""\",
          "state_cmd": \""""+selfServerURL+str(self.device_id)+"/2"+"""\",
          "state_method": "GET",
          "state_data": {
          "get_switch_state": "give"
          },
          "state_response_on": "1",
          "state_response_off": "0"
      },"""
    return configFileOutput



