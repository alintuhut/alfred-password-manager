import sys
import subprocess
import re
import pprint

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

FIND_PASSWORD = re.compile('password: "(.*)"$', re.MULTILINE).search
FIND_ACCOUNT = re.compile('"acct"<blob>="(.*)"$', re.MULTILINE).search
FIND_CLASS = re.compile('class: "(.*)"$', re.MULTILINE).search
FIND_SERVICE = re.compile('"svce"<blob>="(.*)"$', re.MULTILINE).search
FIND_SERVER = re.compile('"srvr"<blob>="(.*)"$', re.MULTILINE).search
FIND_DESC = re.compile('"desc"<blob>="(.*)"$', re.MULTILINE).search
FIND_COMMENTS = re.compile('"icmt"<blob>="(.*)"$', re.MULTILINE).search
FIND_TYPE = re.compile('"type"<uint32>="(.*)"$', re.MULTILINE).search

class Keychain:
    """Simple wrapper for Mac OS X Keychain"""

    def __init__(self, keychain):
        if sys.platform != 'darwin':
            raise Exception('Keychain is only available on Mac OS X')
        self._keychain = keychain;

    def _call_security(self, action, *args):
        """Call the ``security`` CLI app that provides access to keychains.

        May raise `KeychainGenericException`, `KeychainItemNotFound`.

        :param action: The ``security`` action to call, e.g.
                           ``add-generic-password``
        :type action: ``unicode``
        :param *args: list of command line arguments to be passed to
                      ``security``
        :type *args: `list` or `tuple`
        :returns: ``(retcode, output)``. ``retcode`` is an `int`, ``output`` a
                  ``unicode`` string.
        :rtype: `tuple` (`int`, ``unicode``)

        """

        cmd = ['security', action] + list(args)
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

    def _parse_item(self, raw, detailed=False):
        item = KeychainItem();
        item.account = self._find_key(FIND_ACCOUNT, raw)
        item.password = self._find_key(FIND_PASSWORD, raw)
        if detailed:
            item.type = self._find_key(FIND_TYPE, raw) or self._find_key(FIND_CLASS, raw)
            item.service = self._find_key(FIND_SERVICE, raw) or self._find_key(FIND_SERVER, raw)
            item.comments = self._find_key(FIND_COMMENTS, raw) or self._find_key(FIND_DESC, raw)
        return item

    def get_item(self, service, item_type):
        item_type = item_type or 'generic-password'
        return self._parse_item(
            self._call_security('find-' + item_type, '-s', service.strip(), '-g', self._keychain)
        )

    def get_all(self):
        items = []
        raw = self._call_security('dump-keychain', self._keychain)
        # data = self._find_key(FIND_ITEM, raw)
        for entry in raw.split('keychain: "' + self._keychain + '"'):
            if len(entry.strip()):
                items.append(self._parse_item(entry, detailed=True))
        return items
