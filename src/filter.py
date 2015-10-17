# encoding: utf-8

import sys
import argparse
import subprocess
from workflow import (Workflow, ICON_WEB, ICON_INFO, ICON_WARNING, MATCH_SUBSTRING)
from workflow.background import run_in_background, is_running
import os
import pprint

ICON_ROOT = '/System/Library/CoreServices/CoreTypes.bundle/Contents/Resources'
ICON_KEYCHAIN_APPLICATION = os.path.join(ICON_ROOT, 'GenericApplicationIcon.icns')
ICON_KEYCHAIN_NOTE = os.path.join(ICON_ROOT, 'AlertNoteIcon.icns')
ICON_KEYCHAIN_INTERNET = ICON_WEB

def search_key_for_item(item):
    """Generate a string search key for an item"""
    elements = []    
    if item.service:
        elements.append(item.service)
    if item.comments and len(item.service):
        elements.append(item.comments)
    return u' '.join(elements)

def main(wf):

    # build argument parser to parse script args and collect their
    # values
    parser = argparse.ArgumentParser()    
    # add an optional query and save it to 'query'
    parser.add_argument('query', nargs='?', default=None)
    # parse the script's arguments
    args = parser.parse_args(wf.args)
    
    ####################################################################
    # Check that we have a Keychain file saved
    ####################################################################

    keychain_file = wf.settings.get('keychain_file', None)
    if not keychain_file:
        wf.add_item('No Keychain file set.',
                    'Please use pass-set-keychain to set your Keychain file.',
                    valid=False,
                    icon=ICON_WARNING)
        wf.send_feedback()
        return 0

    ####################################################################
    # View/filter items
    ####################################################################

    query = args.query

    # Get items from cache. Set `data_func` to None, as we don't want to
    # update the cache in this script and `max_age` to 0 because we want
    # the cached data regardless of age
    items = wf.cached_data('items', None, max_age=0)

    # Start update script if cached data is too old (or doesn't exist)
    if not wf.cached_data_fresh('items', max_age=60):
        cmd = ['/usr/bin/python', wf.workflowfile('update.py')]
        run_in_background('update', cmd)

    # Notify the user if the cache is being updated
    # if is_running('update'):
    #     wf.add_item('Getting new data from Keychain',
    #                 valid=False,
    #                 icon=ICON_INFO)

    # If script was passed a query, use it to filter items if we have some

    if query and items:
        items = wf.filter(query, items, key=search_key_for_item, match_on=MATCH_SUBSTRING)

    if not items:  # we have no data to show, so show a warning and stop
        wf.add_item('No items found', icon=ICON_WARNING)
        wf.send_feedback()
        return 0

    # Loop through the returned items and add a item for each to
    # the list of results for Alfred
    for item in items:
        if item.type == 'inet':
            icon = ICON_KEYCHAIN_INTERNET
        elif item.type == 'note':
            icon = ICON_KEYCHAIN_NOTE
        else:
            icon = ICON_KEYCHAIN_APPLICATION

        subtitle = ''
        if item.account:
            subtitle += item.account
        if item.comments:
            if subtitle:
                subtitle += ', '
            subtitle += item.comments

        wf.add_item(title=item.service,
                    subtitle=subtitle,
                    arg=item.service + '|||' + ('internet' if item.type == 'inet' else 'generic'),
                    valid=True,
                    icon=icon)

    # Send the results to Alfred as XML
    wf.send_feedback()
    return 0

if __name__ == u"__main__":
    wf = Workflow()
    wf.magic_prefix = 'wf:'  # Change prefix to `wf:`

    def opensettings():
        subprocess.call(['open', wf.settings_path])
        return 'Opening workflow settings...'

    wf.magic_arguments['settings'] = opensettings
    sys.exit(wf.run(main))