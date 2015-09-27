import sys
import subprocess
import re

####################################################################
# Exceptions
####################################################################

class KeychainGenericException(Exception):
    """Raised when ``security`` command returns an unknown error code."""

class KeychainItemNotFound(KeychainGenericException):
    """Raised when ``security`` command cannot find the item in the keychain"""

####################################################################
# Keychain Item class
####################################################################

class KeychainItem(object):
    pass

####################################################################
# Keychain class
####################################################################

FIND_PASSWORD = re.compile('password: "([^"]+)"').search
FIND_ACCOUNT = re.compile('"acct"<blob>="([^"]+)"').search

class Keychain:
    """Simple wrapper for Mac OS X Keychain"""

    def __init__(self, keychain):
        if sys.platform != 'darwin':            
            raise Exception('Keychain is only available on Mac OS X')
        self._keychain = keychain;

    def _call_security(self, action, service, *args):
        """Call the ``security`` CLI app that provides access to keychains.

        May raise `KeychainGenericException`, `KeychainItemNotFound`.

        :param action: The ``security`` action to call, e.g.
                           ``add-generic-password``
        :type action: ``unicode``
        :param service: Name of the service.
        :type service: ``unicode``        
        :param *args: list of command line arguments to be passed to
                      ``security``
        :type *args: `list` or `tuple`
        :returns: ``(retcode, output)``. ``retcode`` is an `int`, ``output`` a
                  ``unicode`` string.
        :rtype: `tuple` (`int`, ``unicode``)

        """
    
        cmd = ['security', action, '-s', service] + list(args)                                
        p = subprocess.Popen(cmd,                              
                             stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT)
        retcode, output = p.wait(), p.stdout.read().strip().decode('utf-8')
        if retcode == 44:  # item does not exist
            raise KeychainItemNotFound()        
        elif retcode > 0:            
            err = KeychainGenericException('Unknown Keychain error : %s' % output)
            err.retcode = retcode
            raise err
        return output

    def _find_key(self, func, raw):
        match = func(raw)
        return match and match.group(1)

    def _parse_item(self, raw):
        item = KeychainItem();
        account = self._find_key(FIND_ACCOUNT, raw)
        if account:
            item.account = account            
        password = self._find_key(FIND_PASSWORD, raw)
        if password:
            item.password = password    
        return item

    def get_item(self, service, item_type):        
        item_type = item_type or 'generic-password'
        return self._parse_item(
            self._call_security('find-' + item_type, service.strip(), '-g', self._keychain)
        )
