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

    ga.login()

    print "Log in successful.\n"

    while 1:
        try:
            print "Select folder to archive: (Ctrl-C to exit)"
            print "Note: *All* pages of results will be archived."
            for optionId, folderName in enumerate(libgmail.STANDARD_FOLDERS):
                print "  %d. %s" % (optionId, folderName)

            folderName = libgmail.STANDARD_FOLDERS[int(raw_input("Choice: "))]

            folder = ga.getFolder(folderName, True)

            print
            mbox = []
            if len(folder):
                for thread in folder:
                    print
                    print thread.id, len(thread), thread.subject

                    for msg in thread:
                        print "  ", msg.id, msg.number, msg.subject
                        # TODO: Rename "body" to "source".
                        source = msg.body.replace("\r","").lstrip()
                        mbox.append("From - Thu Jan 22 22:03:29 1998\n")
                        mbox.append(source)
                        mbox.append("\n\n") #TODO:Check if we need either/both?
                import time 
                open("archive-%s-%s.mbox" % (folderName, time.time()),
                     "w").writelines(mbox)
            else:
                print "No threads found in folder `%s`." % folderName
            print
                
        except KeyboardInterrupt:
            print "\n\nDone."
            break
    
