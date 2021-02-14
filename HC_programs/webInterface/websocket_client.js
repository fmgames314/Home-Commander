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
      // log data from server
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
          }else{
            basic_device_table.insertRow(1).innerHTML ='<td id="'+elementID+'_id">'+device_home+' ('+service_name+')</td><td id="'+elementID+'_name">'+device_name+'</td><td id="'+elementID+'_state" class="'+device_state_onoff+'">'+device_state_onoff+'</td>'
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
          var elementID = 'bs_'+device_home+'_'+(device_name.split(' ').join('_'));
          if ($("#"+elementID+"_id").length > 0) {
            // document.getElementById(elementID+"_id").innerHTML  = device_home
            document.getElementById(elementID+"_name").innerHTML  = device_name
            document.getElementById(elementID+"_state").innerHTML  = device_value
          }else{
            basic_device_table.insertRow(1).innerHTML ='<td id="'+elementID+'_id">'+device_home+' ('+service_name+')</td><td id="'+elementID+'_name">'+device_name+'</td><td id="'+elementID+'_state" class="sensor">'+device_value+'</td>'
          }
        }
      }


      
    } // end if it was json Data
}



var intervalVar = setInterval(websocketSenderLoop, 2000);
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






function sendData(){
  idd = window.prompt("Input ID Number", "");
  nn = window.prompt("Input New Name", "");
  outJSON = {
        event: "rename",
        holeNumber: idd,
        holeName: nn
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