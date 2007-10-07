#!/usr/bin/env python
'''
readmail.py -- Demo to read all messages in gmail account for folders
License: GPL 2.0
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
        choice = raw_input('Read this message? [y/n]: ')
        try:
            if choice == 'y':
                for msg in thread:
                    print "  ", msg.id, msg.number, msg.subject
                    # TODO: print compact header
                    # header = ['From', 'Date', 'Subject']
                    # for k in header:
                    #    print k,':',msg.source[k]
                    print msg.source
            elif choice =='n':
                pass
            else:
                print '\nInput certain code, next message...\n'
        except KeyboardInterrupt:
            break
            
    print "\n\nDone."
