#!/usr/bin/python2.3
#
# libgmail -- Gmail access via Python
#
# Version: 0.0.3 (08 July 2004)
#
# Author: follower@myrealbox.com
#
# License: GPL 2.0
#
# Thanks:
#   * Live HTTP Headers <http://livehttpheaders.mozdev.org/>
#   * Gmail <http://gmail.google.com/>
#   * Google Blogoscoped <http://blog.outer-court.com/>
#   * ClientCookie <http://wwwsearch.sourceforge.net/ClientCookie/>
#     (There when I needed it...)
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

import re
import urllib
import urllib2
import logging

URL_LOGIN = "https://www.google.com/accounts/ServiceLoginBoxAuth"
URL_GMAIL = "https://gmail.google.com/gmail"

FOLDER_INBOX = "inbox"
FOLDER_SENT = "sent"


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



class CookieJar:
    """
    A rough cookie handler, intended to only refer to one domain.

    Does no expiry or anything like that.

    (The only reason this is here is so I don't have to require
    the `ClientCookie` package.)
    
    """

    def __init__(self):
        """
        """
        self._cookies = []


    def extractCookies(self, response, nameFilter = None):
        """
        """
        # TODO: Do this all more nicely?
        for cookie in response.headers.getheaders('Set-Cookie'):
            cookieName = cookie.split("=")[0]
            if not nameFilter or cookieName in nameFilter:
                self._cookies.append(cookie.split(";")[0])


    def addCookie(self, name, value):
        """
        """
        self._cookies.append("%s=%s" % (name, value))


    def setCookies(self, request):
        """
        """
        request.add_header('Cookie', ";".join(self._cookies))
    


class GmailAccount:
    """
    """

    def __init__(self, name, pw):
        """
        """
        self.name = name
        self._pw = pw

        self._cachedQuotaInfo = None

        self._cookieJar = CookieJar()


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

        req = urllib2.Request(URL_LOGIN, data=data, headers=headers)
        resp = urllib2.urlopen(req)

        self._cookieJar.extractCookies(resp, ["SID"])
        
        pageData = resp.read()
        gv = _extractGV(pageData)

        self._cookieJar.addCookie("GV", gv)


    def _retrievePage(self, url):
        """
        """
        # TODO: Do extract cookies here too?
        req = urllib2.Request(url)
        self._cookieJar.setCookies(req)
        resp = urllib2.urlopen(req)

        pageData = resp.read()

        # TODO: Enable logging of page data for debugging purposes?

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

          `folderName` -- As set in Gmail interface.

        Returns a `GmailFolder` instance.
        """
        URL_FOLDER_BASE = "https://gmail.google.com/gmail?search=%s&view=tl"

        items = self._parsePage(URL_FOLDER_BASE % folderName)

        # TODO: Option to get *all* threads if multiple pages are used.

        return GmailFolder(self, folderName, items[D_THREAD])

    
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

        pageData = self._retrievePage(URL_BASE_RAW_MESSAGE % msgId)

        return pageData


    def getUnreadMsgCount(self):
        """
        """
        URL_QUERY_UNREAD = "https://gmail.google.com/gmail?search=query&q=is%3Aunread&view=tl"

        items = self._parsePage(URL_QUERY_UNREAD)

        return items[D_THREADLIST_SUMMARY][TS_TOTAL_MSGS]


class GmailFolder:
    """
    """

    def __init__(self, account, folderName, threadsInfo):
        """

          `threadsInfo` -- As returned from Gmail.
        """
        self._account = account
        self.folderName = folderName

        # TODO: Handle all this properly...
        # This happens when more than one "t" datapack is on a page.
        if type(threadsInfo) != type(tuple):
            # Option 1 - only one thread
            # Option 2 - multiple threads split
            validThreadsInfo = ()
            for item in threadsInfo:
                if type(item) is tuple:
                    validThreadsInfo += item
                else:
                    validThreadsInfo += tuple([item])
            threadsInfo = validThreadsInfo

        self._threads = [GmailThread(self, thread)
                         for thread in threadsInfo]


    def __iter__(self):
        """
        """
        return iter(self._threads)


    def getMessages(self, thread):
        """
        """
        # NOTE: To my mind this method should probably be part of
        #       `GmailThread`, but for some reason the folder name/search
        #       needs to be supplied to retrieve the conversation view,
        #       so it's going here for the moment.

        # TODO: Change how url is constructed & retrieved...
        URL_CONVERSATION_BASE = \
                       "https://gmail.google.com/gmail?search=%s&view=cv&th=%s"

        items = self._account._parsePage(URL_CONVERSATION_BASE %
                                         (self.folderName, thread.id))

        # TODO: Handle this better?

        msgsInfo = items[D_MSGINFO]

        # TODO: Handle special case of only one message in thread better?
        if type(msgsInfo) != type([]):
            msgsInfo = [msgsInfo]

        return [GmailMessage(thread, msg)
                for msg in msgsInfo]


class GmailThread:
    """



    Note: As far as I can tell, the "canonical" thread id is always the same
          as the id of the last message in the thread. But it appears that
          the id of any message in the thread can be used to retrieve
          the thread information.
    
    """

    def __init__(self, parent, threadInfo):
        """
        """
        self._parent = parent
        
        self.id = threadInfo[T_THREADID] # TODO: Change when canonical updated?
        self.subject = threadInfo[T_SUBJECT_HTML]

        # TODO: Store other info?
        # Extract number of messages in thread/conversation.

        self._authors = threadInfo[T_AUTHORS_HTML]

        try:
            # TODO: Find out if this information can be found another way...
            #       (Without another page request.)
            self._length = int(re.search("\((\d+?)\)\Z",
                                         self._authors).group(1))
        except AttributeError:
            # If there's no message count then the thread only has one message.
            self._length = 1

        # TODO: Store information known about the last message  (e.g. id)?
        self._messages = []
        

    def __len__(self):
        """
        """
        return self._length


    def __iter__(self):
        """
        """
        if not self._messages:
            self._messages = self._parent.getMessages(self)
            
        return iter(self._messages)


        
class GmailMessage(object):
    """
    """
    
    def __init__(self, thread, msgData):
        """
        """
        self._thread = thread
        
        self.id = msgData[MI_MSGID]
        self.number = msgData[MI_NUM]
        self.subject = msgData[MI_SUBJECT]

        # TODO: Populate additional fields & cache...(?)

        self._body = None


    def _getBody(self):
        """
        """
        if not self._body:
            # TODO: Ummm, do this a *little* more nicely...
            self._body = self._thread._parent._account.getRawMessage(self.id)

        return self._body

    body = property(_getBody, doc = "")
        



FOLDER_NAMES = ['all', FOLDER_INBOX, FOLDER_SENT] # TODO: Get these on the fly.
if __name__ == "__main__":
    import sys
    from getpass import getpass

    try:
        name = sys.argv[1]
    except IndexError:
        name = raw_input("Gmail account name: ")
        
    pw = getpass("Password: ")

    ga = GmailAccount(name, pw)

    print "\nPlease wait, logging in..."

    ga.login()

    print "Log in successful.\n"

    # TODO: Use properties instead?
    quotaInfo = ga.getQuotaInfo()
    quotaMbUsed = quotaInfo[QU_SPACEUSED]
    quotaMbTotal = quotaInfo[QU_QUOTA]
    quotaPercent = quotaInfo[QU_PERCENT]
    print "%s of %s used. (%s)\n" % (quotaMbUsed, quotaMbTotal, quotaPercent)

    while 1:
        try:
            print "Select folder to list: (Ctrl-C to exit)"
            for optionId, folderName in enumerate(FOLDER_NAMES):
                print "  %d. %s" % (optionId, folderName)

            folderName = FOLDER_NAMES[int(raw_input("Choice: "))]

            folder = ga.getFolder(folderName)

            print
            for thread in folder:
                print
                print thread.id, len(thread), thread.subject
                for msg in thread:
                    print "  ", msg.id, msg.number, msg.subject
                    #print msg.body

            print
        except KeyboardInterrupt:
            print "\n\nDone."
            break
