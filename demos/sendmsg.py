#!/usr/bin/env python
#
# sendmsg.py -- Demo to send a message via Gmail using libgmail
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
    ## Wouldn't this the preffered way?
    ## We shouldn't raise a warning about a normal import
    ##logging.warn("Note: Using currently installed `libgmail` version.")
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
        name = sys.argv[1]
        to = sys.argv[2]
        subject = sys.argv[3]
        msg = sys.argv[4]
    except IndexError:
        print "Usage: %s <account> <to address> <subject> <body>" % sys.argv[0]
        raise SystemExit
        
    pw = getpass("Password: ")

    ga = libgmail.GmailAccount(name, pw)

    print "\nPlease wait, logging in..."

    try:
        ga.login()
    except libgmail.GmailLoginFailure:
        print "\nLogin failed. (Wrong username/password?)"
    else:
        print "Log in successful.\n"
        gmsg = libgmail.GmailComposedMessage(to, subject, msg)

        if ga.sendMessage(gmsg):
            print "Message sent `%s` successfully." % subject
        else:
            print "Could not send message."

        print "Done."
