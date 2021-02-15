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

  def add_BD(self,basic_dev):
    self.device_listOfBDs.append(basic_dev)
  def remove_BD(self,basic_dev):
    self.device_listOfBDs.remove(basic_dev)

  