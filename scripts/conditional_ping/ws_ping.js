/* WS ping addr */
var ws_addr = 'ws://localhost:8080';
/* Regex to test window.location.href */
let re = new RegExp('w3');

var site_location = window.location.href;

if(re.test(site_location)) {
    ws = new WebSocket(ws_addr);
    ws.onopen = function() {
        /* Web Socket is connected, send data using send()*/
        ws.send(site_location);
    };
};