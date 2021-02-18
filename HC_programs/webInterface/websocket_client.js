//setup the connection for websocket

console.log("Connecting to ws://" + document.domain + ":1997/")
const webSockObj = new WebSocket("ws://" + document.domain + ":1997/");
console.log(webSockObj)
// const webSockObj = new WebSocket("ws://192.168.1.202:1997/");
webSockObj.addEventListener("message", function(event) {
  processWebsocketData(event.data);
});



var listOfHoles = {};
var gotGoodData = false;
var logData = [];

function processWebsocketData(data) {
    //data comes out of web socket from data
    if (IsJsonString(data) == true) {
      var jsonData = JSON.parse(data);
      // console.log(jsonData)
      // check what event came in from the server
      var eventName = jsonData["event"]; 
      // List Of Basic Devices from server
      if(eventName == "give_list_basic_devices"){
        var device_table = jsonData["device_table"]; 
        basic_device_table = document.getElementById("basic_devices")
        for (var i = 0; i < device_table.length; i+=1) {
          var device_home =  device_table[i][0]
          var device_name =  device_table[i][1]
          var device_state =  device_table[i][2]
          var service_name = device_table[i][3]
          var device_state_onoff =  "ON" 
          if(device_state == false){device_state_onoff =  "OFF"}
          var elementID = 'bd_'+device_home+'_'+(device_name.split(' ').join('_'));
          if ($("#"+elementID+"_id").length > 0) {
            // document.getElementById(elementID+"_id").innerHTML  = device_home
            document.getElementById(elementID+"_name").innerHTML  = device_name
            document.getElementById(elementID+"_state").innerHTML  = device_state_onoff
            document.getElementById(elementID+"_state").className = device_state_onoff
          }else{
            basic_device_table.insertRow(1).innerHTML ='<td id="'+elementID+'_id">'+device_home+' ('+service_name+')</td><td id="'+elementID+'_name">'+device_name+'</td><td id="'+elementID+'_state" class="'+device_state_onoff+'">'+device_state_onoff+'</td>'
            clickable_name =  document.getElementById(elementID+'_name')
            clickable_name.setAttribute("onclick",'addBDtoHD("'+service_name+'","'+device_name+'");');
            clickable_name.className = "clickable_name"
          }
        }
      }
      // SENSORS FROM SERVER
      if(eventName == "give_list_basic_sensors"){
        var device_table = jsonData["device_table"]; 
        basic_device_table = document.getElementById("basic_sensors")
        for (var i = 0; i < device_table.length; i+=1) {
          var device_home =  device_table[i][0]
          var device_name =  device_table[i][1]
          var device_value =  device_table[i][2]
          var service_name = device_table[i][3]
          var hc_use = device_table[i][4]
          var elementID = 'bs_'+device_home+'_'+(device_name.split(' ').join('_'));
          if ($("#"+elementID+"_id").length > 0) {
            // document.getElementById(elementID+"_id").innerHTML  = device_home
            document.getElementById(elementID+"_name").innerHTML  = device_name
            document.getElementById(elementID+"_state").innerHTML  = device_value
            document.getElementById(elementID+"_hcUse").innerHTML  = hc_use
          }else{
            basic_device_table.insertRow(1).innerHTML ='<td id="'+elementID+'_id">'+device_home+' ('+service_name+')</td><td id="'+elementID+'_name">'+device_name+'</td><td id="'+elementID+'_state" class="sensor">'+device_value+'</td><td id="'+elementID+'__hcUse" class="hcUse">'+hc_use+'</td>'
          }
        }
      }
      // List Of Home Commander Devices 
      if(eventName == "give_list_HCDs"){
        var device_table = jsonData["device_table"]; 
        HCDs_table = document.getElementById("home_commander_device")
        for (var i = 0; i < device_table.length; i+=1) {
          var device_name =  device_table[i][0]
          var device_state =  device_table[i][1]
          var device_id =  device_table[i][2]
          var alexa_control = device_table[i][3]
          var HCD_bd_list = device_table[i][4]
          var device_state_onoff =  device_state
          if(device_state == true){device_state_onoff =  "ON"}
          if(device_state == false){device_state_onoff =  "OFF"}
          if(device_state > 0 && device_state < 1){device_state_onoff = "PERCENT"}

          var elementID = 'hcd_'+device_id
          if ($("#"+elementID+"_id").length > 0) {
            //name
            HCD_Name = document.getElementById(elementID+"_name")
            HCD_Name.innerHTML  = device_name
            HCD_Name.setAttribute("onclick",'renameHCD("'+device_id+'");');
            HCD_Name.className = "clickable_renamer"
            // set stuff for the power state
            HCD_state = document.getElementById(elementID+"_state")
            if(device_state_onoff == "PERCENT"){ // has a percent
              HCD_state.innerHTML  = parseInt(device_state*100)+"%"
              var onOrOff = 0;
              if(device_state >= .5){onOrOff = 1}
              HCD_state.setAttribute("onclick",'powerDevice("'+device_id+'",'+onOrOff+');');
            }else{ // just on or off
              HCD_state.innerHTML  = device_state_onoff
              HCD_state.setAttribute("onclick",'powerDevice("'+device_id+'",'+!device_state+');');
            }
            HCD_state.className = device_state_onoff
            
            // itterate over list items and add if no in there
            bds_cell = document.getElementById(elementID+"_bds")
            // go over list of basic devices in HCD
            bds_cell.innerHTML = ""
            for (var j = 0; j < HCD_bd_list.length; j+=1) {
                var li = document.createElement("li");
                li.innerHTML = HCD_bd_list[j][0]+"_"+HCD_bd_list[j][1]
                li.className = "clickable_removal"
                li.setAttribute("onclick",'removeBDtoHD("'+HCD_bd_list[j][0]+'","'+HCD_bd_list[j][1]+'",'+device_id+');');
                bds_cell.appendChild(li);
            }
            
            // Alexa rename
            HCD_Alexa = document.getElementById(elementID+"_alexa")
            HCD_Alexa.innerHTML  = alexa_control
            HCD_Alexa.setAttribute("onclick",'setAlexaHCD("'+device_id+'",'+!alexa_control+');');
            HCD_Alexa.className = "alexa_"+alexa_control
          
            //row doesn't even exist, add it 
          }else{
            //create row
            var current_row = HCDs_table.insertRow(-1)
            //create cell ID           
            var cell = current_row.insertCell(-1)
            cell.id = elementID+"_id"
            cell.innerHTML = device_id            
            //create cell name
            var cell = current_row.insertCell(-1)
            cell.id = elementID+"_name"
            cell.innerHTML = device_name 
            //create cell with list of devices controled 
            var cell = current_row.insertCell(-1)
                  // go over list of basic devices in HCD
                  var ul_element = document.createElement("ul");
                  for (var i = 0; i < HCD_bd_list.length; i+=1) {
                      var li = document.createElement("li");
                      li.innerHTML = HCD_bd_list[i][0]+"_"+HCD_bd_list[i][1]
                      ul_element.appendChild(li);
                  }
                  //finall appent the list to the cell element
                  cell.appendChild(ul_element);
            cell.id = elementID+"_bds"
            // cell.innerHTML = "add list of devices here"
            //create cell alexa control
            var cell = current_row.insertCell(-1)
            cell.id = elementID+"_alexa"
            cell.innerHTML = alexa_control
            //create cell state
            var cell = current_row.insertCell(-1)
            cell.id = elementID+"_state"
            cell.innerHTML = device_state_onoff
            cell.className = device_state_onoff
          }
        }
      }






      
    } // end if it was json Data
}


var intervalVar1 = setInterval(websocketSenderLoop, 4000);
var intervalVar2 = setInterval(request_HCD_List, 500);

function websocketSenderLoop() {
    outJSON = {
        event: "request_list_basic_devices",
    }
    webSockObj.send(JSON.stringify(outJSON));
    outJSON = {
        event: "request_list_basic_sensors",
    }
    webSockObj.send(JSON.stringify(outJSON));
}

function request_HCD_List(){
    outJSON = {
        event: "request_list_HCDs",
    }
    webSockObj.send(JSON.stringify(outJSON));
}



function renameHCD(device_id){
   device_new_name = window.prompt("Enter HCD Name", "");
  outJSON = {
        event: "renameHCD",
        device_id: device_id,
        device_new_name: device_new_name,
    }
  webSockObj.send(JSON.stringify(outJSON));
  request_HCD_List()
}
function setAlexaHCD(device_id,alexa_state){
  outJSON = {
        event: "setAlexaHCD",
        device_id: device_id,
        alexa_control: alexa_state,
    }
  webSockObj.send(JSON.stringify(outJSON));
  request_HCD_List()
}


function addBDtoHD(device_home,device_name){
   device_id = window.prompt("Enter HCD ID", "");
  outJSON = {
        event: "add_a_BD_to_HCD",
        device_id: device_id,
        device_home: device_home,
        device_name: device_name,
    }
  webSockObj.send(JSON.stringify(outJSON));
  request_HCD_List()
}

function removeBDtoHD(device_home,device_name,device_id){
  outJSON = {
        event: "remove_a_BD_to_HCD",
        device_id: device_id,
        device_home: device_home,
        device_name: device_name,
    }
  webSockObj.send(JSON.stringify(outJSON));
  request_HCD_List()
}

function create_a_HCD(){
  nn = window.prompt("Input New Name", "");
  outJSON = {
        event: "add_a_HCD",
        HCD_Name: nn,
    }
  webSockObj.send(JSON.stringify(outJSON));
  request_HCD_List()
}

function powerDevice(device_id,device_state){
  outJSON = {
        event: "HCD_power",
        device_id: device_id,
        device_state: device_state,
    }
  webSockObj.send(JSON.stringify(outJSON));
  request_HCD_List()
}


function add_xbee_device(){
  console.log("adding device")
  var device_name = document.getElementById("box_device_name").value;
  var device_on_command = document.getElementById("box_device_on_command").value;
  var device_off_command = document.getElementById("box_device_off_command").value;
  outJSON = {
        event: "add_xbee_device",
        device_name: device_name,
        device_on_command: device_on_command,
        device_off_command: device_off_command,
    }
  webSockObj.send(JSON.stringify(outJSON));
}




function IsJsonString(str) {
    try {
      JSON.parse(str);
    } catch (e) {
      return false;
    }
    return true;
  }