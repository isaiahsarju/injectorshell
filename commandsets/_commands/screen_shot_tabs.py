import cmd2
import argparse
import re
import os
import base64
from datetime import datetime
from cmd2 import CommandSet, with_argparser, with_category, with_default_category
from helperclass import helperclass
from helperclass.helperclass import HelperClass

_screen_shot_tabs_parser = cmd2.Cmd2ArgumentParser(parents=[HelperClass.parent_iunderstand])
_screen_shot_tabs_parser.add_argument('-r', '--regex', default = None, required = False,
                                    choices_provider = HelperClass.get_regex_names,
                                    type=str, help='regex for filtering tabs, alias or in line regex')
_screen_shot_tabs_parser.add_argument('-f', '--first', action ='store_true', required = False,
                                        help='flag to only execute on first target')
_screen_shot_tabs_parser.add_argument('-i', '--injector', required = True,
                                    choices_provider = HelperClass.get_injector_names,
                                    type=str, help='target ChromeInjector')
_screen_shot_tabs_parser.add_argument('-q', '--quality', default = None, type=int, choices=range(0,101), required = False,
                                        help='Quality between 0 and 100, will change type to jpg')
_screen_shot_tabs_parser.add_argument('-p', '--path', default = './.screenshots/', required = False,
                                type=str, help='path/to/outfolder/ (default ./.screenshots/)', completer=cmd2.Cmd.path_complete)
_screen_shot_tabs_parser.add_argument('-l', '--silent', action ='store_true', required = False,
                                        help='flag to execute silently and not print output')
_screen_shot_tabs_parser.add_argument('-e', '--timeout', default = None, type=int, required = False,
                                        help='timeout in seconds')
_screen_shot_tabs_parser.add_argument('-w', '--ws_url', default = None, type=str, required = False,
                                        help='ws_url of target instead of regex')
#_screen_shot_tabs_parser.add_argument('--iunderstand', action ='store_true', required = False,
#                                        help='flag to demonstrate that you understand warnings')
@cmd2.as_subcommand_to('exec', 'screen_shot_tabs', _screen_shot_tabs_parser)
def screen_shot_tabs(self, ns: argparse.Namespace):
    """Screenshot tabs and write out PNGs"""
    if not HelperClass.standard_validations(ws_url= ns.ws_url,
                                        regex_or_ws_url_required= True,
                                        regex= ns.regex,
                                        first= ns.first):
        self._cmd.pwarning("Validations failed, increase logging for verbosity")
        return
    elif ns.regex:
        regex = HelperClass.get_regex(ns.regex)
    else:
        regex = None
    if not ns.iunderstand:
        self._cmd.perror('This will end up switching tabs to capture screenshot, '+\
                            'there must not be any fullscreen GUI apps infront of target browser. '+\
                            'Use --iunderstand flag to demonstrate you understand this')
        if not ns.quality:
            self._cmd.pwarning('If you don\'t use -q/--quality the size may be too large and request will timeout. '+\
                            'Use --iunderstand flag to demonstrate you understand this')
        return
    ci = HelperClass.get_injector(ns.injector)
    if not ci:
        return
    if not os.path.isdir(ns.path) or not os.access(ns.path, os.W_OK):
        self._cmd.perror(f"Unable to write to '{ns.path}'")
        return
    if ns.quality:
        response = ci.cdp_capture_screenshot(regex=regex, first_target=ns.first,
                                             time=ns.timeout, ws_url=ns.ws_url,
                                             quality=ns.quality, tab_focus_back= True)
    else:
        response = ci.cdp_capture_screenshot(regex=regex,
                                            first_target=ns.first, time=ns.timeout,
                                            ws_url=ns.ws_url, tab_focus_back=True)
    if not response:
        return
    for url, data, tab_ws_url in response:
        if data:
            alpha_only = re.sub(r'\W+', '', url)
            time = datetime.now().strftime('%Y%m%d%H%M%S%f')
            if ns.quality:
                file_name = time + '-' + alpha_only + '.jpg'
            else:
                file_name = time + '-' + alpha_only + '.png'
            file_path = ns.path + file_name
            png = base64.b64decode(data)
            if not ns.silent:
                self._cmd.poutput(f"Writing screenshot for {url}:\n\t'{file_path}'")
            HelperClass.write_out(file_path, png, False, binary_mode=True)
