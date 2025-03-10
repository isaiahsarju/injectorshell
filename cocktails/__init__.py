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
import cocktails._cocktails_cmd2
import sys


@with_default_category('InstalledCocktails')
class InstalledCocktails(CommandSet):
    """Built-in subcommands to list cocktails
    """
    
    _logger = logging.getLogger(__name__)

    def __init__(self):
        super().__init__()

    # List cocktails
    _list_built_in_cocktails_parser = cmd2.Cmd2ArgumentParser()
    @cmd2.as_subcommand_to('list', 'cocktails', _list_built_in_cocktails_parser)
    def list_installed_cocktails_cmd2(self, ns: argparse.Namespace):
        """List Built-in cocktails"""
        for cmd, description in HelperClass.installed_cocktails_cmd2.items():
            self._cmd.poutput(f"{cmd}: {description}")

    #https://packaging.python.org/en/latest/guides/creating-and-discovering-plugins/
    def iter_namespace(ns_pkg):
        """Get name of module from package"""
        return pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + ".")

    discovered_cocktails_cmd2 = {
        name: importlib.import_module(name)
        for finder, name, ispkg
        in iter_namespace(cocktails._cocktails_cmd2)
    }

# Need to add subcommand methods to InstalledCocktails namespace so
# CMD2 can discover them
method_index = 0
# Get module name and the module from discovered_cocktails_cmd2
for module_name, module in InstalledCocktails.discovered_cocktails_cmd2.items():
    # Get just method name, should be same as file name
    method_name = module_name[module_name.rindex('.')+1:]
    # Get the method from discovered module
    disc_method = getattr(module,method_name)
    # Create dummy name to be added to InstalledCocktails namespace
    bi_method_name = "bi_" + str(method_index) + f"_{method_name}"
    # Add dummy method to InstalledCocktails namespace
    setattr(InstalledCocktails,bi_method_name,disc_method)
    # Add method description to installed_cocktails_cmd2 dict
    HelperClass.installed_cocktails_cmd2[method_name] = disc_method.__doc__
    method_index += 1


