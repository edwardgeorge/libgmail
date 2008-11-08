#!/usr/bin/env python
"""
libgmail test suite

Tests:
Very little, at this point :)
"""
import unittest
import time
from libgmail import *
import getpass

class LibgmailTests(unittest.TestCase):
    """
    Set of tests that exercise very basic libgmail functionality
    """
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_utf8(self):
        f = account.getMessagesByFolder(U_INBOX_SEARCH, True)
        for t in f:
            for m in t:
                w = m.source
                for attach in m.attachments:
                    a = attach.content

    def test_send_and_receive_mail(self):
        if account.domain:
            name = account.name + '@' + account.domain
        else:
            name = account.name + '@gmail.com'
        subject = "libgmail test subject"
        body = """
        Hi, I am a unit test of libgmail. Ignore this message,
        if you dare. Seriously, I won't be offended if you
        ignore it. And you probably should, since right
        now, the test suite doesn't delete this message
        from your trash, sooo.... it'll just linger.

        "You've got me wrapped around your finger /
        did you have to let it linger?
        did you have to?
        did you have to?
        did you have to let it linger?"

        etc.
        """
        msg = GmailComposedMessage(to=name, subject=subject,
                                   body=body)
        output = account.sendMessage(msg)

        # Now go to the inbox and attempt to retrieve
        # this message
        # Sleep for like, ten seconds, so that we can
        # actually get the message
        time.sleep(10)
        result = account.getMessagesByFolder(U_INBOX_SEARCH)
        # We'd better be in the first thread
        thread = result[0]
        first = thread[0]
        self.assertEqual(first.subject, first.subject)
        self.assertEqual(first.to[0], msg.to)
        # Now send the message to the trash
        account.trashMessage(first)

if __name__ == '__main__':
    #unittest.main()
    ## With this we get a better output
    print "\n=============================================="
    print "Start 'libgmail' testsuite"
    print "------------------------------------------------\n"
    print "WARNING: THIS TEST MAY DELETE/REARRANGE"
    print "         YOUR ADDRESSBOOK/EMAILS"
    print "PLEASE DON'T RUN IT ON A REAL ACCOUNT"
    
    name = raw_input("Gmail account name: ")
    pw = getpass.getpass("Password: ")
    domain = raw_input("Domain [leave blank for gmail]: ")
    account = GmailAccount(name, pw, domain=domain)

    try:
        account.login()
        print "Login successful.\n"
    except GmailLoginFailure,e:
        print "\nLogin failed. (%s)" % e.message
    else:
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(LibgmailTests))
        unittest.TextTestRunner(verbosity=2).run(suite)
