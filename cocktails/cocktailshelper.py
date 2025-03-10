import logging
import coloredlogs
from chromeinjector.chromeinjector import ChromeInjector
import time
import re

class CocktailsHelper:
    """Helper Class for the cocktails"""

    @classmethod
    def oneline_script(cls, file_path):
        """Returns script file as oneliner or return None if error"""
        logger = logging.getLogger(__name__)
        try:
            with open(file_path, 'r') as script_file:
                try:
                    script = script_file.read()
                except Exception as e:
                    raise e
                finally:
                    script_file.close()
                    logger.debug(f"Script is:\n{script}")
                    script_regex = re.compile("(\n|([ ]{2,}))")
                    new_script = script_regex.sub(" ",script)
                    return new_script
        except Exception as e:
            logger.error(f"Unable to open js file: {e}")
            logger.error("Returing None")
            return None

    @classmethod
    def key_press(cls, injector: ChromeInjector,
                        nativeVirtualKeyCode: int,
                        down: bool = True,
                        up: bool = True,
                        windowsVirtualKeyCode: int = None,
                        regex: re.Pattern = None,
                        first_target: bool = False,
                        ws_url: str = None):
        """Simulate key down or up press event
        
        Keyword arguments:
        injector -- ChromeInjector
        nativeVirtualKeyCode -- Native virtual key code int
        down -- bool to send down press (default: True)
        up -- bool to send up press (default: True)
        windowsVirtualKeyCode -- Windows virtual key code int (default: None)
        ws_url -- string of WS URL to execute on (default: None)
        regex -- regex of target tab (default: None)
        first_target -- only execute on first target (default: False)
        """
        logger = logging.getLogger(__name__)
        if not (down or up):
            logger.error("Requires up or down keypress")
            return

        if not windowsVirtualKeyCode:
            logger.info("Syncing windowsVirtualKeyCode with nativeVirtualKeyCode")
            windowsVirtualKeyCode = nativeVirtualKeyCode
        elif windowsVirtualKeyCode != nativeVirtualKeyCode:
            logger.warning("Key codes not the same!")

        method = "Input.dispatchKeyEvent"
        if down:
            params = {"type":"keyDown",
                    "nativeVirtualKeyCode": nativeVirtualKeyCode,
                    "windowsVirtualKeyCode": windowsVirtualKeyCode}
            injector.cdp_method_exec(method,
                                    cdp_params = params,
                                    regex=regex,
                                    first_target=first_target,
                                    ws_url=ws_url)

        if up:
            params = {"type":"keyUp",
                    "nativeVirtualKeyCode": nativeVirtualKeyCode,
                    "windowsVirtualKeyCode": windowsVirtualKeyCode}
            injector.cdp_method_exec(method,
                                    cdp_params = params,
                                    regex=regex,
                                    first_target=first_target,
                                    ws_url=ws_url)

    @classmethod
    def mouse_click(cls, injector: ChromeInjector,
                        x: int = 1,
                        y: int = 1,
                        down: bool = True,
                        up: bool = True,
                        regex: re.Pattern = None,
                        first_target: bool = False,
                        ws_url: str = None):
        """Simulate mouse click down or up  event
        
        Keyword arguments:
        injector -- ChromeInjector
        x -- X cooridnate of view port (default: 1)
        y -- Y cooridnate of view port (default: 1)
        down -- bool to send down press (default: True)
        up -- bool to send up press (default: True)
        ws_url -- string of WS URL to execute on (default: None)
        regex -- regex of target tab (default: None)
        first_target -- only execute on first target (default: False)
        """
        logger = logging.getLogger(__name__)
        if not (down or up):
            logger.error("Requires up or down keypress")
            return


        method = "Input.dispatchMouseEvent"
        if down:
            params = {"type":"mousePressed",
                    "x": x,
                    "y": y}
            injector.cdp_method_exec(method,
                                    cdp_params = params,
                                    regex=regex,
                                    first_target=first_target,
                                    ws_url=ws_url)

        if up:
            params = {"type":"mouseReleased",
                    "x": x,
                    "y": y}
            injector.cdp_method_exec(method,
                                    cdp_params = params,
                                    regex=regex,
                                    first_target=first_target,
                                    ws_url=ws_url)

    @classmethod
    def prepare_new_page(cls, injector: ChromeInjector,
                    url: str,
                    pre_sleep: float = 0.0,
                    sleep: float = 0.0,
                    final_sleep: float = 0.0,
                    new_session: bool = False,
                    new_window: bool = False,
                    background: bool = False,
                    switch_tabs: bool = False) -> str:
        """ Prepares a new page for DOM traversal and returns
        a ws_url, and target_id

        Keyword arguments:

        injector -- ChromeInjector instance
        url -- string of url to open in new tab or new window
        pre_sleep -- float of sleep time to let initial page load (default: 0.0)        
        sleep -- float of sleep time to stay on page (default: 0.0)
        final_sleep -- float of sleep (after pre_sleep and/or sleep) to wait (default: 0.0)
        new_session -- open new page in new session (default: False))
        new_window -- bool flag to open in new window or not (default: False)
        background -- bool flag to open backgrounded or not (default: False)
        switch_tabs -- bool flag to switch to new tab to let load (default: False)
        """
        logger = logging.getLogger(__name__)

        if new_session:
            logger.warning('New session not yet implemented')

        target_id = None
        original_ws = None
        if switch_tabs or new_window:
            # Only need to enum if new tab is switched to
            # Or we need to switch back from a new_window
            original_tab = injector.get_current_tab()
            original_target = original_tab.get('targetId')
            original_ws = injector.generate_ws_url(original_target)
        #Open new tab or window get ws_url. Always start backgrounded
        ws_url, target_id = injector.cdp_new_window(url,
                                background = background, new_window=new_window)

        # If opened with new window need to force switch back
        if new_window:
            logger.info(f"Opened new window, and switching back")
            injector.switch_tabs(original_ws)

        # let page load for pre_sleep time
        if bool(pre_sleep):
            logger.info(f"Letting page load for {pre_sleep}s")
            time.sleep(pre_sleep)

        # If for some reason you want to switch tabs (e.g. kick of page load)
        if bool(switch_tabs):
            injector.switch_tabs(ws_url)
            if(sleep):
                logger.info(f"Staying on target page for {pre_sleep}s")
                time.sleep(sleep)

        # Send tab event on new page to activate filling of page
        logger.info("Sending tab keystroke to new page")
        cls.key_press(injector, 9, ws_url=ws_url)
        # Send mouse click event on new page to activate filling of page
        logger.info("Sending mouse click to new page")
        cls.mouse_click(injector, ws_url=ws_url)

        # Switch back if we switched
        if bool(switch_tabs):
            injector.switch_tabs(original_ws)
        
        # Wait this time before executing scripts
        if bool(final_sleep):
            logger.info(f"Letting page load for {pre_sleep}s "+\
                        "before continuing execution")
            time.sleep(final_sleep)

        return ws_url, target_id