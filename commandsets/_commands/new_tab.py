import cmd2
import argparse
from cmd2 import CommandSet, with_argparser, with_category, with_default_category
from helperclass import helperclass
from helperclass.helperclass import HelperClass

_new_tab_parser = cmd2.Cmd2ArgumentParser(parents=[HelperClass.parent_iunderstand])
_new_tab_parser.add_argument('-i', '--injector', required = True,
                                    choices_provider = HelperClass.get_injector_names,
                                    type=str, help='target ChromeInjector'),
_new_tab_parser.add_argument('-u', '--url', default = None, type=str, required = False,
                                        help='url of new tab')
_new_tab_parser.add_argument('-b', '--background', action ='store_true', required = False,
                                        help='flag to background new tab'),
_new_tab_parser.add_argument('-w', '--new_window', action ='store_true', required = False,
                                        help='flag to open in new window instead of tab',
                                        default = False),
_new_tab_parser.add_argument('-f', '--for_tab', action ='store_true', required = False,
                                        help='flag to send forTab: true in Target.createTarget')
_new_tab_parser.add_argument('-l', '--silent', action ='store_true', required = False,
                                        help='flag to execute silently and not print output')
@cmd2.as_subcommand_to('exec', 'new_tab', _new_tab_parser)
def new_tab(self, ns: argparse.Namespace):
    """Open new window or tab"""
    if (ns.background and ns.new_window) and not ns.iunderstand:
        self._cmd.pwarning("Using background and new_window together  " +
                          "may not work as expected. Test in mirror env " +
                          "first. May pop up new window in view of user. " +
                          "Use --iunderstand to surpress warning.")
        answer = self._cmd.read_input("Do you want to continue? (Yes/No)> ")
        if answer.lower() == 'yes':
            self._cmd.poutput("Proceeding!")
        else:
            self._cmd.pwarning("Canceling!")
            return

    ci = HelperClass.get_injector(ns.injector)
    if not ci:
        return
    if ns.for_tab:
        # Warning for Chrome Versions 120.0.6099.218+
        self._cmd.pwarning("As of Chrome 120.0.6099.218 "+
                             "Target.createTarget returns incorrect "+
                             "target ID when used with --for_tab. "+
                             "Check with exec list_tabs")
    response, *__ = ci.cdp_new_window(ns.url, background=ns.background, new_window=ns.new_window,
                                      for_tab=ns.for_tab)
    if not response:
        self._cmd.perror("No new tab created")

    if not ns.silent and response:
            self._cmd.poutput(f"New ws_url:\n{response}")