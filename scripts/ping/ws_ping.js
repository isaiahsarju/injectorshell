/* WS ping addr */
let ws_addr = 'ws://localhost:8080';
/* URI to GET. Be aware of Content security policy*/

var site_location = window.location.href;

ws = new WebSocket(ws_addr);
    ws.onopen = function() {
        /* Web Socket is connected, send data using send()*/
        ws.send(site_location);
    };