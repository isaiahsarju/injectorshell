"""A cmd2 application for managing and using ChromeInjector Objects"""
import sys
import os
import re
import logging
import coloredlogs
import cmd2
import argparse
import json
import os.path
import base64
from datetime import datetime
from cmd2 import CommandSet, with_argparser, with_category, with_default_category, style
from optparse import OptionParser
from chromeinjector.chromeinjector import ChromeInjector
#from cocktails.cocktails import Bartender
from helperclass.helperclass import HelperClass
from commandsets import InstalledCommands
from cocktails import InstalledCocktails
assert sys.version_info >= (3, 11)

@with_default_category('Injectors')
class ChromeInjectors(CommandSet):
    """ChromeInjector subcommands to create, delete, and use"""
    _logger = logging.getLogger(__name__)

    def __init__(self):
        super().__init__()

    # New Injector
    _new_injector_parser = cmd2.Cmd2ArgumentParser()
    _new_injector_parser.add_argument('-n', '--name', default = None, type=str, help='alias of CI')
    _new_injector_parser.add_argument('-t', '--target', default = '127.0.0.1', type=str, help='target host')
    _new_injector_parser.add_argument('-p', '--port', default = 9222, type=int, help='port')
    _new_injector_parser.add_argument('--custom_ws_target', type=str, help='set this when WS targets '+
                                      'will not be localhost (e.g. using ngrok)')
    _new_injector_parser.add_argument('--custom_ws_port', default = None, type=int, help='set this when WS target ports '+
                                      'are proxied (e.g. using ngrok)')
    _new_injector_parser.add_argument('-o', '--overwrite', action ='store_true', required = False,
                                            help='flag to overwrite previously defined CI')
    _new_injector_parser.add_argument('--rewrite_host_header', action ='store_true', required = False,
                                            help='flag rewrite HOST header to' +
                                            ' --custom_host_header in HTTP requests')
    _new_injector_parser.add_argument('--custom_host_header', required=False,
                                            default = 'localhost', type=str,
                                            help='custom HOST Header in HTTP requests')
    _new_injector_parser.add_argument('--https', action ='store_true', required = False,
                                            help='flag to use TLS/SSL for HTTP requests')
    _new_injector_parser.add_argument('--wss', action ='store_true', required = False,
                                            help='flag to use TLS/SSL for WebSocket requests')
    _new_injector_parser.add_argument('--proxy_type', required=False,
                                            default = None, type=str,
                                            help='proxy type (socks4, socks5, http)')
    _new_injector_parser.add_argument('--proxy_host', required=False,
                                            default = None, type=str,
                                            help='proxy host')
    _new_injector_parser.add_argument('--proxy_port', required=False,
                                            default = None, type=int,
                                            help='proxy port as int')
    @cmd2.as_subcommand_to('new', 'injector', _new_injector_parser)
    def new_injector(self, ns: argparse.Namespace):
        """Create new ChromeInjector"""

        if not ns.name:
            name = "ChromeInjector" + str(HelperClass.injectors_count)
        else:
            name = ns.name
        try:
            if name in HelperClass.injectors and not overwrite:
                self._cmd.perror(f"CI named {name} already exists. Use -o to overwrite")
                raise ValueError(f"Key '{name}' already exists")
            else:
                ci = ChromeInjector(ns.target, ns.port,
                                    rewrite_host_header=ns.rewrite_host_header,
                                    custom_host_header=ns.custom_host_header,
                                    custom_ws_target=ns.custom_ws_target,
                                    custom_ws_port=ns.custom_ws_port,
                                    https=ns.https,
                                    wss=ns.wss,
                                    proxy_type=ns.proxy_type,
                                    proxy_host=ns.proxy_host,
                                    proxy_port=ns.proxy_port)
                self._cmd.poutput(f"Created ChromeInjector")
                self._logger.debug(f"Created ChromeInjector with target:{ns.target}, port:{ns.port}")
            HelperClass.injectors[name] = ci
            self._cmd.poutput(name + ': ' + ns.target + ":" + str(ns.port))
            HelperClass.injectors_count += 1
        except ValueError as ve:
            self._cmd.pexcept(ve)
            self._cmd.perror(f"Failed to create '{name}': {ve}")

    # List ChromeInjectors
    _list_chromeinjectors_parser = cmd2.Cmd2ArgumentParser()
    @cmd2.as_subcommand_to('list', 'chromeinjectors', _list_chromeinjectors_parser)
    def list_chromeinjectors(self, ns: argparse.Namespace):
        """List ChromeInjectors"""
        self._cmd.poutput(str(len(HelperClass.injectors)) + " ChromeInjector(s):")
        for key, injector in HelperClass.injectors.items():
            name = key
            host = injector.get_host()
            port = injector.get_port()
            browser_ws = injector.get_browser_ws()
            self._cmd.poutput(name + " (" + host + ":" + str(port) +
                              ", " +
                              (browser_ws if browser_ws
                                else "No Browser Debug WS set")+
                              ")")

    # List available cocktails
    #_list_cocktails_parser = cmd2.Cmd2ArgumentParser()
    #@cmd2.as_subcommand_to('list', 'cocktails', _list_cocktails_parser)
    #def list_cocktails(self, ns: argparse.Namespace):
    #    """List cocktails"""
    #    self._cmd.poutput("Available cocktails:")
    #    for name, description in HelperClass.cocktails.items():
    #        self._cmd.poutput(name + ": " + description)

    # Set Injectors settings
    _set_property_injector_browser_ws_parser = cmd2.Cmd2ArgumentParser()
    _set_property_injector_browser_ws_parser.add_argument('-i', '--injector', required = True,
                                        choices_provider = HelperClass.get_injector_names,
                                        type=str, help='target ChromeInjector')
    _set_property_injector_browser_ws_parser.add_argument('-w', '--browser_ws',
                                                default = None, type=str,
                                                required = False,
                                                help='ws:// browser websocket debug url')
    @cmd2.as_subcommand_to('set_property', 'injector_browser_ws', _set_property_injector_browser_ws_parser)
    def set_property_injector_browser_ws(self, ns: argparse.Namespace):
        """Set ChromeInjector browser_ws"""
        ci = HelperClass.get_injector(ns.injector)
        browser_ws = ns.browser_ws
        if not browser_ws:
            self._cmd.pwarning('browser_ws not set. ' +
                            'Will attempt to retrieve via http(s)')
        ci.set_browser_ws(browser_ws)
        

@with_default_category('Scripts')
class Scripts(CommandSet):
    """Script subcommands to create, delete, and use"""
    _logger = logging.getLogger(__name__)

    def __init__(self):
        super().__init__()

    # New Script
    _new_script_parser = cmd2.Cmd2ArgumentParser()
    _new_script_parser.add_argument('-n', '--name', default = None, type=str, help='alias of script')
    _new_script_parser.add_argument('-p', '--path', default = None, required = False,
                                    type=str, help='path to script', completer=cmd2.Cmd.path_complete)
    _new_script_parser.add_argument('-i', '--inline', default = None,
                                    required = False, type=str, help='inline script')
    _new_script_parser.add_argument('-o', '--overwrite', action ='store_true', required = False,
                                            help='flag to overwrite previously defined script')
    @cmd2.as_subcommand_to('new', 'script', _new_script_parser)
    def new_script(self, ns: argparse.Namespace):
        """Create new Script"""

        if not ns.path and not ns.inline:
            self._cmd.perror("No inline script or path provided")
            return
        elif ns.inline:
            script_content = HelperClass.oneline_script(script=ns.inline)
        else:
            script_content = HelperClass.oneline_script(file_path=ns.path)

        if not script_content:
            self._cmd.perror("Failed to load script")
            return None

        if not ns.name:
            name = "Script" + str(HelperClass.scripts_count)
        else:
            name = ns.name
        try:
            if name in HelperClass.scripts and not ns.overwrite:
                self._cmd.perror(f"Script named {name} already exists. Use -o to overwrite")
                raise ValueError(f"Key '{name}' already exists")
            HelperClass.scripts[name] = script_content
            self._cmd.poutput(name + ': ' + HelperClass.truncate_script(script_content))
            HelperClass.scripts_count += 1
        except ValueError as ve:
            self._cmd.perror(f"Failed to create '{name}':{ve}")

    # List Scripts
    _list_script_parsers = cmd2.Cmd2ArgumentParser()
    @cmd2.as_subcommand_to('list', 'scripts', _list_script_parsers)
    def list_scripts(self, ns: argparse.Namespace):
        """List Scripts"""
        self._cmd.poutput(str(len(HelperClass.scripts)) + " Script(s):")
        for key, script_content in HelperClass.scripts.items():
            name = key
            self._cmd.poutput(name + ": " + HelperClass.truncate_script(script_content))

@with_default_category('Regexes')
class Regexes(CommandSet):
    """Regex subcommands to create, delete, and use"""
    _logger = logging.getLogger(__name__)

    def __init__(self):
        super().__init__()

    # New Regex
    _new_regex_parser = cmd2.Cmd2ArgumentParser()
    _new_regex_parser.add_argument('-n', '--name', default = None, type=str, help='alias of regex')
    _new_regex_parser.add_argument('-r', '--regex', default = None,
                                    required = False, type=str, help='the regex')
    _new_regex_parser.add_argument('-o', '--overwrite', action ='store_true', required = False,
                                            help='flag to overwrite previously defined regex')
    @cmd2.as_subcommand_to('new', 'regex', _new_regex_parser)
    def new_regex(self, ns: argparse.Namespace):
        """Create new Regex"""

        if not ns.name:
            name = "Regex" + str(HelperClass.regexes_count)
        else:
            name = ns.name
        try:
            if name in HelperClass.regexes and not ns.overwrite:
                self._cmd.perror(f"Regex named {name} already exists. Use -o to overwrite")
                raise ValueError(f"Key '{name}' already exists")
            HelperClass.regexes[name] = ns.regex
            self._cmd.poutput(name + ': ' + ns.regex)
            HelperClass.regexes_count += 1
        except ValueError as ve:
            self._cmd.perror(f"Failed to create '{name}':{ve}")

    # List Regexes
    _list_regex_parsers = cmd2.Cmd2ArgumentParser()
    @cmd2.as_subcommand_to('list', 'regexes', _list_regex_parsers)
    def list_regexes(self, ns: argparse.Namespace):
        """List Regexes"""
        self._cmd.poutput(str(len(HelperClass.regexes)) + " Regex(es):")
        for key, regex in HelperClass.regexes.items():
            name = key
            self._cmd.poutput(name + ": " + regex)

@with_default_category('Commands')
class InjectorShell(cmd2.Cmd):
    """Manage ChromeInjectors in a shell"""

    _logger = logging.getLogger(__name__)

    def __init__(self, *args, **kwargs):
        # gotta have this or neither the plugin or cmd2 will initialize
        super().__init__(*args,
                        auto_load_commands=False,
                        **kwargs,
                        multiline_commands=['echo'],
                        allow_cli_args=False,
                        include_py=True,
                        persistent_history_file='.injectorshell_history',
                        persistent_history_length=1000)
        # Prints an intro banner once upon application startup
        self.intro = style('Welcome to the ChromeInjector Shell!', bold=True)
        # Show this as the prompt when asking for input
        self.prompt = 'ci> '
        # Used as prompt for multiline commands after the first line
        self.continuation_prompt = '... '
        # Injectors subcommands
        self._chrome_injectors = ChromeInjectors()
        self.register_command_set(self._chrome_injectors)
        # Installed subcommands
        self._installed_cmds = InstalledCommands()
        self.register_command_set(self._installed_cmds)
        # Installed cocktails
        self._installed_cocktails = InstalledCocktails()
        self.register_command_set(self._installed_cocktails)
        # Script subcommands
        self._scripts = Scripts()
        self.register_command_set(self._scripts)
        # Regex subcommands
        self._regexes = Regexes()
        self.register_command_set(self._regexes)

    # new injectors, scripts, etc
    _new_parser = cmd2.Cmd2ArgumentParser()
    #new_subparsers =
    _new_parser.add_subparsers(title='item', help='injector, script,...')
    @with_argparser(_new_parser)
    def do_new(self, ns: argparse.Namespace):
        """Create a new item"""
        handler = ns.cmd2_handler.get()
        if handler is not None:
            # Call whatever subcommand function was selected
            handler(ns)
        else:
            # No subcommand was provided, so call help
            self.poutput('This command does nothing without sub-parsers registered')
            self.do_help('new')

    # close injectors, scripts, etc
    _close_parser = cmd2.Cmd2ArgumentParser()
    #new_subparsers =
    _close_parser.add_subparsers(title='item', help='injector, tab,...')
    @with_argparser(_close_parser)
    def do_close(self, ns: argparse.Namespace):
        """Close something"""
        handler = ns.cmd2_handler.get()
        if handler is not None:
            # Call whatever subcommand function was selected
            handler(ns)
        else:
            # No subcommand was provided, so call help
            self.poutput('This command does nothing without sub-parsers registered')
            self.do_help('new')

    # list injectors, scripts, etc
    _list_parser = cmd2.Cmd2ArgumentParser()
    _list_parser.add_subparsers(title='item', help='injectors, scripts,...')
    @with_argparser(_list_parser)
    def do_list(self, ns: argparse.Namespace):
        """List things"""
        handler = ns.cmd2_handler.get()
        if handler is not None:
            # Call whatever subcommand function was selected
            handler(ns)
        else:
            # No subcommand was provided, so call help
            self.poutput('This command does nothing without sub-parsers registered')
            self.do_help('list')

    # exec installed commands and scripts
    _exec_parser = cmd2.Cmd2ArgumentParser()
    _exec_parser.add_subparsers(title='command', help='cdp command, scripts,...')
    @with_argparser(_exec_parser)
    def do_exec(self, ns: argparse.Namespace):
        """Execute command"""
        handler = ns.cmd2_handler.get()
        if handler is not None:
            # Call whatever subcommand function was selected
            handler(ns)
        else:
            # No subcommand was provided, so call help
            self.poutput('This command does nothing without sub-parsers registered')
            self.do_help('exec')

    # exec installed cocktails and scripts
    _exec_cocktails_parser = cmd2.Cmd2ArgumentParser()
    _exec_cocktails_parser.add_subparsers(title='command', help='settings_navigator, history, etc...')
    @with_argparser(_exec_cocktails_parser)
    def do_exec_cocktails(self, ns: argparse.Namespace):
        """Execute command"""
        handler = ns.cmd2_handler.get()
        if handler is not None:
            # Call whatever subcommand function was selected
            handler(ns)
        else:
            # No subcommand was provided, so call help
            self.poutput('This command does nothing without sub-parsers registered')
            self.do_help('exec_cocktails')

    # set values
    _set_property_parser = cmd2.Cmd2ArgumentParser()
    _set_property_parser.add_subparsers(title='item', help='browser_ws, etc.,...')
    @with_argparser(_set_property_parser)
    def do_set_property(self, ns: argparse.Namespace):
        """Set a property"""
        handler = ns.cmd2_handler.get()
        if handler is not None:
            # Call whatever subcommand function was selected
            handler(ns)
        else:
            # No subcommand was provided, so call help
            self.poutput('This command does nothing without sub-parsers registered')
            self.do_help('set_property')


def main():
    parser = OptionParser()
    parser.add_option("-l", "--loglevel", dest="loglevel", default="ERROR", help="Log level of INFO, DEBUG, WARNING, ERROR (default), and CRITICAL")
    parser.add_option("-e", "--enforce_case", dest="enforce_case", default=False, action='store_true', help="Enforce Casing in Regex")
    (options, args) = parser.parse_args()
    loglevel = options.loglevel
    enforce_case = options.enforce_case

    logger = logging.getLogger(__name__)
    logger.setLevel(getattr(logging, loglevel.upper()))
    coloredlogs.install(level=loglevel.upper(),fmt='%(name)s[%(process)d] %(levelname)s %(message)s')

    logger.debug("Starting cmd2 shell...")
    HelperClass.set_case_enforcement(enforce_case)
    c = InjectorShell()
    sys.exit(c.cmdloop())

if __name__ == '__main__':
    """Call main function or exit."""
    if sys.version_info <= (3, 11):
        print("It's not pre-pandemic, use python >= 3.11")
        exit()
    main()