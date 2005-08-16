#!/usr/bin/env python
#
# gmailpopd.py -- Demo to provide POP3 proxy for Gmail message retrieval..
#
# $Revision$ ($Date$)
#
# Author: follower@myrealbox.com
#
# License: Dual GPL 2.0 and PSF (This file only.)
#
#
# Based on smtpd.py by Barry Warsaw <barry@python.org> (Thanks Barry!)
#

import sys
import os
import time
import socket
import asyncore
import asynchat

program = sys.argv[0]
__version__ = 'Python Gmail POP3 proxy version 0.0.1'

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


from libgmail import U_AS_SUBSET_UNREAD


class Devnull:
    def write(self, msg): pass
    def flush(self): pass


DEBUGSTREAM = Devnull()
NEWLINE = '\n'
EMPTYSTRING = ''


# TODO: Get rid of this global stuff...
my_user = ""
snapshot = None # Account snapshot...

class GmailAccountSnapshot:
    """
    """

    def __init__(self, ga):
        """
        """
        self.account = ga
        # TODO: Work out at what stage messages get marked as 'read'.
        #       (as I think of it, it happens when I retrieve the
        #        messages in the threads, should really preserve read/unread
        #        state then.)
        # TODO: Fix this so it does not retrieve messages that have already
        #       been read. ("unread" is a property of thread in this case?)
        #       Is this even possible without caching stuff ourselves,
        #       maybe use "archive" as the equivalent of read?
        self._unreadThreads = ga.getMessagesByQuery("is:" + U_AS_SUBSET_UNREAD,
                                                    True)#TODO:True as default?
        self.unreadMsgs = []
        for thread in self._unreadThreads:
            for msg in thread:
                self.unreadMsgs.append(msg)


    def retrieveMessage(self, msgNumber, bodyLines = None):
        """

        Returns an array of lines... (TODO: Decide if we want this.)        
        """
        # TODO: Check request is in range...
        # TODO: Don't retrieve all of the message, just what's needed.
        msgContent = self.unreadMsgs[msgNumber].source

        msgContent = _massage(msgContent)# TODO: Remove this...

        msgLines = msgContent.split("\r\n")

        if bodyLines is not None:
            blankIndex = msgLines.index("") # Blank line between header & body.
            msgLines = msgLines[:blankIndex + 1 + bodyLines]

        return msgLines            

                
class POPChannel(asynchat.async_chat):

    def __init__(self, server, conn, addr):
        asynchat.async_chat.__init__(self, conn)
        self.__server = server
        self.__conn = conn
        self.__addr = addr
        self.__line = []
        self.__fqdn = socket.getfqdn()
        self.__peer = conn.getpeername()
        print >> DEBUGSTREAM, 'Peer:', repr(self.__peer)
        self.push('+OK %s %s' % (self.__fqdn, __version__))
        self.set_terminator('\r\n')

        self._activeDataChannel = None
        

    # Overrides base class for convenience
    def push(self, msg):
        asynchat.async_chat.push(self, msg + '\r\n')

    # Implementation of base class abstract method
    def collect_incoming_data(self, data):
        self.__line.append(data)

    # Implementation of base class abstract method
    def found_terminator(self):
        line = EMPTYSTRING.join(self.__line)
        print >> DEBUGSTREAM, 'Data:', repr(line)
        self.__line = []
        if not line:
            self.push('500 Error: bad syntax')
            return
        method = None
        i = line.find(' ')
        if i < 0:
            command = line.upper()
            arg = None
        else:
            command = line[:i].upper()
            arg = line[i+1:].strip()
        method = getattr(self, 'pop_' + command, None)
        if not method:
            self.push('-ERR Error : command "%s" not implemented' % command)
            return
        method(arg)
        return


    def pop_USER(self, arg):
        if not arg:
            self.push('-ERR: Syntax: USER username')
        else:
            global my_user
            my_user = arg
            self.push('+OK Password required')


    def pop_PASS(self, arg = ''):
        """
        """
        ga = libgmail.GmailAccount(my_user, arg)

        try:
            ga.login()
        except libgmail.GmailLoginFailure:
            self.push('-ERR Login failed. (Wrong username/password?)')
        else:
            # For the moment this is our form of "locking the maildrop".
            global snapshot
            snapshot = GmailAccountSnapshot(ga)
            
            self.push('+OK User logged in')


    def pop_STAT(self, arg):
        """
        """
        # We define "Mail Drop" as being unread messages.
        # TODO: Handle presenting all messages using read=deleted approach
        #       or would it be better to be read=archived?
        
        # We just use a dummy mail drop size here at present, hope it causes
        # no problems...
        # TODO: Determine actual drop size... (i.e. always download msgs)
        mailDropSize = 1
        
        self.push('+OK %d %d' % (len(snapshot.unreadMsgs), mailDropSize))


    def pop_LIST(self, arg):
        """
        """
        DUMMY_MSG_SIZE = 1 # TODO: Determine actual message size.
        if not arg:
            # TODO: Change all of this to operate on an account snapshot?
            msgCount = len(snapshot.unreadMsgs)
            self.push('+OK')
            for msgIdx in range(1, msgCount + 1):
                self.push('%d %d' % (msgIdx, DUMMY_MSG_SIZE))
            self.push(".")
        else:
            # TODO: Handle per-msg LIST commands
            raise NotImplementedError
                

    def pop_RETR(self, arg):
        """
        """
        if not arg:
            self.push('-ERR: Syntax: RETR msg')
        else:
            # TODO: Check request is in range...
            msgNumber = int(arg) - 1 # Argument is 1 based, sequence is 0 based
            
            self.push('+OK')

            for msgLine in byteStuff(snapshot.retrieveMessage(msgNumber)):
                self.push(msgLine)

            self.push('.') # TODO: Make constant...


    def pop_TOP(self, arg):
        """
        """
        if not arg:
            self.push('-ERR: Syntax: RETR msg')
        else:
            msgNumber, bodyLines = arg.split(" ")
            # TODO: Check request is in range...
            msgNumber = int(msgNumber) - 1 # Argument is 1 based, sequence is 0 based
            bodyLines = int(bodyLines)
            
            self.push('+OK')

            for msgLine in byteStuff(snapshot.retrieveMessage(msgNumber, bodyLines)):
                self.push(msgLine)

            self.push('.') # TODO: Make constant...

    
    def pop_QUIT(self, arg):
        # args is ignored
        self.push('+OK Goodbye')
        self.close_when_done()


def byteStuff(lines):
    """
    """
    for line in lines:
        if line.startswith("."):
            line = "." + line
        yield line


def _massage(msgContent):
    """
    """
    # TODO: Put this message massaging in `GmailMessage.source`
    #       and standardise how message ends? (e.g. '\r\n' not '\n')
    msgContent = msgContent.lstrip()
    msgContent += "\r\n"
    return msgContent


class POP3Proxy(asyncore.dispatcher):
    def __init__(self, localaddr):
        self._localaddr = localaddr
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        # try to re-use a server port if possible
        self.set_reuse_addr()
        self.bind(localaddr)
        self.listen(5)
        print >> DEBUGSTREAM, \
              '%s started at %s\n\tLocal addr: %s\n' % (
            self.__class__.__name__, time.ctime(time.time()),
            localaddr)

    def handle_accept(self):
        conn, addr = self.accept()
        print >> DEBUGSTREAM, 'Incoming connection from %s' % repr(addr)
        channel = POPChannel(self, conn, addr)

        

if __name__ == '__main__':
    DEBUGSTREAM = sys.stderr
    
    proxy = POP3Proxy(('127.0.0.1', 8110))

    try:
        asyncore.loop()
    except KeyboardInterrupt:
        pass
