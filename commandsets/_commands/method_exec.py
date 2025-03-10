import cmd2
import argparse
from cmd2 import CommandSet, with_argparser, with_category, with_default_category
from helperclass import helperclass
from helperclass.helperclass import HelperClass
import json

# Execute CDP method via CI
_method_exec_parser = cmd2.Cmd2ArgumentParser()
_method_exec_parser.add_argument('-r', '--regex', default = None, required = False,
                                    choices_provider = HelperClass.get_regex_names,
                                    type=str, help='regex for filtering tabs, alias or in line regex')
_method_exec_parser.add_argument('-f', '--first', action ='store_true', required = False,
                                        help='flag to only execute on first target')
_method_exec_parser.add_argument('-i', '--injector', required = True,
                                    choices_provider = HelperClass.get_injector_names,
                                    type=str, help='target ChromeInjector')
_method_exec_parser.add_argument('-m', '--method', required = True,
                                    type=str, help='method to execute (e.g. Page.reload)')
_method_exec_parser.add_argument('-a', '--params', required = False, default = None,
                                    type=str, help='optional JSON of params ' +
                                    '(e.g. {"ignoreCache":true, "scriptToEvaluateOnLoad":"alert(1)"}')
_method_exec_parser.add_argument('-w', '--ws_url', default = None, type=str, required = False,
                                        help='ws_url of target instead of regex')
_method_exec_parser.add_argument('-p', '--path', default = None, required = False,
                                type=str, help='path to outfile', completer=cmd2.Cmd.path_complete)
_method_exec_parser.add_argument('-o', '--overwrite', action ='store_true', required = False,
                                        help='flag to overwrite previously written out file')
_method_exec_parser.add_argument('-l', '--silent', action ='store_true', required = False,
                                        help='flag to execute silently and not print output')
_method_exec_parser.add_argument('-e', '--timeout', default = None, type=int, required = False,
                                        help='timeout in seconds')
@cmd2.as_subcommand_to('exec', 'method_exec', _method_exec_parser)
def method_exec(self, ns: argparse.Namespace):
    """Execute CDP method (with parameters)"""
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
    if ns.params and not HelperClass.validate_json(ns.params):
        self._cmd.perror("Invalid JSON")
        return
    elif ns.params:
        response = ci.cdp_method_exec(ns.method, cdp_params=json.loads(ns.params),\
                                        regex=regex, first_target=ns.first, time=ns.timeout, ws_url=ns.ws_url)
        HelperClass.write_out(ns.path, str(response), ns.overwrite)
        if not ns.silent and response:
            self._cmd.poutput(f"Response:\n{response}")
    else:
        response = ci.cdp_method_exec(ns.method, regex=regex, first_target=ns.first, time=ns.timeout, ws_url=ns.ws_url)
        HelperClass.write_out(ns.path, str(response), ns.overwrite)
        if not ns.silent and response:
            self._cmd.poutput(f"Response:\n{response}")