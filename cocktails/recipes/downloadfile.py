import logging
import coloredlogs
from string import Template
import re
from chromeinjector.chromeinjector import ChromeInjector

class DownloadFile:
    """Uses JS to download a file
    """
    @classmethod
    def download (cls, injector: ChromeInjector,
                    url: str,
                    file_name: str,
                    open_file: bool = False,
                    ws_url: str = None,
                    regex: re.Pattern = None,
                    first_target: bool = True,
                    ) -> tuple:
        """Return tuple of result of download JS execution

        Keyword arguments:
        injector -- ChromeInjector instance
        url  -- target url
        file_name -- name to save on disk (default: None)
        open_file -- boolean to open after download. (Default: False)
        ws_url -- str of WS URL to execute on
        regex -- regex of target tab (Default: None)
        first_target -- only execute on first target (default: True)
        """
        logger = logging.getLogger(__name__)

        # https://dev.to/nombrekeff/download-file-from-blob-21ho
        download_func_js = 'function downloadBlob(blob, name) { const blobUrl = URL.createObjectURL(blob); const link = document.createElement("a"); link.href = blobUrl; link.download = name; document.body.appendChild(link); link.dispatchEvent( new MouseEvent(\'click\', { bubbles: true, cancelable: true, view: window }) ); document.body.removeChild(link); }' 
        # ChaptGPT 4 "Give me code to convert a file from a url into a JS blob"
        url_to_blob_js = 'async function fetchFileAsBlob(url) { try { const response = await fetch(url); const data = await response.blob(); return data; } catch (error) { console.error(\'Error fetching file:\', error); } }'
        execute_download_template = Template("fetchFileAsBlob(\'$url\').then(blob => {downloadBlob(blob,\'$file_name\')});")
        execute_download_js = execute_download_template.substitute(url=url, file_name=file_name)

        if(open_file):
            logger.error("Open not yet implemented. Sry")
            return None

        df_result = injector.cdp_eval_script(download_func_js, 
                                            regex=regex,
                                            ws_url=ws_url,
                                            first_target=first_target)[0]
        logger.info(df_result)
        u2b_result = injector.cdp_eval_script(url_to_blob_js,
                                            regex=regex,
                                            ws_url=ws_url,
                                            first_target=first_target)[0]
        logger.info(u2b_result)
        d_result = injector.cdp_eval_script(execute_download_js,
                                            regex=regex,
                                            ws_url=ws_url,
                                            first_target=first_target)[0]
        if not 'Error' in d_result[1]['result']['description']:
            logger.info('Download likely succeeeded. No Error Detected in Reponse')
        return (d_result)