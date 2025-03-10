import cmd2
import argparse
from cmd2 import CommandSet, with_argparser, with_category, with_default_category
from helperclass import helperclass
from helperclass.helperclass import HelperClass

_eval_script_parser = cmd2.Cmd2ArgumentParser()
_eval_script_parser.add_argument('-s', '--script', default = None, required = True,
                                    choices_provider = HelperClass.get_script_names,
                                    type=str, help='script name')
_eval_script_parser.add_argument('-i', '--injector', required = True,
                                    choices_provider = HelperClass.get_injector_names,
                                    type=str, help='target ChromeInjector')
_eval_script_parser.add_argument('-r', '--regex', default = None, required = False,
                                    choices_provider = HelperClass.get_regex_names,
                                    type=str, help='regex for filtering tabs, alias or in line regex')
_eval_script_parser.add_argument('-f', '--first', action ='store_true', required = False,
                                        help='flag to only execute on first target')
_eval_script_parser.add_argument('-p', '--path', default = None, required = False,
                                type=str, help='path to outfile', completer=cmd2.Cmd.path_complete)
_eval_script_parser.add_argument('-o', '--overwrite', action ='store_true', required = False,
                                        help='flag to overwrite previously written out file')
_eval_script_parser.add_argument('-l', '--silent', action ='store_true', required = False,
                                        help='flag to execute silently and not print output')
_eval_script_parser.add_argument('-e', '--timeout', default = None, type=int, required = False,
                                        help='timeout in seconds')
_eval_script_parser.add_argument('-w', '--ws_url', default = None, type=str, required = False,
                                        help='ws_url of target instead of regex')
_eval_script_parser.add_argument('-v', '--returnBV', default = False, required = False, action ='store_true',
                                        help='Whether the result is expected to be a JSON object')
@cmd2.as_subcommand_to('exec', 'eval_script', _eval_script_parser)
def eval_script(self, ns: argparse.Namespace):
    """Execute script via ChromeInjector"""

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

    ci = HelperClass.get_injector(ns.injector)
    if not ci:
        return
    script = HelperClass.get_script(ns.script)
    if not script:
        return

    response = ci.cdp_eval_script(script, regex=regex, first_target=ns.first, time=ns.timeout, ws_url=ns.ws_url, returnBV=ns.returnBV)
    HelperClass.write_out(ns.path, str(response), ns.overwrite)
    if not ns.silent and response:
        self._cmd.poutput(f"Response:\n{response}")