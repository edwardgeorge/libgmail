#!/usr/bin/python2.3
#
# gmailsmtp.py -- Demo to allow smtp delivery via Gmail
#
# $Revision$ ($Date$)
#
# Author: follower@myrealbox.com
#
# License: GPL 2.0
#

import os
import sys
import email
import base64
import asyncore

import smtpd

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



ga = None

class GmailSmtpProxy(smtpd.SMTPServer):
    """
    """

    def process_message(self, peer, mailfrom, rcpttos, data):
        """
        """
        result = None

        body = ""
        attachments = []
        
        msg = email.message_from_string(data)

        #import pdb; pdb.set_trace()

        # Handle attachments, if present.
        if msg.is_multipart():
            for part in msg.get_payload():
                if part.get_content_type() == "text/plain":
                    # TODO: Do we need to handle "message/rfc822" too?
                    body = part.get_payload()
                else:
                    attachments.append(part)
        else:
            body = msg.get_payload()

        gmsg = libgmail.GmailComposedMessage(to = msg["To"],
                                             subject = msg["Subject"],
                                             body = body,
                                             files = attachments)

        # Don't drop connection until we know we delivered...
        if not ga.sendMessage(gmsg):
            result = "Could not deliver."

        return result


    def handle_accept(self):
        conn, addr = self.accept()
        print >> smtpd.DEBUGSTREAM, 'Incoming connection from %s' % repr(addr)
        channel = ESMTPChannel(self, conn, addr)


class ESMTPChannel(smtpd.SMTPChannel):
    """
    """
    
    def smtp_EHLO(self, arg):
        if not arg:
            self.push('501 Syntax: EHLO hostname')
            return
##        if self.__greeting:
        if self._SMTPChannel__greeting:
            self.push('503 Duplicate HELO/EHLO')
        else:
##             self.__greeting = arg
##             self.push('250 %s' % self.__fqdn)
            self._SMTPChannel__greeting = arg
            self.push('250-%s' % self._SMTPChannel__fqdn)
            self.push('250 AUTH LOGIN PLAIN')


    def smtp_AUTH(self, arg):
        """
        """
        kind, data = arg.split(" ")
        # TODO: Ensure kind == "PLAIN"

        data = base64.decodestring(data)[1:]
        user, pw = data.split("\x00")

        global ga
        ga = libgmail.GmailAccount(user, pw)
        
        try:
            ga.login()
        except:
            self.push("535 Authorization failed")
        else:
            self.push('235 Ok')


if __name__ == "__main__":

    #smtpd.DEBUGSTREAM = sys.stderr

    server = GmailSmtpProxy(("localhost", 8025), None)

    asyncore.loop()
