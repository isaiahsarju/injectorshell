import cmd2
import argparse
from cmd2 import CommandSet, with_argparser, with_category, with_default_category
from helperclass import helperclass
from helperclass.helperclass import HelperClass

_close_tab_parser = cmd2.Cmd2ArgumentParser()
_close_tab_parser.add_argument('-i', '--injector', required = True,
                                    choices_provider = HelperClass.get_injector_names,
                                    type=str, help='target ChromeInjector'),
_close_tab_parser.add_argument('-t', '--target', default = None, type=str, required = True,
                                        help='targetID of tab to close (UUID of ws_url)')
_close_tab_parser.add_argument('-l', '--silent', action ='store_true', required = False,
                                        help='flag to execute silently and not print output')
@cmd2.as_subcommand_to('exec', 'close_tab', _close_tab_parser)
def close_tab(self, ns: argparse.Namespace):
    """Close chrome tab"""
    ci = HelperClass.get_injector(ns.injector)
    if not ci:
        return
    response = ci.cdp_close_window(ns.target)
    if not ns.silent and response:
        self._cmd.poutput("Tab succesfully closed")
    elif not ns.silent and not response:
        self._cmd.perror("Tab NOT succesfully closed")