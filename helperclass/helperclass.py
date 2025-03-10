import logging
import coloredlogs
import re
import os
import json
import cmd2
from cmd2 import CommandSet, with_argparser, with_category, with_default_category

class HelperClass:
    """Helper Class for the shell"""

    # Dict of name:CI pairs
    injectors = {}
    # Used to count total created and apppend to default name
    injectors_count = 0

    # Dict of name:scripts pairs
    scripts = {}
    # Used to count total created and apppend to default name
    scripts_count = 0

    # Dict of name:regexes pairs
    regexes = {}
    # Used to count total created and apppend to default name
    regexes_count = 0

    # Dict of cocktails name:description
    #cocktails = Bartender.get_cocktails_cmd2()

    # Dict of installed commands name:description
    installed_commands = {}

    # Dict of installed cocktails name:description
    installed_cocktails_cmd2 = {}
    enforce_case = False

    # Helper arguments
    parent_iunderstand = cmd2.Cmd2ArgumentParser(add_help=False)
    parent_iunderstand.add_argument('--iunderstand', action ='store_true', required = False,
                                help='flag to demonstrate that you understand opsec risks')

    @classmethod
    def get_injector(cls, name):
        """Return ChromeInjector with specified name or None"""
        logger = logging.getLogger(__name__)
        try:
            ci = cls.injectors[name]
            logger.debug(f"Found injector with name {name}")
            return ci
        except KeyError as ke:
            logger.error(f"Injector {name} does not exist")
            return None

    @classmethod
    def get_script(cls, name):
        """Return Script with specified name or None"""
        logger = logging.getLogger(__name__)
        try:
            script = cls.scripts[name]
            logger.debug(f"Found script with name {name}")
            return script
        except KeyError as ke:
            logger.error(f"Script {name} does not exist")
            return None


    @classmethod
    def get_injector_names(cls,*__):
        """Return list of injectors by name"""
        if cls.injectors != {}:
            return list(cls.injectors.keys())
        else:
            return []

    @classmethod
    def get_script_names(cls,*__):
        """Return list of scripts by name"""
        if cls.scripts != {}:
            return list(cls.scripts.keys())
        else:
            return []

    @classmethod
    def get_regex_names(cls,*__):
        """Return list of regexes by name"""
        if cls.regexes != {}:
            return list(cls.regexes.keys())
        else:
            return []

    @classmethod
    def validate_json(cls, json_string):
        """Returns True if valid JSON, returns False if not"""
        try:
            json.loads(json_string)
        except ValueError as err:
            return False
        return True

    @classmethod
    def oneline_script(cls, file_path=None, script=None):
        """Returns script file as oneliner or return None if error"""
        logger = logging.getLogger(__name__)
        if not file_path and not script:
            logger.error("No script or file specified. Returning None")
            return None
        elif script:
            script_regex = re.compile("(\n|([ ]{2,}))")
            new_script = script_regex.sub(" ",script)
            return new_script
        else:
            try:
                with open(file_path, 'r') as script_file:
                    try:
                        script = script_file.read()
                    except Exception as e:
                        raise e
                    finally:
                        script_file.close()
                        logger.debug(f"Script is:\n{script}")
                        script_regex = re.compile("(\n|([ ]{2,}))")
                        new_script = script_regex.sub(" ",script)
                        return new_script
            except Exception as e:
                logger.error(f"Unable to open js file: {e}")
                logger.error("Returing None")
                return None

    @classmethod
    def truncate_script(cls, script_content):
        """Pretty trunctation of script contents"""
        truncate_len = 60
        truncated = '...'
        if len(script_content) < 60:
            truncate_len = len(script_content)
            truncated = ""
        final_string = script_content[0:59] + truncated
        return final_string

    @classmethod
    def write_out(cls, file_path, content, overwrite, binary_mode=False):
        """Writes content to out file"""
        logger = logging.getLogger(__name__)
        if file_path and not overwrite and os.path.isfile(file_path):
            logger.error(f"'{file_path}'' already exists, set " +
                                                "overwrite to True to overwrite")
        elif not file_path and content:
            logger.info("No output file specified")
        elif not content:
            logger.error(f"No content to write")
        else:
            try:
                if binary_mode:
                    with open(file_path, 'wb') as out:
                        out.write(content)
                else:
                    with open(file_path, 'w') as out:
                        out.write(content)
                logger.info(f"Wrote data  to {file_path}")
            except Exception as e:
                logger.error(f"Unable to write to file" + \
                                                    f"{file_path}: {e}")

    @classmethod
    def get_regex(cls, provided_regex):
        """Returns regex from global regex dict or returns provided regex as string"""
        logger = logging.getLogger(__name__)
        if not provided_regex:
            regex = None
            logger.debug("Regex is set to None")
        elif provided_regex not in cls.regexes.keys():
            logger.info(f"Regex '{provided_regex}' is not in regex dictionary. "+
                                    "Using as regex")
            regex = provided_regex
        else:
            logger.info(f"'{provided_regex}' present in regex dictionary")
            regex = cls.regexes[provided_regex]
            logger.debug(f"Returning regex:'{regex}'")
        
        if cls.enforce_case:
            logger.warning(f"Enforce regex case set to True. May limit targets")
            return re.compile(regex)
        else:
            logger.info(f"Enforce regex case set to False")
            return re.compile(regex, re.IGNORECASE)

    @classmethod
    def set_case_enforcement(cls, enforce):
        """Sets case enforcement for regexs"""
        logger = logging.getLogger(__name__)
        cls.enforce_case = enforce
        logger.info(f"Enforce regex case set to: {cls.enforce_case}")

    @classmethod
    def get_case_enforcement(cls):
        return cls.enforce_case

    @classmethod
    def standard_validations(cls,
                            regex_or_ws_url_required: bool = False,
                            regex = False,
                            ws_url = False,
                            url = False,
                            first = False,
                            background = False,
                            new_window = False,
                            iunderstand = False
                            ):
        """Returns true or false based on if provided
        values trigger any conflicts"""
        logger = logging.getLogger(__name__)
        return_val = True

        if (not(regex or ws_url) and regex_or_ws_url_required):
            logger.error("Requires regex or ws_url")
            return_val = False
        elif (regex and ws_url):
            logger.error("Cannot use regex with ws_url")
            return_val= False
        elif url and (regex or ws_url):
            logger.error('Cannot use url with ws_url or regex')
            return_val = False
        elif (regex or first) and ws_url:
            logger.error("Cannot use regex or first with ws_url")
            return_val = False

        if (background and new_window) and not iunderstand:
            logger.warning("Using background and new_window together  " +
                          "may not work as expected. Test in mirror env " +
                          "first. May pop up new window in view of user. "  +
                          "Use --iunderstand to surpress warning.")
            return_val = False

        return return_val
