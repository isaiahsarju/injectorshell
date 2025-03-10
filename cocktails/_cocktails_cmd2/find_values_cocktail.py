import cmd2
import argparse
from cmd2 import CommandSet, with_argparser, with_category, with_default_category
from helperclass import helperclass
from helperclass.helperclass import HelperClass
from cocktails.recipes.findvalues import FindValues

_find_values_parser = cmd2.Cmd2ArgumentParser(parents=[HelperClass.parent_iunderstand])
_find_values_parser.add_argument('-i', '--injector', required = True,
                                    choices_provider = HelperClass.get_injector_names,
                                    type=str, help='target ChromeInjector'),
_find_values_parser.add_argument('-t', '--inputs', required = False,
                                    type=str, nargs='+', default = None,
                                    help='Inputs to look for. Use -e/--exact_input to '+
                                    'limit inputs to exact name')
_find_values_parser.add_argument('-u', '--url', default = None, type=str, required = False,
                                        help='target url to open')
_find_values_parser.add_argument('-e', '--exact_input', action ='store_true', required = False,
                                        help='flag to limit inputs to exact name')
_find_values_parser.add_argument('-c', '--switch_tabs', action ='store_true', default = False,
                                        required = False,
                                        help='flag to switch tabs after opening URL (e.g. let load). '+
                                            'Use with -s/--sleep')
_find_values_parser.add_argument('-n', '--new_window', action ='store_true', required = False,
                                        help='flag to open target page in new window')
_find_values_parser.add_argument('-b', '--background', action ='store_true', required = False,
                                        help='flag to open settings page backgrounded')
_find_values_parser.add_argument('-o', '--new_session', action ='store_true', required = False,
                                        help='flag to open target page in new session (e.g. to get passwords from logon page)')
_find_values_parser.add_argument('-p', '--pre_sleep', default = None, type=float, required = False,
                                        help='sleep time before switch to allow load')
_find_values_parser.add_argument('-s', '--sleep', default = None, type=float, required = False,
                                        help='sleep time after tab switch to force load.  '+
                                            'Use with -c/--switch_tabs')
_find_values_parser.add_argument('-l', '--pre_script_sleep', default = None, type=float, required = False,
                                        help='sleep time (after pre_sleep)(and/or after sleep) to allow load')
_find_values_parser.add_argument('-r', '--regex', default = None, required = False,
                                    choices_provider = HelperClass.get_regex_names,
                                    type=str, help='regex for filtering tabs, alias or in line regex')
_find_values_parser.add_argument('-f', '--first_target', action ='store_true', required = False,
                                        help='flag to execute on first target found with regex')
_find_values_parser.add_argument('-w', '--ws_url', default = None, type=str, required = False,
                                        help='ws_url of target instead of regex')
@cmd2.as_subcommand_to('exec_cocktails', 'find_values_cocktail', _find_values_parser)
def find_values_cocktail(self, ns: argparse.Namespace):
    """Uses JS to find values on page. Hint what does auto-fill fill ;-) ?
    """
    if not HelperClass.standard_validations(iunderstand=ns.iunderstand,
                                            background=ns.background,
                                            new_window=ns.new_window):
        self._cmd.pwarning("Validations failed, increase logging for verbosity")
        answer = self._cmd.read_input("Do you want to continue? (Yes/No)> ")
        if answer.lower() == 'yes':
            self._cmd.poutput("Proceeding!")
        else:
            self._cmd.pwarning("Canceling!")
            return

    # Either open a new window or find existing window based on regex
    # or WS addr
    if not HelperClass.standard_validations(url=ns.url,
                                        ws_url = ns.ws_url,
                                        regex = ns.regex):
        self._cmd.pwarning("Validations failed, increase logging for verbosity")
        return
    elif ns.regex:
        regex = HelperClass.get_regex(ns.regex)
    else:
        regex = None

    if bool(ns.sleep) ^ ns.switch_tabs:
        self._cmd.pwarning('You are sleeping w/o switching tabs ' +
                        'or vice versa. Proceeding anyways...')

    if ns.new_session:
        self._cmd.pwarning('New session not yet implemented')

    if not ns.inputs:
        self._cmd.pwarning("No inputs provided. This will enumerate all inputs")
        answer = self._cmd.read_input("Do you want to continue? (Yes/No)> ")
        if answer.lower() == 'yes':
            self._cmd.poutput("Proceeding!")
            inputs = None
        else:
            self._cmd.pwarning("Canceling!")
            return
    else:
        inputs = set(ns.inputs)

    ci = HelperClass.get_injector(ns.injector)
    response = FindValues.find(ci, inputs, url=ns.url, exact_input=ns.exact_input,
                    sleep=ns.sleep, pre_sleep=ns.pre_sleep, new_window=ns.new_window,
                    switch_tabs=ns.switch_tabs, ws_url=ns.ws_url, regex=regex,
                    first_target=ns.first_target, new_session=ns.new_session,
                    pre_script_sleep=ns.pre_script_sleep, background=ns.background)

    self._cmd.poutput(f"{response}")