# encoding: utf-8

from workflow import web, Workflow, PasswordNotFound
from keychain import Keychain, KeychainItemNotFound, KeychainGenericException

def get_data(keychain_file):
    """Retrieve items from Keychain"""

    keychain = Keychain(keychain_file)
    items = keychain.get_all()
    return items

def main(wf):
    try:
        # Get Keychain file from settings
        keychain_file = wf.settings.get('keychain_file', None)
        if not keychain_file:  # Keychain file has not yet been set
            raise Exception('No Keychain file set.')

        # Retrieve posts from cache if available and no more than 60
        # seconds old

        def wrapper():
            """`cached_data` can only take a bare callable (no args),
            so we need to wrap callables needing arguments in a function
            that needs none.
            """
            return get_data(keychain_file)

        items = wf.cached_data('items', wrapper, max_age=60)
        # Record our progress in the log file
        wf.logger.debug('{} Keychain items cached'.format(len(items)))

    except Exception as detail:
        wf.logger.error('Cannot update cache: Maybe keychain file is not set.')
        print detail

if __name__ == '__main__':
    wf = Workflow()
    wf.run(main)