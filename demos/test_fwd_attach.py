#!/usr/bin/python2.3

#
# Usage: test_fwd_attach.py <account> <password> <recipient> <subject>
#

# This example forwards the first attachment from the search for "<subject>"
# to the recipient.
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

account, pw, recipient, searchSubject = sys.argv[1:]

ga = libgmail.GmailAccount(account, pw)
ga.login()

sr = ga.getMessagesByQuery("subject:%s" % searchSubject)

attachmentId = None

for thread in sr:
    for msg in thread:
        if msg.attachments:
            attachmentId = msg.attachments[0]._fullId
            break # Just use the first result.

if not attachmentId:
    print "No attachment found."
    raise SystemExit


cm = libgmail.GmailComposedMessage(to=recipient,
                                   subject="File attachment from: %s" % msg.subject,
                                   body="body")

# Note: At present we can only have one forwarded attachment because
#       we're using a dictionary for the parameters, and all attachments
#       have the field name "attach".
# TODO: Allow multiple forwarded attachments. (Probably by adding to the
#       `_paramsToMime` function, although that's kinda hacky.)
if ga.sendMessage(cm, _extraParams = {'attach': attachmentId}):
    print "Succeeded."
else:
    print "Failed."
