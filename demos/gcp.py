#!/usr/bin/python2.3
#
# gcp.py -- Demo to copy a file to Gmail using libgmail
#
# $Revision$ ($Date$)
#
# Author: follower@myrealbox.com
#
# License: GPL 2.0
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

    # TODO: Allow copy from account.

    try:
        filename = sys.argv[1]
        destination = sys.argv[2]
    except IndexError:
        print "Usage: %s <filename> <account>:[<label>/]" % sys.argv[0]
        raise SystemExit

    name, label = destination.split(":", 1)

    if label.endswith("/"):
        label = label[:-1]

    if not label:
        label = None
        
    pw = getpass("Password: ")

    ga = libgmail.GmailAccount(name, pw)

    print "\nPlease wait, logging in..."

    try:
        ga.login()
    except libgmail.GmailLoginFailure:
        print "\nLogin failed. (Wrong username/password?)"
    else:
        print "Log in successful.\n"

        if ga.storeFile(filename, label=label):
            print "File `%s` stored successfully in `%s`." % (filename, label)
        else:
            print "Could not store file."

        print "Done."
