import cmd2
import argparse
from cmd2 import CommandSet, with_argparser, with_category, with_default_category
from helperclass import helperclass
from helperclass.helperclass import HelperClass

_list_tabs_parser = cmd2.Cmd2ArgumentParser()  
_list_tabs_parser.add_argument('-i', '--injector', required = True,
                                    choices_provider = HelperClass.get_injector_names,
                                    type=str, help='target ChromeInjector')
_list_tabs_parser.add_argument('-p', '--path', default = None, required = False,
                                type=str, help='path to outfile', completer=cmd2.Cmd.path_complete)
_list_tabs_parser.add_argument('-o', '--overwrite', action ='store_true', required = False,
                                        help='flag to overwrite previously written out file')
_list_tabs_parser.add_argument('-l', '--silent', action ='store_true', required = False,
                                        help='flag to execute silently and not print output')
@cmd2.as_subcommand_to('exec', 'list_tabs', _list_tabs_parser)
def list_tabs(self, ns:argparse.Namespace):
    """List open tabs and windows"""
    ci = HelperClass.get_injector(ns.injector)
    if not ci:
        return
    response = ci.cdp_get_open_tabs()
    HelperClass.write_out(ns.path, str(response), ns.overwrite)
    if not ns.silent and response:
        self._cmd.poutput(f"Tabs:")
        for tab in response:
            win_type = tab['type']
            title = tab['title']
            url = tab['url']
            ws_url = ci.generate_ws_url(tab['targetId'])
            self._cmd.poutput(f"[{win_type}] {title}:\n\t{url}\n\t{ws_url}")