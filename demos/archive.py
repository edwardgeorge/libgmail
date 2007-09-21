#!/usr/bin/env python
#
# archive.py -- Demo to archive all threads in a Gmail folder
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
import re
import time

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
        name = sys.argv[1]
    except IndexError:
        name = raw_input("Gmail account name: ")
        
    pw = getpass("Password: ")

    ga = libgmail.GmailAccount(name, pw)

    print "\nPlease wait, logging in..."

    try:
        ga.login()
    except libgmail.GmailLoginFailure:
        print "\nLogin failed. (Wrong username/password?)"
    else:
        print "Log in successful.\n"

        searches = libgmail.STANDARD_FOLDERS + ga.getLabelNames()

        while 1:
            try:
                print "Select folder or label to archive: (Ctrl-C to exit)"
                print "Note: *All* pages of results will be archived."

                for optionId, optionName in enumerate(searches):
                    print "  %d. %s" % (optionId, optionName)

                name = searches[int(raw_input("Choice: "))]

                if name in libgmail.STANDARD_FOLDERS:
                    result = ga.getMessagesByFolder(name, True)
                else:
                    result = ga.getMessagesByLabel(name, True)

                print
                from_re = re.compile('^(>*From )', re.MULTILINE)
                if len(result):
                    now = time.strftime("%Y-%m-%d_%H.%M.%S")
                    mbox = open("archive-%s-%s.mbox" % (name, now), "w")
                    try:
                        for thread in result:
                            print
                            print thread.id, len(thread), thread.subject

                            for msg in thread:
                                print "  ", msg.id, msg.number, msg.subject
                                mbox.write("From - Thu Jan 22 22:03:29 1998\n")
                                source = msg.source.replace("\r","").lstrip()
                                mbox.write(from_re.sub('>\\1', source))
                                mbox.write("\n\n")
                    finally:
                        mbox.close()
                else:
                    print "No threads found in `%s`." % name
                print
                    
            except KeyboardInterrupt:
                break

    print "\n\nDone."
    
