#!/usr/bin/python2.3
#
# gmailftpd.py -- Demo to allow retrieval of attachments via FTP.
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
# Note: Requires messages to be marked with a label named "ftp".
#       (This requirement can be removed.)
#
# TODO: Handle duplicate file names...
#

import sys
import os
import time
import socket
import asyncore
import asynchat

program = sys.argv[0]
__version__ = 'Python Gmail FTP proxy version 0.0.1'

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


class Devnull:
    def write(self, msg): pass
    def flush(self): pass


DEBUGSTREAM = Devnull()
NEWLINE = '\n'
EMPTYSTRING = ''


nextPort = 9021
my_cwd = ""
my_user = ""
ga = None

class FTPChannel(asynchat.async_chat):

    def __init__(self, server, conn, addr):
        asynchat.async_chat.__init__(self, conn)
        self.__server = server
        self.__conn = conn
        self.__addr = addr
        self.__line = []
        self.__fqdn = socket.getfqdn()
        self.__peer = conn.getpeername()
        print >> DEBUGSTREAM, 'Peer:', repr(self.__peer)
        self.push('220 %s %s' % (self.__fqdn, __version__))
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
        method = getattr(self, 'ftp_' + command, None)
        if not method:
            self.push('502 Error: command "%s" not implemented' % command)
            return
        method(arg)
        return

    def ftp_USER(self, arg):
        if not arg:
            self.push('501 Syntax: USER username')
        else:
            global my_user
            my_user = arg
            self.push('331 Password required')

    def ftp_PASS(self, arg = ''):
        global ga
        ga = libgmail.GmailAccount(my_user, arg)

        try:
            ga.login()
        except libgmail.GmailLoginFailure:
            self.push('530 Login failed. (Wrong username/password?)')
        else:
            self.push('230 User logged in')

    def ftp_LIST(self, arg):
        self._activeDataChannel.cmd = "LIST " + str(arg)
        self.push('226 ')

    def ftp_RETR(self, arg):
        """
        """
        self._activeDataChannel.cmd = "RETR " + str(arg)
        self.push('226 ')

    def ftp_PASV(self, arg):
        global nextPort
        PORT = nextPort
        nextPort += 1
        ADDR = ('127.0.0.1', PORT)
        self._activeDataChannel = DataChannel(ADDR)
        self.push('227 =127,0,0,1,%d,%d' % (PORT / 256, PORT % 256))
        self.push('150 ')

    def ftp_QUIT(self, arg):
        # args is ignored
        self.push('221 Bye')
        self.close_when_done()

    def ftp_CWD(self, arg):
        global cwd
        cwd = arg
        self.push('250 OK')

files = {}

class DataChannel(asyncore.dispatcher):
    """
    """
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

        self.cmd = ""

    def handle_accept(self):
        conn, addr = self.accept()

        self.conn = conn

        if self.cmd.startswith('LIST'):
            r = ga.getMessagesByLabel('ftp')
            filenames = []
            for th in r:
                for m in th:
                    for a in m.attachments:
                        files[a.filename] = a

            conn.sendall("\r\n".join(files.keys()) + "\r\n")
        elif self.cmd.startswith('RETR'):
            name_req = self.cmd[5:]
            conn.sendall(files[name_req].content)

        conn.close()


class FTPServer(asyncore.dispatcher):
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
        channel = FTPChannel(self, conn, addr)

        

if __name__ == '__main__':
    DEBUGSTREAM = sys.stderr
    
    proxy = FTPServer(('127.0.0.1', 8021))

    try:
        asyncore.loop()
    except KeyboardInterrupt:
        pass
