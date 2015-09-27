# encoding: utf-8

import sys
import argparse
import subprocess
from workflow import Workflow
from keychain import Keychain, KeychainItemNotFound, KeychainGenericException

def get_item(query, property, wf):

    keychain_file = wf.settings.get('keychain_file', None)
    if not keychain_file:
        return '503: No keychain file set'

    query = query.split('|||')

    try:
        keychain = Keychain(keychain_file)
        item = keychain.get_item(query[0], query[1])
        return getattr(item, property)
    except KeychainItemNotFound:
        return '404: ' + query[0]
    except:
        return '400: ' + query[0]


def main(wf):

    # build argument parser to parse script args and collect their
    # values
    parser = argparse.ArgumentParser()
    parser.add_argument('--keychain', dest='keychain', nargs='?', default=None)
    parser.add_argument('--get-password', dest='password', nargs='?', default=None)
    parser.add_argument('--get-account', dest='account', nargs='?', default=None)

    # parse the script's arguments
    args = parser.parse_args(wf.args)

    # decide what to do based on arguments
    if args.keychain:
        # Save the provided Keychain file
        wf.settings['keychain_file'] = args.keychain
        print wf.settings['keychain_file']
    elif args.password:
        # Get the password of the specified service
        print get_item(args.password, 'password', wf)
    elif args.account:
        print get_item(args.account, 'account', wf)

    return 0  # 0 means script exited cleanly

if __name__ == u"__main__":
    wf = Workflow()
    sys.exit(wf.run(main))