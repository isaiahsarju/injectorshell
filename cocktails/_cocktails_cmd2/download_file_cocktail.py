import cmd2
import argparse
from cmd2 import CommandSet, with_argparser, with_category, with_default_category
from helperclass import helperclass
from helperclass.helperclass import HelperClass
from cocktails.recipes.downloadfile import DownloadFile

_download_files_parser = cmd2.Cmd2ArgumentParser()
_download_files_parser.add_argument('-i', '--injector', required = True,
                                    choices_provider = HelperClass.get_injector_names,
                                    type=str, help='target ChromeInjector'),
_download_files_parser.add_argument('-u', '--url', default = None, type=str, required = True,
                                        help='target url to download')
_download_files_parser.add_argument('-n', '--file_name', default = None, type=str, required = True,
                                        help='name of downloaded file')
_download_files_parser.add_argument('-open', '--open_file', action ='store_true', required = False,
                                        help='flag to open file immediatly')
_download_files_parser.add_argument('-r', '--regex', default = None, required = False,
                                    choices_provider = HelperClass.get_regex_names,
                                    type=str, help='regex for filtering tabs, alias or in line regex, will only execute on first match')
_download_files_parser.add_argument('-w', '--ws_url', default = None, type=str, required = False,
                                        help='ws_url of target instead of regex')
@cmd2.as_subcommand_to('exec_cocktails', 'download_files', _download_files_parser)
def download_file_cocktail(self, ns: argparse.Namespace):
    """Uses JS to download a file"""
    if not HelperClass.standard_validations(regex=ns.regex,
                                            ws_url=ns.ws_url,
                                            regex_or_ws_url_required=True):
        self._cmd.pwarning("Validations failed, increase logging for verbosity")
        return
    elif ns.regex:
        regex = HelperClass.get_regex(ns.regex)
        first_target = True
    else:
        regex = None
        first_target = False

    ci = HelperClass.get_injector(ns.injector)
    if not ci:
        return

    response = DownloadFile.download(ci, ns.url, file_name=ns.file_name,
                                    open_file=ns.open_file, ws_url=ns.ws_url,
                                    regex=regex, first_target=first_target)
    self._cmd.poutput(f"Response:\n{response}")