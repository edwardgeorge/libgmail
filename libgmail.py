#!/usr/bin/python2.3
#
# libgmail -- Gmail access via Python
#
# Version: 0.0.1 (2 July 2004)
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
import ClientCookie
import urllib
import re

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


RE_MAIL_DATA = "<!--(.*)-->"
def _extractMailData(pageData):
    """
    """
    try:
        mailData = re.search(RE_MAIL_DATA, pageData, re.DOTALL).group(1)
    except AttributeError:
        print "Error: Couldn't get mail data."
        raise SystemExit
        
    return mailData


RE_SPLIT_MAIL_DATA = re.compile("D\((.*?)\);", re.DOTALL)
def _parseMailData(mailData):
    """
    """
    items = (re.findall(RE_SPLIT_MAIL_DATA, mailData))

    itemsDict = {}

    for item in items:
        item = item.strip()[1:-1]
        name, value = (item.split(",", 1) + [""])[:2]
        itemsDict[name.strip('"')] = value

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
        

def _parseMsgData(msgsInfo):
    """
    """
    # TODO: Parse this better/safer...
    msgsData = eval(msgsInfo.replace("\n",""))

    msgs = [GmailMessage(msg)
            for msg in msgsData]

    return msgs


class GMailAccount:
    """
    """

    def __init__(self, name, pw):
        """
        """
        self.name = name
        self._pw = pw

        self._cookieJar = ClientCookie.CookieJar()
        self._opener = ClientCookie.build_opener(NullCookieProcessor)

        self._items = None



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


    def _retrieveURL(self, url):
        """
        """
        # TODO: Do extract cookies here too?
        req = ClientCookie.Request(url)
        self._cookieJar.add_cookie_header(req)
        resp = ClientCookie.urlopen(req)

        pageData = resp.read()

        return pageData
        

    def getFolderContent(self, folderName):
        """

        `folderName` -- As set in GMail interface.
        """
        URL_FOLDER_BASE = "https://gmail.google.com/gmail?search=%s&view=tl"

        pageData = self._retrieveURL(URL_FOLDER_BASE % folderName)

        mailData = _extractMailData(pageData)

        self._items = _parseMailData(mailData)

        msgsInfo = self._items["t"]

        return _parseMsgData(msgsInfo)
    

    def getQuotaInfo(self):
        """

        Return MB used, Total MB and percentage used.
        """
        if not self._items:
            # TODO: Handle this better.
            # This retrieves the value if we haven't cached it yet.
            self.getFolderContent(FOLDER_INBOX)

        quotaInfo = [value.strip('"')
                     for value in self._items["qu"].split(",")]

        return tuple(quotaInfo[:3])


    def getRawMessage(self, msgId):
        """
        """
        URL_BASE_RAW_MESSAGE = "https://gmail.google.com/gmail?view=om&th=%s"

        pageData = self._retrieveURL(URL_BASE_RAW_MESSAGE % msgId)

        return pageData

        

FOLDER_NAMES = [FOLDER_INBOX, FOLDER_SENT] # TODO: Get these on the fly.
if __name__ == "__main__":
    name = raw_input("GMail account name: ")
    pw = raw_input("Password: ")

    ga = GMailAccount(name, pw)

    print "\nPlease wait, logging in..."

    ga.login()

    print "Log in successful.\n"

    print "%s of %s used. (%s)\n" % ga.getQuotaInfo()

    while 1:
        try:
            print "Select folder to list: (Ctrl-C to exit)"
            print "(NOTE: This will display the content of *ALL* messages.)"
            for optionId, folderName in enumerate(FOLDER_NAMES):
                print "  %d. %s" % (optionId, folderName)

            folderName = FOLDER_NAMES[int(raw_input("Choice: "))]

            msgs = ga.getFolderContent(folderName)

            print
            for msg in msgs:
                print "================================"
                #print msg.id, msg.subject
                print ga.getRawMessage(msg.id)
                print "================================"

            print
        except KeyboardInterrupt:
            print "\n\nDone."
            break
