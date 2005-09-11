#!/usr/bin/env python
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
# Major rewrite of the datachannel handeling by Willy De la Court <wdl@linux-lovers.be>
#
# Note: Requires messages to be marked with a label named "ftp".
#       (This requirement can be removed.)
#
# TODO: Handle duplicate file names...
#

import sys
import os
import re
import time
import socket
import asyncore
import asynchat
import logging

program = sys.argv[0]
__version__ = 'Python Gmail FTP proxy version 0.0.3'

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
        self.my_type = "A"
        self.my_cwd = ""
        self.my_user = ""
        self.filenames = {}
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

    def get_filelist(self):
        """
        Get the file list from GMail
        """
        r = self.ga.getMessagesByLabel('ftp')
        for th in r:
            for m in th:
                for a in m.attachments:
                    self.filenames[a.filename] = a

    def ftp_USER(self, arg):
        """
        Process USER ftp command
        """
        if not arg:
            self.push('501 Syntax: USER username')
        else:
            self.my_user = arg
            self.push('331 Password required')

    def ftp_PASS(self, arg = ''):
        """
        Process PASS ftp command
        """
        self.ga = libgmail.GmailAccount(self.my_user, arg)

        try:
            self.ga.login()
        except libgmail.GmailLoginFailure:
            self.push('530 Login failed. (Wrong username/password?)')
        else:
            self.push('230 User logged in')

    def ftp_LIST(self, arg):
        """
        Process LIST ftp command
        """
        self.filenames = {}
        self._activeDataChannel.cmd = "LIST " + str(arg)
        self._activeDataChannel.handle_LIST()

    def ftp_RNFR(self, arg):
        """
        Process RNFR ftp command
        """
        self.push('350 File exists, ready for destination name')

    def ftp_RNTO(self, arg):
        """
        Process RNTO ftp command
        """
        self.push('250 RNTO command successful.')

    def ftp_SIZE(self, arg):
        """
        Process SIZE ftp command
        """
        name_req = arg
        if name_req[:1] == '/':
           name_req = name_req[1:]
        try:
           response = "213 %d" % (self.filenames[name_req].filesize)
        except:
           self.push("550 %s: No such file or directory." % (name_req))
        else:
           self.push(response)

    def ftp_RETR(self, arg):
        """
        Process RETR ftp command
        """
        self._activeDataChannel.cmd = "RETR " + str(arg)
        self._activeDataChannel.handle_RETR()


    def ftp_STOR(self, arg):
        """
        Process STORE ftp command
        """
        # TODO: Check this is legit, don't just copy & paste from RETR...
        self._activeDataChannel.cmd = "STOR " + str(arg)
        self._activeDataChannel.handle_STOR()


    def ftp_PASV(self, arg):
        """
        Process PASV ftp command
        """
        # *** TODO: Don't allow non-binary file transfers here?
        global nextPort
        PORT = nextPort
        nextPort += 1
        ADDR = ('127.0.0.1', PORT)
        self._activeDataChannel = DataChannel(ADDR, self)
        self.push('227 =127,0,0,1,%d,%d' % (PORT / 256, PORT % 256))


    def ftp_QUIT(self, arg):
        """
        Process QUIT ftp command
        """
        # args is ignored
        self.push('221 Bye')
        self.close_when_done()


    def ftp_CWD(self, arg):
        """
        Process CWD ftp command
        """
        # TODO: Attach CWD (and other items) to channel...
        self.my_cwd = arg
        self.push('550 ' + self.my_cwd + ': No such file or directory.')

    def ftp_PWD(self, arg):
        """
        Process PWD ftp command
        """
        self.push('257 "/" is current directory.')


    def ftp_TYPE(self, arg):
        """
        Process TYPE ftp command
        """
        response = '200 OK'

        if arg in ["A", "A N"]:
            self.my_type = "A"
        elif arg in ["I", "L 8"]:
            self.my_type = "I"
        else:
            response = "504 Unsupported TYPE parameter"

        self.push(response)


import tempfile

class DataChannel(asyncore.dispatcher):
    """
    """
    def __init__(self, localaddr, ControlChannel):
        self._ControlChannel = ControlChannel
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
        """
        Start the DATA connection
        """
        conn, addr = self.accept()

        self._ControlChannel.push('150 Opening data connection.')

        self.conn = conn

    def handle_LIST(self):
        """
        Send the data response for the LIST command
        """
        self._ControlChannel.get_filelist()
        result = ""
        for file in self._ControlChannel.filenames.keys():
            result = result + "-rw-r--r--   1 %s %s %10d Jan  1  2000 %s\r\n" % (self._ControlChannel.my_user, self._ControlChannel.my_user, self._ControlChannel.filenames[file].filesize, self._ControlChannel.filenames[file].filename)
        self.conn.sendall(result)
        self._ControlChannel.push('226 Transfer complete.')
        self.close()
        self.conn.close()

    def handle_RETR(self):
        """
        Send the file for the RETR command
        """
        if self._ControlChannel.my_type != "I":
            self._ControlChannel.push('426 Only binary transfer mode is supported')
            self.close()
            self.conn.close()
            return

        name_req = self.cmd[5:]
        # Remove leading /
        if name_req[:1] == '/':
            name_req = name_req[1:]
        print >> DEBUGSTREAM, "Reading `%s`." % (name_req)
        # check if the file exists
        try:
            name = self._ControlChannel.filenames[name_req].filename
        except KeyError:
            # if not the list is probably not read yet
            self._ControlChannel.get_filelist()
        # try again
        try:
            self.conn.sendall(self._ControlChannel.filenames[name_req].content)
            response = '226 Transfer complete.'
        except KeyError:
            response = '550 ' + name_req + ': No such file or directory.'
        self._ControlChannel.push(response)
        self.close()
        self.conn.close()

    def handle_STOR(self):
        """
        Receive the file for the STOR command
        """
        if self._ControlChannel.my_type != "I":
            self._ControlChannel.push('426 Only binary transfer mode is supported')
            self.close()
            self.conn.close()
            return

        buffer = ""
        while True:
            data = self.conn.recv(1024)
            if not data:
                break
            buffer += data

        filename = self.cmd[5:]
        # Remove leading /
        if filename[:1] == '/':
            filename = filename[1:]
        tempDir = tempfile.mkdtemp()
        # Remove trailing '.part' KDE uses this to upload files
        tempFileName = re.sub('\.part', '', filename)
        tempFilePath = os.path.join(tempDir, tempFileName)
        print >> DEBUGSTREAM, "Writing `%s` to `%s`." % (filename, tempFilePath)
        open(tempFilePath, "wb").write(buffer)

        self._ControlChannel.ga.storeFile(tempFilePath, "ftp")

        os.remove(tempFilePath)
        os.rmdir(tempDir)
        self._ControlChannel.push('226 Transfer complete.')
        self.close()
        self.conn.close()

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
