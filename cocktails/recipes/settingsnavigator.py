import logging
import os
import coloredlogs
import time
from string import Template
from chromeinjector.chromeinjector import ChromeInjector
import sys
import re
from cocktails.cocktailshelper import CocktailsHelper
assert sys.version_info >= (3, 11)

class SettingsNavigator:
    """Used to execute JS that navigates
    DOM of chrome:// settings pages. Can
    also modify settings with JS
    """

    current_file_path = __file__
    current_directory = os.path.dirname(current_file_path)

    # JSs
    ret_func_template = Template("""function f(ret){return ret;};
    f($ret_var);""")

    list_passwords_js = CocktailsHelper.oneline_script(
        file_path=current_directory+'/settingsnavigator_js/list_passwords.js')

    get_site_rankings_js = CocktailsHelper.oneline_script(
        file_path=current_directory+'/settingsnavigator_js/get_site_rankings.js')

    get_history_js = CocktailsHelper.oneline_script(
        file_path=current_directory+'/settingsnavigator_js/get_history.js')

    # Dict of actions to dicts of (page, JS, description, final_js)
    actions_dict = {'list_passwords':
                        {"page": "chrome://password-manager/passwords",
                         "js": list_passwords_js,
                         "final_js": ret_func_template.substitute(ret_var="pwLabels"),
                         "description":"Get sites available in DOM of chrome://password-manager/passwords"},
                    'get_rankings':
                        {"page":"chrome://site-engagement/",
                        "js": get_site_rankings_js,
                        "final_js": ret_func_template.substitute(ret_var="rankings_table"),
                        "description": "Get site rankings from DOM of chrome://site-engagement/"},
                    'get_history':
                        {"page": "chrome://history",
                        "js": get_history_js,
                        "final_js": ret_func_template.substitute(ret_var="urlArray"),
                        "description": "Get history from DOM of chrome://history"}}

    @classmethod
    def get_actions(cls, *__) -> list:
        """Return keys and descriptions of actions dict"""
        return list(cls.actions_dict.keys())

    @classmethod
    def get_actions_desc(cls) -> dict:
        """Return keys and descriptions of actions dict"""
        keys_desc = {}
        for key, attributes in cls.actions_dict.items():
            description = attributes["description"]
            keys_desc[key] = description
        return keys_desc

    @classmethod
    def exec_action(cls, injector: ChromeInjector,
                    action_name: str = None,
                    sleep: float = 0.0,
                    pre_script_sleep: float = 0.0,
                    pre_sleep: float = 0.0,
                    new_window: bool = False,
                    background: bool = False,
                    switch_tabs: bool = False,
                    script_exec_time: float = 0.0) -> tuple:
        """Uses JS to navigate and change settings
        return tuple of result of JS execution

        Keyword arguments:
        injector -- ChromeInjector instance
        action_name -- string of action to perform (default: None)
        pre_sleep -- float of sleep time to let initial page load (default: 0.0)        
        sleep -- float of sleep time to stay on page (default: 0.0)
        pre_script_sleep -- float of sleep (after pre_sleep and/or sleep) to wait to begin script exec (default: 0.0)
        new_window -- bool flag to open in new window or not (default: False)
        background -- bool flag to open backgrounded or not (default: False)
        switch_tabs -- bool flag to switch to new tab to let load (default: False)
        script_exec_time -- time to allow script execution prior to final value retrieval (default 0.0)
        """
        logger = logging.getLogger(__name__)
        if not action_name:
            logger.error("requires an action")
            return None

        action = cls.actions_dict[action_name]

        ws_url, target_id = CocktailsHelper.prepare_new_page(injector, action["page"],
                        pre_sleep=pre_sleep,
                        sleep=sleep, final_sleep=pre_script_sleep,
                        new_window=new_window,
                        switch_tabs=switch_tabs, background=background)
        results = injector.cdp_eval_script(action["js"], ws_url= ws_url, returnBV = True, silent= True)
        if script_exec_time:
            logger.info(f"Allowing script exec for {script_exec_time}s")
            time.sleep(script_exec_time)
        results = injector.cdp_eval_script(action["final_js"], ws_url= ws_url, returnBV = True)
        injector.cdp_close_window(target_id)
        return results

