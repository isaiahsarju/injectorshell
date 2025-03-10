/* Regex to test window.location.href */
let re = new RegExp('mozilla');
/* URI to GET. Be aware of Content security policy*/
let ping = 'https://example.com/doesntexist.png';

let site_location = window.location.href;

if(re.test(site_location)) {
        new Image().src = ping;
    };