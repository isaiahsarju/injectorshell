# Adding Your Own Commands
Use the following template and add your file to `commandsets/_commands`

```python
# [your_command].py
# File name must match method

import cmd2
import argparse
from cmd2 import CommandSet, with_argparser, with_category, with_default_category
from helperclass import helperclass
from helperclass.helperclass import HelperClass
# import if you want to use cocktails...
# from cocktails.cocktails import Bartender

_[your_command]_parser = cmd2.Cmd2ArgumentParser()
_[your_command]_parser.add_argument('-r', '--regex', default = None, required = False,
                                    choices_provider = HelperClass.get_regex_names,
                                    type=str, help='regex for filtering tabs, alias or in line regex')
_[your_command]_parser.add_argument('-i', '--injector', required = True,
                                    choices_provider = HelperClass.get_injector_names,
                                    type=str, help='target ChromeInjector')
_[your_command]_parser.add_argument('-w', '--ws_url', default = None, type=str, required = False,
                                        help='ws_url of target instead of regex')
_[your_command]_parser.add_argument('-p', '--path', default = None, required = False,
                                type=str, help='path to outfile', completer=cmd2.Cmd.path_complete)
_[your_command]_parser.add_argument('-o', '--overwrite', action ='store_true', required = False,
                                        help='flag to overwrite previously written out file')
_[your_command]_parser.add_argument('-o', '--overwrite', action ='store_true', required = False,
                                        help='flag to overwrite previously written out file')
_[your_command]_parser.add_argument('-l', '--silent', action ='store_true', required = False,
                                        help='flag to execute silently and not print output')
_[your_command]_parser.add_argument('-e', '--timeout', default = None, type=int, required = False,
                                        help='timeout in seconds')
@cmd2.as_subcommand_to('exec', '[your_command]', _[your_command]_parser)
def [your_command](self, ns: argparse.Namespace):
    """Descriptive docstring describing operation"""
    if (ns.regex or ns.first) and ns.ws_url:
        self._cmd.perror("Cannot use regex or first with ws_url")
    elif ns.regex:
        regex = HelperClass.get_regex(ns.regex)
    else:
        regex = None
    ci = HelperClass.get_injector(ns.injector)
    if not ci:
        return
    #...stuff...
    result = ci.[some_command](regex=regex, first_target=ns.first, time=ns.timeout, ws_url=ns.ws_url)
    #...other stuff, maybe...
    HelperClass.write_out(ns.path, str(result), ns.overwrite)
    if not ns.silent and history:
        self._cmd.poutput(f"Response:\n{history}")
```