#!/usr/bin/env python
'''
readmail.py -- Demo to read all messages in gmail account for folders
License: GPL 2.0
Copyright 2006 leogregianin@users.sourceforge.net
'''

import sys
from getpass import getpass
import libgmail

if __name__ == "__main__":
    try:
        name = sys.argv[1]
    except IndexError:
        name = raw_input("Gmail account name: ")
        
    pw = getpass("Password: ")

    ga = libgmail.GmailAccount(name, pw)

    print "\nPlease wait, logging in..."

    try:
        ga.login()
    except libgmail.GmailLoginFailure,e:
        print "\nLogin failed. (%s)" % e.message
        sys.exit(1)
    else:
        print "Login successful.\n"

    FOLDER_list = {'U_INBOX_SEARCH' : 'inbox',
                   'U_STARRED_SEARCH' : 'starred',
                   'U_ALL_SEARCH' : 'all',
                   'U_DRAFTS_SEARCH' : 'drafts' ,
                   'U_SENT_SEARCH' : 'sent',
                   'U_SPAM_SEARCH' : 'spam',
                   }

    FOLDER_list = raw_input('Choose a folder (inbox, starred, all, drafts, sent, spam): ')
    folder = ga.getMessagesByFolder(FOLDER_list)

    for thread in folder:
        print thread.id, len(thread), thread.subject
        choice = raw_input('Read this message? [y/n/q]: ')
        try:
            if choice == 'y':
                for msg in thread:
                    print ">"*79
                    print '\n',msg.id, msg.number, msg.subject
                    # As the source contains the whole message including the
                    # header we try to split the message and provide a more
                    # condensed header.
                    # Here we loop through the message to fetch some header
                    # fields.
                    for line in msg.source.split('\n'):
                        if 'From:' in line or 'Date' in line:
                            print line
                    # We assume 'Date:' to be the last line from the header.
                    # We split again at '\n' to loose the first line which will
                    # be the remainder of the 'Date' line.
                    body = msg.source.split('Date:',1)[-1].split('\n',1)[1]
                    print body   
                    print ">"*79
            elif choice == 'q':
                break
            elif choice =='n':
                pass
            else:
                print '\nInput certain code, next message...\n'
        except KeyboardInterrupt:
            break
            
    print "\n\nDone."
