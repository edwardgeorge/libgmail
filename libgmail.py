#!/usr/bin/python2.3
#
# libgmail -- Gmail access via Python
#
# Version: 0.0.2 (XX July 2004)
#
# Author: follower@myrealbox.com
#
# License: GPL 2.0
#
# Requires:
#   * ClientCookie <http://wwwsearch.sourceforge.net/ClientCookie/>
#
# Thanks:
#   * Live HTTP Headers <http://livehttpheaders.mozdev.org/>
#   * Gmail <http://gmail.google.com/>
#   * Google Blogoscoped <http://blog.outer-court.com/>
#   * The *first* big G. :-)
#
# NOTE:
#   You should ensure you are permitted to use this script before using it
#   to access Google's Gmail servers.
#
#
# Gmail Implementation Notes
# ==========================
#
# * Folders contain message threads, not individual messages. At present I
#   do not know any way to list all messages without processing thread list.
#

from constants import *

import ClientCookie

import re
import urllib
import logging

URL_LOGIN = "https://www.google.com/accounts/ServiceLoginBoxAuth"
URL_GMAIL = "https://gmail.google.com/gmail"

FOLDER_INBOX = "inbox"
FOLDER_SENT = "sent"


## This class is from the ClientCookie docs.
## TODO: Do all this cleanly.
# Build an opener that *doesn't* automatically call .add_cookie_header()
# and .extract_cookies(), so we can do it manually without interference.
class NullCookieProcessor(ClientCookie.HTTPCookieProcessor):
    def http_request(self, request): return request
    def http_response(self, request, response): return response



## TODO: Do this properly.
import time
def _bakeQuickCookie(name, value, path, domain):
    """
    Kludge to work around no easy way to create Cookie with defaults.
    (Defaults taken from Usenet post by `ClientCookie` author.)
    """
    return ClientCookie.Cookie(0, name, value, None, 0,
                               domain, True, domain.startswith("."),
                               path, True,
                               True,  # true if must only be sent via https
                               time.time()+(3600*24*365),  # expires
                               0, "", "", {})



RE_COOKIE_VAL = 'cookieVal=\W*"(.+)"'
def _extractGV(pageData):
    """

    var cookieVal= "xxxxxxxxxxx-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx";

    `pageData` -- HTML page with Javascript to set cookie value.
    """
    gv = None
    
    try:
        gv = re.search(RE_COOKIE_VAL, pageData).group(1)
    except AttributeError:
        print "Error: Couldn't extract GV cookie."
        raise SystemExit

    return gv



RE_SPLIT_PAGE_CONTENT = re.compile("D\((.*?)\);", re.DOTALL)
def _parsePage(pageContent):
    """
    Parse the supplied HTML page and extract useful information from
    the embedded Javascript.
    
    """
    # Note: We use the easiest thing that works here and no longer
    #       extract the Javascript code we want from the page first.
    items = (re.findall(RE_SPLIT_PAGE_CONTENT, pageContent)) 

    # TODO: Check we find something?
    
    itemsDict = {}

    namesFoundTwice = []

    for item in items:
        item = item.strip()[1:-1]
        name, value = (item.split(",", 1) + [""])[:2]

        name = name[1:-1] # Strip leading and trailing single or double quotes.
        
        try:
            # By happy coincidence Gmail's data is stored in a form
            # we can turn into Python data types by simply evaluating it.
            # TODO: Parse this better/safer?
            if value != "": # Empty strings aren't parsed successfully.
                parsedValue = eval(value.replace("\n",""))
            else:
                parsedValue = value
        except SyntaxError:
            logging.warning("Could not parse item `%s` as it was `%s`." %
                            (name, value))
        else:
            if itemsDict.has_key(name):
                # This handles the case where a name key is used more than
                # once (e.g. mail items, mail body) and automatically
                # places the values into list.
                # TODO: Check this actually works properly, it's early... :-)
                if (name in namesFoundTwice):
                    itemsDict[name].append(parsedValue)
                else:
                    itemsDict[name] = [itemsDict[name], parsedValue]
                    namesFoundTwice.append(name)
            else:
                itemsDict[name] = parsedValue

    if itemsDict[D_VERSION] != js_version:
        logging.warning("Live Javascript and constants file versions differ.")

    return itemsDict



OFFSET_MSG_ID = 0
OFFSET_MSG_SUBJECT = 6
class GmailMessage:
    """
    """
    
    def __init__(self, msgData):
        """
        """
        self.id = msgData[OFFSET_MSG_ID]
        self.subject = msgData[OFFSET_MSG_SUBJECT]

        # TODO: Populate additional fields & cache...(?)
        


class GmailAccount:
    """
    """

    def __init__(self, name, pw):
        """
        """
        self.name = name
        self._pw = pw

        self._cookieJar = ClientCookie.CookieJar()
        self._opener = ClientCookie.build_opener(NullCookieProcessor)

        self._cachedQuotaInfo = None



    def login(self):
        """
        """
        data = urllib.urlencode({'continue': URL_GMAIL,
                                 'service': 'mail',
                                 'Email': self.name,
                                 'Passwd': self._pw,
                                 'null': 'Sign+in'})
    
        headers = {'Host': 'www.google.com',
                   'User-Agent': 'User-Agent: Mozilla/5.0 (compatible;)'}

        req = ClientCookie.Request(URL_LOGIN, data=data, headers=headers)
        resp = ClientCookie.urlopen(req)
        self._cookieJar.extract_cookies(resp, req)
        
        pageData = resp.read()
        gv = _extractGV(pageData)

        self._cookieJar.set_cookie(
            _bakeQuickCookie(name="GV", value=gv, path="/",
                             domain=".gmail.google.com"))



    def _retrievePage(self, url):
        """
        """
        # TODO: Do extract cookies here too?
        req = ClientCookie.Request(url)
        self._cookieJar.add_cookie_header(req)
        resp = ClientCookie.urlopen(req)

        pageData = resp.read()

        return pageData



    def _parsePage(self, url):
        """
        Retrieve & then parse the requested page content.
        
        """
        items = _parsePage(self._retrievePage(url))
        
        # Automatically cache some things like quota usage.
        # TODO: Cache more?
        # TODO: Expire cached values?
        try:
            self._cachedQuotaInfo = items[D_QUOTA]
        except KeyError:
            pass
        
        return items



    def getFolder(self, folderName):
        """

        Folders contain conversation/message threads.

          `folderName` -- As set in GMail interface.

        Returns a `GmailFolder` instance.
        """
        URL_FOLDER_BASE = "https://gmail.google.com/gmail?search=%s&view=tl"

        items = self._parsePage(URL_FOLDER_BASE % folderName)

        return GmailFolder([GmailThread(thread)
                            for thread in items[D_THREAD]])

    

    def getQuotaInfo(self):
        """

        Return MB used, Total MB and percentage used.
        """
        # TODO: Change this to a property.
        if not self._cachedQuotaInfo:
            # TODO: Handle this better...
            self.getFolder(FOLDER_INBOX)

        return self._cachedQuotaInfo[:3]


    def getRawMessage(self, msgId):
        """
        """
        URL_BASE_RAW_MESSAGE = "https://gmail.google.com/gmail?view=om&th=%s"

        pageData = self._retrieveURL(URL_BASE_RAW_MESSAGE % msgId)

        return pageData


class GmailThread:
    """
    """

    def __init__(self, threadInfo):
        """
        """
        self.id = threadInfo[T_THREADID] # TODO: Check if this actually
                                               #       changes when new
                                               #       messages arrive.
        self.subject = threadInfo[T_SUBJECT_HTML]

        # TODO: Store other info?
        # TODO: Extract number of messages in thread/conversation.

        self._authors = threadInfo[T_AUTHORS_HTML]

        try:
            # TODO: Find out if this information can be found another way...
            self._length = int(re.search("\((\d+?)\)\Z",
                                         self._authors).group(1))
        except AttributeError:
            # If there's no message count then the thread only has one message.
            self._length = 1

    def __len__(self):
        """
        """
        return self._length
            


class GmailFolder:
    """
    """

    def __init__(self, threads):
        """

          `threads` -- A sequence of thread instances.
        """
        self._threads = threads


    def __iter__(self):
        """
        """
        return iter(self._threads)


FOLDER_NAMES = [FOLDER_INBOX, FOLDER_SENT] # TODO: Get these on the fly.
if __name__ == "__main__":
    name = raw_input("GMail account name: ")
    pw = raw_input("Password: ")

    ga = GmailAccount(name, pw)

    print "\nPlease wait, logging in..."

    ga.login()

    print "Log in successful.\n"

    print "%s of %s used. (%s)\n" % ga.getQuotaInfo()

    while 1:
        try:
            print "Select folder to list: (Ctrl-C to exit)"
            #print "(NOTE: This will display the content of *ALL* messages.)"
            for optionId, folderName in enumerate(FOLDER_NAMES):
                print "  %d. %s" % (optionId, folderName)

            folderName = FOLDER_NAMES[int(raw_input("Choice: "))]

            folder = ga.getFolder(folderName)

            print
            for thread in folder:
                #print "================================"
                print thread.id, thread.subject, len(thread)
                #print ga.getRawMessage(msg.id)
                #print "================================"

            print
        except KeyboardInterrupt:
            print "\n\nDone."
            break
