#!/usr/bin/python2.3
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

    
FOLDER_NAMES = ['all',
                libgmail.FOLDER_INBOX,
                libgmail.FOLDER_SENT] # TODO: Get on the fly.
if __name__ == "__main__":
    from getpass import getpass
    
    name = raw_input("Gmail account name: ")
    pw = getpass("Password: ")

    ga = libgmail.GmailAccount(name, pw)

    print "\nPlease wait, logging in..."

    ga.login()

    print "Log in successful.\n"

    while 1:
        try:
            print "Select folder to archive: (Ctrl-C to exit)"
            print "Note: Only first page of results will be archived."
            for optionId, folderName in enumerate(FOLDER_NAMES):
                print "  %d. %s" % (optionId, folderName)

            folderName = FOLDER_NAMES[int(raw_input("Choice: "))]

            folder = ga.getFolder(folderName)

            print
            for thread in folder:
                print
                print thread.id, len(thread), thread.subject

                for msg in thread:
                    print "  ", msg.id, msg.number, msg.subject
                    open("%s-%s.msg" % (thread.id, msg.number), "w").write(ga.getRawMessage(msg.id))

            print
        except KeyboardInterrupt:
            print "\n\nDone."
            break
    
