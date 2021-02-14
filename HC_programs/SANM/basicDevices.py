class basicDevice:
  device_state = 0

  def __init__(self, device_home, device_name, service_name):
    self.device_name = device_name
    self.device_home = device_home
    self.device_home_name = service_name

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
   


class basicSensor:
  device_value = 0

  def __init__(self, device_home, device_name, service_name):
    self.device_name = device_name
    self.device_home = device_home
    self.device_home_name = service_name

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

