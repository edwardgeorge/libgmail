#!/usr/bin/python2.3

#
# Rough first draft code to use "official" Gmail Notifier protocol
#
# Author: follower@myrealbox.com
#
# License: GPL 2.0
# 
# Obviously this all needs to be turned into something state-machiney
# eventually.
#
# ObBlah: This program is for educational or interoperability purposes.
# 

import os
import sys

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

r = '\n\x82\x02\x10\x93\xdd\xf8\xab\x87\x99\xa7\xf5\x0f\x18\xc9\x8c\xb2\xce\xea\x1f\x82\x01\x04^all\x82\x01\x02^f\x82\x01\x02^i\x82\x01\x02^u\x92\x01\x1e\n\x18\n\x12xxxxxxxx@gmail.com\x12\x02me\x10\x01\x18\x01\x98\x01\x02\xa2\x01\x97\x01[Test] This is a really really really really really really really really blah blah blah blah long subject line blah blah 123456789012345678901234567890\xaa\x01\x16So, did you see it all\xb8\x01\x01\n\xfa\x01\x10\xd0\x8a\xb8\x97\xf5\xcd\xa4\xf5\x0f\x18\xbd\xea\x9b\xc9\xea\x1f\x82\x01\x04^all\x82\x01\x02^i\x82\x01\x02^u\x92\x01,\n&\n\x18gmail-noreply@google.com\x12\nGmail Team\x10\x01\x18\x01\x98\x01\x02\xa2\x014Xxxxxx Xxxxxxx has accepted your invitation to Gmail\xaa\x01iXxxxxx Xxxxxxx has accepted your invitation to Gmail and has chosen the brand new address xxxxxx &hellip;\xb8\x01\x01\x88\x01\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

from pprint import pprint
#pprint(r.split("\x01"))

from cStringIO import StringIO


def _getCode(s):
    """
    """
    code = ord(s.read(1))
    print "code:", hex(code)

    assert(s.read(1) == "\x01")

    return code


def _getNextBytes(s, nextReadCount = 0):
    """
    """
    if not nextReadCount:
        nextReadCount = ord(s.read(1))
        
    bytes = s.read(nextReadCount)
    print "bytes:", repr(bytes),

    return bytes
    
    

def parseThreadData(s, obj):
    """
    """

    # Data header
    # Unknown initial bytes--maybe message Id?
    ##nextReadCount = 19 # This does not seem to be consistent...
    # TODO: Find out why.
    #
    # Example:
    #
    ## 0x82 02 10 93 dd f8 ab 87 99 a7 f5 0f 18 c9 8c b2 ce ea 1f  code: 0x82
    ## 0xfa 01 10 d0 8a b8 97 f5 cd a4 f5 0f 18 bd ea 9b c9 ea 1f  code: 0x82
    ## 0x7f 10 b8 d5 a2 bf b6 b7 a4 f5 0f 18 f8 ed ee c8 ea 1f  code: 0x82
    ## 0x83 01 10 de 8d d5 8f d6 b3 a4 f5 0f 18 80 ad e7 c8 ea 1f  code: 0x82
    ## 0x89 01 10 e0 be 9e cb f3 a8 a4 f5 0f 18 98 e7 d1 c8 ea 1f  code: 0x82
    ## 0x96 01 10 95 d4 e3 d8 d6 a7 a4 f5 0f 18 d8 ae cf c8 ea 1f  code: 0x82
    ## 0x9e 02 10 94 ba be c9 9b a7 a2 f5 0f 18 a2 b5 ce c4 ea 1f  code: 0x82
    ## 0xc5 01 10 f0 94 d6 dd fb 94 a2 f5 0f 18 87 f6 a9 c4 ea 1f  code: 0x82
    ## 0xf5 01 10 e5 f3 b8 97 cd ab a0 f5 0f 18 9b 99 d7 c0 ea 1f  code: 0x82
    ## 0xf1 01 10 e2 b2 c9 ed f3 96 9b f5 0f 18 87 e7 ad b6 ea 1f  code: 0x82
    ## 0xaa 02 10 8a 8e ab f9 e7 fd 93 f5 0f 18 a5 ce fb a7 ea 1f  code: 0x82
    ## 0x81 02 10 a8 aa f4 f2 80 a7 df f4 0f 18 d0 82 ce be e9 1f  code: 0x82
    ## 0x92 02 10 a0 ae 98 c6 a5 d3 aa f4 0f 18 b8 cb a6 d5 e8 1f  code: 0x82
    ## 0xf8 01 10 8e d5 bf 98 f9 a0 a1 f4 0f 18 81 f2 c1 c2 e8 1f  code: 0x82
    ## 0x9c 02 10 be f1 c5 e6 c9 e5 9a f4 0f 18 88 92 cb b5 e8 1f  code: 0x82
    ## 0x86 02 10 e6 bc 99 ca a0 e5 9a f4 0f 18 f8 c3 ca b5 e8 1f  code: 0x82
    ## 0x87 01 10 91 ce 8d e8 90 96 9a f4 0f 18 90 a2 ac b4 e8 1f  code: 0x82
    ## 0xd3 01 10 be f7 b9 8b 81 b2 99 f4 0f 18 a8 81 e4 b2 e8 1f  code: 0x82
    ## 0xf3 01 10 e6 df b1 c3 ae 9b 97 f4 0f 18 d7 dc b6 ae e8 1f  code: 0x82
    ## 0xf1 01 10 88 95 e0 8f d9 d0 90 f4 0f 18 c4 b0 a1 a1 e8 1f  code: 0x82
    ## 0xef 01 10 cc e0 f9 92 b2 da 8f f4 0f 18 f1 e6 b4 9f e8 1f  code: 0x82
    ## 0xf0 01 10 ac b5 b6 fe af ec 86 f4 0f 18 d3 dd d8 8d e8 1f  code: 0x82
    ## 0x7b 10 fc 82 eb e0 85 a6 86 f4 0f 18 b7 8a cc 8c e8 1f  code: 0x82
    ## 0xa5 01 10 e3 f0 87 db f6 91 86 f4 0f 18 a4 ee a3 8c e8 1f  code: 0x82
    ## 0x73 10 dd a8 e9 b5 ee ea 85 f4 0f 18 ca dd d5 8b e8 1f  code: 0x82

    byteString = "0x"
    while True:
        # Skip unknown bytes (Note: This method probably isn't 100% reliable.)
        # TODO: Work out what they are--there are some similarities.
        #       Guess is date/time/id?
        byte = s.read(1)
        byteString += "%02x " % ord(byte)
        if byte == "\x1f":
            print byteString,
            code = _getCode(s)
            break

    while code != 0x92:

        bytes = _getNextBytes(s) ##, nextReadCount)
        code = _getCode(s)

        ##if code == 0x92:
        ##    break

    fromCount = 0
    while True:
        fromCount +=1
        # Unknown, time/date?
        print "Hard-coded read."
        bytes = _getNextBytes(s, 4)
        print
            
        # From
        bytes = _getNextBytes(s)
        print

        assert(s.read(1) == "\x12")

        bytes = _getNextBytes(s)
        print

        # --- This isn't right/or is messy... ----
        # 0x10 == From?
        # 0x18 == To?
        code = _getCode(s)
        assert((code == 0x10) or (code == 0x18)
               or (code == 0x98) or (code == 0x92))

        if code == 0x98:
            break

        if code == 0x92:
            continue

        byte = _getCode(s)
        if byte == 0x18:
            byte = _getCode(s)

        if byte == 0x98:
            break
        else:
            assert(byte == 0x92)
        # ----------------

    print "fromCount:", fromCount
        
        
    
        #elif code == 0x10:
        #    break

        ##nextReadCount = ord(s.read(1))

        ##print "next:", nextReadCount


    # Unknown
    for nextReadCount in [2]:
        bytes = _getNextBytes(s, nextReadCount)
        print
        
        assert(s.read(1) == "\x01")

    # Subject
    # Extra long (> n, where n = ???) subjects have form:
    #    length, 0x01, subject
    #
    # Shorter length subject have form:
    #    length, subject
    #
    # TODO: Determine what happens when length > 255?
    nextReadCount = ord(s.read(1))

    if s.read(1) != "\x01":
        s.seek(-1, 1)

    bytes = _getNextBytes(s, nextReadCount)
    code = _getCode(s)

    obj.subject = bytes

    # Message snippet
    bytes = _getNextBytes(s)
    code = _getCode(s)

    obj.snippet = bytes

    # End of message data
    #assert(s.read(1) == "\x01")
    threadMsgCount = ord(s.read(1))
    print "threadMsgCount", threadMsgCount
    # TODO: Find some way to make sure this is true...

    


class GmailNotifierResponse:
    """
    """

    def __init__(self, responseData):
        """
        """


# TODO: Merge this with GmailThread?
class GmailNotifierThread:
    """
    """

    def __init__(self, threadData):
        """
        """
        # TODO: Move this to method of this object?
        parseThreadData(threadData, self)
    

if __name__ == "__main__":
    # Change the `0` to a `1` to retrieve a live response.
    if 0:
    
        import sys
        from getpass import getpass

        try:
            name = sys.argv[1]
        except IndexError:
            name = raw_input("Gmail account name: ")

        pw = getpass("Password: ")

        ga = libgmail.GmailAccount(name, pw)

        print "\nPlease wait, logging in..."

        #import pdb; pdb.set_trace()
        ga.login()

        print "Log in successful.\n"

        r = ga._retrievePage("https://gmail.google.com/gmail?ui=pb&q=label:^i%20label:^u")
        #r = ga._retrievePage("https://gmail.google.com/gmail?ui=pb&q=label:^all")

    #print repr(r)
    pprint(r.split("\x01"))

    s = StringIO(r)

    numMsgs = 0

    threads = []

    while True:
        code = ord(s.read(1))

        if code == 0x0a:
            numMsgs += 1
            threads.append(GmailNotifierThread(s))
        elif code == 0x88:
            # trailer
            assert(s.read(1) == "\x01")
            # If there are no messages there's no trailing count?
            msgCount = ord(s.read(1)) # TODO: What about count > 255?
            print "Messages:", msgCount
            print "Messages found:", numMsgs

            # Maximum of 30 Messages?
            try:
                assert(msgCount == numMsgs)
                print "All messages retrieved."
            except AssertionError:
                print "Not all messages retrieved."
                assert(msgCount > 30)
                assert(numMsgs == 30)

            padding = s.read() # Padding ensures data length is power of 2.
            print "padding bytes:", len(padding)
            try:
                assert(len([byte for byte in padding if byte != "\x00"]) == 0)
            except AssertionError:
                # What is the extra data value? ("more", "not all shown"?)
                print "AssertionError: Not all padding blank."
                print repr(padding[:10])

            break
        else:
            raise Exception("Unknown code")

    print "Total length:", len(r)

    print

    for th in threads:
        print th.subject
        print th.snippet
        print
        
