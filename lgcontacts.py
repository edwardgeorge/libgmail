"""\n
########################################################################
libgmail contacts stuff

This is work in progress and might be a wrong appraoch.

Contact Stas through the libgmail mailinglist for more info.
#######################################################################\n
"""

print __doc__

import urllib,urllib2
from lgconstants import *

def _buildURL(**kwargs):
    """Helper function
    """
    return "%s?%s" % (URL_GMAIL, urllib.urlencode(kwargs))

class GContacts:
    """Initial attempt to move the contacts stuff into a module of it's own"""
    def __init__(self,ga):
        """@ga must be a GmailAccount object with the login method called."""
        self.ga = ga

    def getContacts(self):
        """
        Returns a GmailContactList object
        that has all the contacts in it as
        GmailContacts
        """
        contactList = []
        # pnl = a is necessary to get *all* contacts
        myUrl = _buildURL(view='cl',search='contacts', pnl='a')
        ## Reminder: Why are there two _parsePage functions, one in the
        ## ga class and one in the libgmail toplevel code.
        myData = self.ga._parsePage(myUrl)
        # This comes back with a dictionary
        # with entry 'cl'
        addresses = myData['cl']
        for entry in addresses:
            if len(entry) >= 6 and entry[0]=='ce':
                newGmailContact = GmailContact(entry[1], entry[2], entry[4], entry[5])
                #### new code used to get all the notes 
                #### not used yet due to lockdown problems
                ##rawnotes = self._getSpecInfo(entry[1])
                ##print rawnotes
                ##newGmailContact = GmailContact(entry[1], entry[2], entry[4],rawnotes)
                contactList.append(newGmailContact)

        return GmailContactList(contactList)

    def addContact(self, myContact, *extra_args):
        """
        Attempts to add a GmailContact to the gmail
        address book. Returns true if successful,
        false otherwise

        Please note that after version 0.1.3.3,
        addContact takes one argument of type
        GmailContact, the contact to add.

        The old signature of:
        addContact(name, email, notes='') is still
        supported, but deprecated. 
        """
        if len(extra_args) > 0:
            # The user has passed in extra arguments
            # He/she is probably trying to invoke addContact
            # using the old, deprecated signature of:
            # addContact(self, name, email, notes='')        
            # Build a GmailContact object and use that instead
            (name, email) = (myContact, extra_args[0])
            if len(extra_args) > 1:
                notes = extra_args[1]
            else:
                notes = ''
            myContact = GmailContact(-1, name, email, notes)

        # TODO: In the ideal world, we'd extract these specific
        # constants into a nice constants file
        
        # This mostly comes from the Johnvey Gmail API,
        # but also from the gmail.py cited earlier
        myURL = _buildURL(view='up')        

        myDataList =  [ ('act','ec'),
                        ('at', self.ga._cookieJar._cookies['GMAIL_AT']), # Cookie data?
                        ('ct_nm', myContact.getName()),
                        ('ct_em', myContact.getEmail()),
                        ('ct_id', -1 )
                       ]

        notes = myContact.getNotes()
        if notes != '':
            myDataList.append( ('ctf_n', notes) )

        validinfokeys = [
                        'i', # IM
                        'p', # Phone
                        'd', # Company
                        'a', # ADR
                        'e', # Email
                        'm', # Mobile
                        'b', # Pager
                        'f', # Fax
                        't', # Title
                        'o', # Other
                        ]

        moreInfo = myContact.getMoreInfo()
        ctsn_num = -1
        if moreInfo != {}:
            for ctsf,ctsf_data in moreInfo.items():
                ctsn_num += 1
                # data section header, WORK, HOME,...
                sectionenum ='ctsn_%02d' % ctsn_num
                myDataList.append( ( sectionenum, ctsf ))
                ctsf_num = -1

                if isinstance(ctsf_data[0],str):
                    ctsf_num += 1
                    # data section
                    subsectionenum = 'ctsf_%02d_%02d_%s' % (ctsn_num, ctsf_num, ctsf_data[0])  # ie. ctsf_00_01_p
                    myDataList.append( (subsectionenum, ctsf_data[1]) )
                else:
                    for info in ctsf_data:
                        if validinfokeys.count(info[0]) > 0:
                            ctsf_num += 1
                            # data section
                            subsectionenum = 'ctsf_%02d_%02d_%s' % (ctsn_num, ctsf_num, info[0])  # ie. ctsf_00_01_p
                            myDataList.append( (subsectionenum, info[1]) )

        myData = urllib.urlencode(myDataList)
        request = urllib2.Request(myURL,
                                  data = myData)
        pageData = self.ga._retrievePage(request)

        if pageData.find("The contact was successfully added") == -1:
            print pageData
            if pageData.find("already has the email address") > 0:
                raise Exception("Someone with same email already exists in Gmail.")
            elif pageData.find("https://www.google.com/accounts/ServiceLogin"):
                raise Exception("Login has expired.")
            return False
        else:
            return True

    def _removeContactById(self, id):
        """
        Attempts to remove the contact that occupies
        id "id" from the gmail address book.
        Returns True if successful,
        False otherwise.

        This is a little dangerous since you don't really
        know who you're deleting. Really,
        this should return the name or something of the
        person we just killed.

        Don't call this method.
        You should be using removeContact instead.
        """
        myURL = _buildURL(search='contacts', ct_id = id, c=id, act='dc', at=self.ga._cookieJar._cookies['GMAIL_AT'], view='up')
        pageData = self.ga._retrievePage(myURL)

        if pageData.find("The contact has been deleted") == -1:
            return False
        else:
            return True

    def removeContact(self, gmailContact):
        """
        Attempts to remove the GmailContact passed in
        Returns True if successful, False otherwise.
        """
        # Let's re-fetch the contact list to make
        # sure we're really deleting the guy
        # we think we're deleting
        newContactList = self.getContacts()
        newVersionOfPersonToDelete = newContactList.getContactById(gmailContact.getId())
        # Ok, now we need to ensure that gmailContact
        # is the same as newVersionOfPersonToDelete
        # and then we can go ahead and delete him/her
        if (gmailContact == newVersionOfPersonToDelete):
            return self._removeContactById(gmailContact.getId())
        else:
            # We have a cache coherency problem -- someone
            # else now occupies this ID slot.
            # TODO: Perhaps signal this in some nice way
            #       to the end user?
            
            print "Unable to delete."
            print "Has someone else been modifying the contacts list while we have?"
            print "Old version of person:",gmailContact
            print "New version of person:",newVersionOfPersonToDelete
            return False

## Don't remove this. contact stas
##    def _getSpecInfo(self,id):
##        """
##        Return all the notes data.
##        This is currently not used due to the fact that it requests pages in 
##        a dos attack manner.
##        """
##        myURL =_buildURL(search='contacts',ct_id=id,c=id,\
##                        at=self._cookieJar._cookies['GMAIL_AT'],view='ct')
##        pageData = self._retrievePage(myURL)
##        myData = self._parsePage(myURL)
##        #print "\nmyData form _getSpecInfo\n",myData
##        rawnotes = myData['cov'][7]
##        return rawnotes

class GmailContact:
    """
    Class for storing a Gmail Contacts list entry
    """
    def __init__(self, name, email, *extra_args):
        """
        Returns a new GmailContact object
        (you can then call addContact on this to commit
         it to the Gmail addressbook, for example)

        Consider calling setNotes() and setMoreInfo()
        to add extended information to this contact
        """
        # Support populating other fields if we're trying
        # to invoke this the old way, with the old constructor
        # whose signature was __init__(self, id, name, email, notes='')
        id = -1
        notes = ''
   
        if len(extra_args) > 0:
            (id, name) = (name, email)
            email = extra_args[0]
            if len(extra_args) > 1:
                notes = extra_args[1]
            else:
                notes = ''

        self.id = id
        self.name = name
        self.email = email
        self.notes = notes
        self.moreInfo = {}
    def __str__(self):
        return "%s %s %s %s" % (self.id, self.name, self.email, self.notes)
    def __eq__(self, other):
        if not isinstance(other, GmailContact):
            return False
        return (self.getId() == other.getId()) and \
               (self.getName() == other.getName()) and \
               (self.getEmail() == other.getEmail()) and \
               (self.getNotes() == other.getNotes())
    def getId(self):
        return self.id
    def getName(self):
        return self.name
    def getEmail(self):
        return self.email
    def getNotes(self):
        return self.notes
    def setNotes(self, notes):
        """
        Sets the notes field for this GmailContact
        Note that this does NOT change the note
        field on Gmail's end; only adding or removing
        contacts modifies them
        """
        self.notes = notes

    def getMoreInfo(self):
        return self.moreInfo
    def setMoreInfo(self, moreInfo):
        """
        moreInfo format
        ---------------
        Use special key values::
                        'i' =  IM
                        'p' =  Phone
                        'd' =  Company
                        'a' =  ADR
                        'e' =  Email
                        'm' =  Mobile
                        'b' =  Pager
                        'f' =  Fax
                        't' =  Title
                        'o' =  Other

        Simple example::

        moreInfo = {'Home': ( ('a','852 W Barry'),
                              ('p', '1-773-244-1980'),
                              ('i', 'aim:brianray34') ) }

        Complex example::

        moreInfo = {
            'Personal': (('e', 'Home Email'),
                         ('f', 'Home Fax')),
            'Work': (('d', 'Sample Company'),
                     ('t', 'Job Title'),
                     ('o', 'Department: Department1'),
                     ('o', 'Department: Department2'),
                     ('p', 'Work Phone'),
                     ('m', 'Mobile Phone'),
                     ('f', 'Work Fax'),
                     ('b', 'Pager')) }
        """
        self.moreInfo = moreInfo 
    def getVCard(self):
        """Returns a vCard 3.0 for this
        contact, as a string"""
        # The \r is is to comply with the RFC2425 section 5.8.1
        vcard = "BEGIN:VCARD\r\n"
        vcard += "VERSION:3.0\r\n"
        ## Deal with multiline notes
        ##vcard += "NOTE:%s\n" % self.getNotes().replace("\n","\\n")
        vcard += "NOTE:%s\r\n" % self.getNotes()
        # Fake-out N by splitting up whatever we get out of getName
        # This might not always do 'the right thing'
        # but it's a *reasonable* compromise
        fullname = self.getName().split()
        fullname.reverse()
        vcard += "N:%s" % ';'.join(fullname) + "\r\n"
        vcard += "FN:%s\r\n" % self.getName()
        vcard += "EMAIL;TYPE=INTERNET:%s\r\n" % self.getEmail()
        vcard += "END:VCARD\r\n\r\n"
        # Final newline in case we want to put more than one in a file
        return vcard

class GmailContactList:
    """
    Class for storing an entire Gmail contacts list
    and retrieving contacts by Id, Email address, and name
    """
    def __init__(self, contactList):
        self.contactList = contactList
    def __str__(self):
        return '\n'.join([str(item) for item in self.contactList])
    def getCount(self):
        """
        Returns number of contacts
        """
        return len(self.contactList)
    def getAllContacts(self):
        """
        Returns an array of all the
        GmailContacts
        """
        return self.contactList
    def getContactByName(self, name):
        """
        Gets the first contact in the
        address book whose name is 'name'.

        Returns False if no contact
        could be found
        """
        nameList = self.getContactListByName(name)
        if len(nameList) > 0:
            return nameList[0]
        else:
            return False
    def getContactByEmail(self, email):
        """
        Gets the first contact in the
        address book whose name is 'email'.
        As of this writing, Gmail insists
        upon a unique email; i.e. two contacts
        cannot share an email address.

        Returns False if no contact
        could be found
        """
        emailList = self.getContactListByEmail(email)
        if len(emailList) > 0:
            return emailList[0]
        else:
            return False
    def getContactById(self, myId):
        """
        Gets the first contact in the
        address book whose id is 'myId'.

        REMEMBER: ID IS A STRING

        Returns False if no contact
        could be found
        """
        idList = self.getContactListById(myId)
        if len(idList) > 0:
            return idList[0]
        else:
            return False
    def getContactListByName(self, name):
        """
        This function returns a LIST
        of GmailContacts whose name is
        'name'. 

        Returns an empty list if no contacts
        were found
        """
        nameList = []
        for entry in self.contactList:
            if entry.getName() == name:
                nameList.append(entry)
        return nameList
    def getContactListByEmail(self, email):
        """
        This function returns a LIST
        of GmailContacts whose email is
        'email'. As of this writing, two contacts
        cannot share an email address, so this
        should only return just one item.
        But it doesn't hurt to be prepared?

        Returns an empty list if no contacts
        were found
        """
        emailList = []
        for entry in self.contactList:
            if entry.getEmail() == email:
                emailList.append(entry)
        return emailList
    def getContactListById(self, myId):
        """
        This function returns a LIST
        of GmailContacts whose id is
        'myId'. We expect there only to
        be one, but just in case!

        Remember: ID IS A STRING

        Returns an empty list if no contacts
        were found
        """
        idList = []
        for entry in self.contactList:
            if entry.getId() == myId:
                idList.append(entry)
        return idList
        
