import cmd2
import argparse
from cmd2 import CommandSet, with_argparser, with_category, with_default_category
from helperclass import helperclass
from helperclass.helperclass import HelperClass
from cocktails.recipes.settingsnavigator import SettingsNavigator

_settings_navigator_parser = cmd2.Cmd2ArgumentParser(parents=[HelperClass.parent_iunderstand])
_settings_navigator_parser.add_argument('-i', '--injector', required = False,
                                    choices_provider = HelperClass.get_injector_names,
                                    type=str, help='target ChromeInjector'),
_settings_navigator_parser.add_argument('-a', '--action', default = None, type=str, required = False,
                                        choices_provider = SettingsNavigator.get_actions,
                                        help='settings action to perform (e.g. list_passwords)')
_settings_navigator_parser.add_argument('-l', '--list', action ='store_true', required = False,
                                        help='flag to list settings actions')
_settings_navigator_parser.add_argument('-w', '--new_window', action ='store_true', required = False,
                                        help='flag to open settings page in new window')
_settings_navigator_parser.add_argument('-b', '--background', action ='store_true', required = False,
                                        help='flag to open settings page backgrounded')
_settings_navigator_parser.add_argument('-c', '--switch_tabs', action ='store_true', default = False,
                                        required = False,
                                        help='flag to switch tabs after opening URL (e.g. let load). '+
                                            'Use with -s/--sleep')
_settings_navigator_parser.add_argument('-s', '--sleep', default = None, type=float, required = False,
                                        help='sleep time after tab switch to force load. '+
                                        'Use with -c/--switch_tabs')
_settings_navigator_parser.add_argument('-p', '--pre_sleep', default = None, type=float, required = False,
                                        help='sleep time before switch to allow load')
_settings_navigator_parser.add_argument('-r', '--pre_script_sleep', default = None, type=float, required = False,
                                        help='sleep time (after pre_sleep)(and/or after switch+sleep) to allow load')
_settings_navigator_parser.add_argument('-t', '--script_exec_time', default = 0.0, type=float, required = False,
                                        help='time to allow script execution prior to final value retrieval ')
@cmd2.as_subcommand_to('exec_cocktails', 'settings_navigator_cocktail', _settings_navigator_parser)
def settings_navigator_cocktail(self, ns: argparse.Namespace):
    """Uses JS to naviage and change settings
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

    available_actions = SettingsNavigator.get_actions_desc()
    response = ""
    if not (ns.action or ns.list):
        self._cmd.perror("Pick an action OR list")
        return None
    elif (ns.action and ns.list):
        self._cmd.perror("Pick an action OR list")
        return None
    elif (ns.list):
        for action, description in available_actions.items():
            response += f"{action}:\n\t{description}\n\n"
    else:
        ci = HelperClass.get_injector(ns.injector)
        response = SettingsNavigator.exec_action(ci, ns.action,
                        background= ns.background,
                        pre_sleep=ns.pre_sleep,
                        new_window=ns.new_window,
                        sleep=ns.sleep,
                        pre_script_sleep=ns.pre_script_sleep,
                        switch_tabs=ns.switch_tabs,
                        script_exec_time=ns.script_exec_time)

    self._cmd.poutput(f"{response}")
        