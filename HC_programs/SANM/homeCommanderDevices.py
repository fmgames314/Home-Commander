class HCDevice:
  device_name = 0
  device_state = 0
  device_listOfBDs = []
  device_id = 0
  alexa_control = True

  def __init__(self, device_name):
    self.device_name = device_name

  def get_device_state(self):
    return self.device_state
  def set_device_state(self,device_state):
    self.device_state = device_state

   