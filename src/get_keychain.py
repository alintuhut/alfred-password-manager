import sys
import subprocess
import os
from keychain import Keychain, KeychainItemNotFound, KeychainGenericException
from urlparse import urlparse
from workflow import Workflow
from settings import *

def main(wf):

    # Get query from Alfred
    if len(wf.args) and wf.args[0].strip():
        app = wf.args[0].strip()        
    else:
        proc = subprocess.Popen('osascript \'' + os.getcwd() + '/get_active_window.applescript\'', shell=True, stdout=subprocess.PIPE)
        app = proc.stdout.read()                

    if app.startswith('https://') or app.startswith('http://'):        
        service = '{uri.netloc}'.format(uri=urlparse(app))
        item_type = 'internet-password'
    else:
        service = app
        item_type = 'generic-password'

    try:
        keychain = Keychain(KEYCHAIN)
        item = keychain.get_item(service, item_type)        
        # wf.logger.info(item.account + SEPARATOR + item.password)
        if item.account and item.password:
            print item.account + SEPARATOR + item.password
        else:
            print '503: ' + service
    except KeychainItemNotFound:
        print '404: ' + service
    except:
        print '400: ' + service
    
if __name__ == "__main__":    
    wf = Workflow()
    sys.exit(wf.run(main))