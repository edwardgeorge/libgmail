#!/usr/bin/python2.3
#
# unreadmsgcount.py -- Demo to return unread message count with saved state
#
# $Revision$ ($Date$)
#
# Author: follower@myrealbox.com
#
# License: GPL 2.0
#
#
# This demo intends to show how account state can be saved between script
# runs.
#
import os
import sys
import logging

# Allow us to run using installed `libgmail` or the one in parent directory.
try:
    import libgmail
    logging.warn("Note: Using currently installed `libgmail` version.")
except ImportError:
    # Urghhh...
    sys.path.insert(1,
                    os.path.realpath(os.path.join(os.path.dirname(__file__),
                                                  os.path.pardir)))

    import libgmail

    
if __name__ == "__main__":
    import sys
    from getpass import getpass

    try:
        filename = sys.argv[1]
    except IndexError:
        print "Usage: %s <state filename>" % sys.argv[0]
        raise SystemExit

    if not os.path.isfile(filename):
        name = raw_input("Gmail account name: ")
        pw = getpass("Password: ")
        ga = libgmail.GmailAccount(name, pw)

        print "\nPlease wait, logging in..."

        try:
            ga.login()
        except libgmail.GmailLoginFailure:
            print "\nLogin failed. (Wrong username/password?)"
            raise SystemExit

        print "Log in successful.\n"
    else:
        print "\nDon't wait, not logging in... :-)"
        ga = libgmail.GmailAccount(
            state = libgmail.GmailSessionState(filename = filename))

    print "Unread messages: %s" % ga.getUnreadMsgCount()

    print "Saving state..."
    state = libgmail.GmailSessionState(account = ga).save(filename)

    print "Done."
