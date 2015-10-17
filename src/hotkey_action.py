import sys
import subprocess
import os
from keychain import Keychain, KeychainItemNotFound, KeychainGenericException
from urlparse import urlparse
from workflow import Workflow
from settings import *

MODE_BOTH = 0
MODE_PASSWORD = 1
MODE_ACCOUNT = 2

def main(wf):

    # Get query from Alfred
    if len(wf.args) and wf.args[0].strip():
        app = wf.args[0].strip()
    else:
        proc = subprocess.Popen('osascript \'' + os.getcwd() + '/get_active_window.applescript\'', shell=True, stdout=subprocess.PIPE)
        app = proc.stdout.read()

    mode = MODE_BOTH
    if len(wf.args) > 1 and wf.args[1].strip():
        mode = int(wf.args[1].strip())

    if app.startswith('https://') or app.startswith('http://'):
        service = '{uri.netloc}'.format(uri=urlparse(app))
        item_type = 'internet-password'
    else:
        service = app.strip()
        item_type = 'generic-password'

    keychain_file = wf.settings.get('keychain_file', None)
    if not keychain_file:
        print '503: No keychain file set'
        return 0

    try:
        keychain = Keychain(keychain_file)
        item = keychain.get_item(service, item_type)
        if mode == MODE_BOTH:
            if item.account and item.password:
                print item.account + SEPARATOR + item.password
            else:
                print '503: Missing data for ' + service
        elif mode == MODE_PASSWORD:
            print item.password
        elif mode == MODE_ACCOUNT:
            print item.account
        else:
            print '400: unknown mode'
    except KeychainItemNotFound:
        print '404: ' + service
    except:
        print '400: ' + service

if __name__ == "__main__":
    wf = Workflow()
    sys.exit(wf.run(main))