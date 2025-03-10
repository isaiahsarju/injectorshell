/* URI to GET. Be aware of Content security policy*/
let ping = 'https://example.com/doesntexist.png';

let site_location = window.location.href;

new Image().src = ping;