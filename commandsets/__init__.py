import cmd2
import argparse
import logging
from cmd2 import CommandSet, with_argparser, with_category, with_default_category, style
from optparse import OptionParser
from helperclass.helperclass import HelperClass
import os
import re
import importlib
import pkgutil
import commandsets._commands
import sys


@with_default_category('InstalledCommands')
class InstalledCommands(CommandSet):
    """Built-in subcommands to list commands
    """
    
    _logger = logging.getLogger(__name__)

    def __init__(self):
        super().__init__()

    # List built in commands
    _list_built_in_parser = cmd2.Cmd2ArgumentParser()
    @cmd2.as_subcommand_to('list', 'installed_commands', _list_built_in_parser)
    def list_installed_commands(self, ns: argparse.Namespace):
        """List Built-in commands"""
        for cmd, description in HelperClass.installed_commands.items():
            self._cmd.poutput(f"{cmd}: {description}")

    #https://packaging.python.org/en/latest/guides/creating-and-discovering-plugins/
    def iter_namespace(ns_pkg):
        """Get name of module from package"""
        return pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + ".")

    discovered_plugins = {
        name: importlib.import_module(name)
        for finder, name, ispkg
        in iter_namespace(commandsets._commands)
    }

# Need to add subcommand methods to InstalledCommands namespace so
# CMD2 can discover them
method_index = 0
# Get module name and the module from discovered_plugins
for module_name, module in InstalledCommands.discovered_plugins.items():
    # Get just method name, should be same as file name
    method_name = module_name[module_name.rindex('.')+1:]
    # Get the method from discovered module
    disc_method = getattr(module,method_name)
    # Create dummy name to be added to InstalledCommands namespace
    bi_method_name = "bi_" + str(method_index) + f"_{method_name}"
    # Add dummy method to InstalledCommands namespace
    setattr(InstalledCommands,bi_method_name,disc_method)
    # Add method description to installed_commands dict
    HelperClass.installed_commands[method_name] = disc_method.__doc__
    method_index += 1



