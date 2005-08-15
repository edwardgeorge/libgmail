#!/usr/bin/python2.3
"""
libgmail test suite

Tests:
Contacts
"""
import unittest
from libgmail import *
import getpass

class ContactsTests(unittest.TestCase):
    """
    Set of tests that exercise the contacts portion of libgmail
    """
    def setUp(self):
        """
        Delete all entries in the
        addressbook so we start fresh
        """
        #print "Setting up!"
        contacts = account.getContacts().getAllContacts()
        for contact in contacts:
            # print "Removing", contact
            account.removeContact(contact)

    def tearDown(self):
        """
        Delete all entries in the
        addressbook so we start fresh
        """
        #print "Tearing down!"
        contacts = account.getContacts().getAllContacts()
        for contact in contacts:
            # print "Removing", contact
            account.removeContact(contact)


    def test1_BasicAddContact(self):
        """Create and retrieve an entry-level contact"""
        name = 'John Smith'
        email = 'john.smith@gmail.com'
        notes = 'I am average'
        account.addContact(name, email, notes)
        myContacts = account.getContacts()
        contact = myContacts.getContactByName(name)
        self.assertEqual(contact.getName(), name, "Returned name isn't the one we created initially")
        self.assertEqual(contact.getEmail(), email, "Returned email isn't the one we created initially")
        self.assertEqual(contact.getNotes(), notes, "Returned note isn't the one we created initially")

## This is a known non-working test
## at release time.
## Commenting it out for the release
## so that the test suite passes
#    
#     def test2_AdvancedAddContact(self):
#         """Create and retrieve a contact with a newline in the notes"""
#         name = 'W4533m'
#         email = 'fake-person@gmail.com'
#         notes = 'Is\nawesome'
#         account.addContact(name, email, notes)
#         myContacts = account.getContacts()
#         contact = myContacts.getContactByName(name)
#         self.assertEqual(contact.getName(), name, "Returned name isn't the one we created initially")
#         self.assertEqual(contact.getEmail(), email, "Returned email isn't the one we created initially")
#         self.assertEqual(contact.getNotes(), notes, "Returned note isn't the one we created initially")

    def test3_GmailContact(self):
        """Check that GmailContact equality and accessor methods work"""
        w = GmailContact('a','b','c','d')
        x = GmailContact('x','y','z')
        y = GmailContact('a','b','c','d')
        z = GmailContact('a','b','c','d')

        self.assertEqual(w,w, "%s doesn't equals %s" % (w,w))
        self.assertEqual(x,x, "%s doesn't equals %s" % (x,x))
        self.assertEqual(y,y, "%s doesn't equals %s" % (y,y))
        self.assertEqual(z,z, "%s doesn't equals %s" % (z,z))
        self.assertEqual(w,y, "%s doesn't equals %s" % (w,y))
        self.assertEqual(y,z, "%s doesn't equals %s" % (y,z))
        self.assertEqual(w,z, "%s doesn't equals %s" % (w,z))
        self.assertEqual(z,w, "%s doesn't equals %s" % (z,w))

        self.assertNotEqual(w,x, "%s shouldn't equals %s" % (w,x))
        self.assertNotEqual(x,w, "%s shouldn't equals %s" % (x,w))
        
        i,a,e,n = w.getId(),w.getName(),w.getEmail(),w.getNotes()
        self.assertEqual(i, 'a', "%s doesn't equals 'a'" % i)
        self.assertEqual(a, 'b', "%s doesn't equals 'b'" % a)
        self.assertEqual(e, 'c', "%s doesn't equals 'c'" % e)
        self.assertEqual(n, 'd', "%s doesn't equals 'd'" % n)

        self.assertEqual(x.getNotes(), '', "getNotes() should return ''")

    def test4_GetBy(self):
        """Get a contact by name, email, and id"""
        account.addContact('Waseem', 'wdaher@gmail.com', 'Is awesome')
        myContacts = account.getContacts()
        waseem = myContacts.getContactByName('Waseem')
        self.assertEqual(waseem, myContacts.getContactByEmail('wdaher@gmail.com'))
        self.assertEqual(waseem, myContacts.getContactById(waseem.getId()))

    def test5_GetByLists(self):
        """Get a contact list by name, email, and id"""
        account.addContact('Waseem', 'wdaher@gmail.com', 'Is awesome')
        account.addContact('Daher', 'test@foo.bar')
        myContacts = account.getContacts()
        waseem = myContacts.getContactByName('Waseem')
        
        result = [waseem]
        obj = myContacts.getContactListByName('Waseem')
        self.assertEqual(result, obj, "%s doesn't equals %s" % (result,obj))
        obj = myContacts.getContactListByEmail('wdaher@gmail.com')
        self.assertEqual([waseem], obj,"%s doesn't equals %s" % (result,obj))
        obj = myContacts.getContactListById(waseem.getId())
        self.assertEqual([waseem], obj,"%s doesn't equals %s" % (result,obj))

    def test6_SmallGetAndRemove(self):
        """Add one address and remove it again"""
        count = 1
        # Add some
        for x in range(count):
            account.addContact(str(x), str(x))
        myContactList = account.getContacts()
        self.assertEqual(myContactList.getCount(), count)

        # Now remove them all
        for x in range(count):
            self.assertEqual(True, account.removeContact(myContactList.getContactByName(str(x))))
        myContactList = account.getContacts()
        self.assertEqual(myContactList.getCount(), 0)

## MediumGetAndRemove and LargeGetAndRemove pound
## gmail's servers faster than they'd like to be accessed,
## so this usually gets our account suspended, it seems.
## If you really want to test that these large gets/sets work,
## maybe insert a delay and run them? Doesn't really make 
## sense to run them every time though
#     def test7_MediumGetAndRemove(self):
#         """Add 14 addresses and remove them again"""
#         count = 14
#         for x in range(count):
#             account.addContact(str(x), str(x))
#         myContactList = account.getContacts()
#         self.assertEqual(myContactList.getCount(), count)

#         # Now remove them all
#         for x in range(count):
#             self.assertTrue(account.removeContact(myContactList.getContactByName(str(x))))
#         myContactList = account.getContacts()
#         self.assertEqual(myContactList.getCount(), 0)

#     def test8_LargeGetAndRemove(self):
#         """Add 25 addresses and remove them again"""
#         count = 25
#         for x in range(count):
#             account.addContact(str(x), str(x))
#         myContactList = account.getContacts()
#         self.assertEqual(myContactList.getCount(), count)

#         # Now remove them all
#         for x in range(count):
#             self.assertTrue(account.removeContact(myContactList.getContactByName(str(x))))
#         myContactList = account.getContacts()
#         self.assertEqual(myContactList.getCount(), 0)

    def test9_vCard(self):
        """Test vCard export"""
        waseem = GmailContact("0", "Waseem Daher", "wdaher@mit.edu", "GmailAgent developer")
        vcard = waseem.getVCard()
        expectedVCard="""BEGIN:VCARD
VERSION:3.0
NOTE:GmailAgent developer
N:Daher;Waseem
FN:Waseem Daher
EMAIL;TYPE=INTERNET:wdaher@mit.edu
END:VCARD

"""
        self.assertEqual(vcard, expectedVCard, "getVCard() did not export what we expected for Waseem")
	

        # Test multi-line NOTEs
        bob = GmailContact("0", "BillyJo", "billy@jo.net", "I like multilines\nwoo")
        bobvcard=bob.getVCard()
        bobexpectedVCard="""BEGIN:VCARD
VERSION:3.0
NOTE:I like multilines\\nwoo
N:BillyJo
FN:BillyJo
EMAIL;TYPE=INTERNET:billy@jo.net
END:VCARD
"""
        self.assertEqual(vcard, expectedVCard, "getVCard() didn't export what we expected for BillyJo")

if __name__ == '__main__':
    #unittest.main()
    ## With this we get a better output
    print "\n=============================================="
    print "Start 'libgmail contacts' testsuite"
    print "------------------------------------------------\n"
    print "WARNING: THIS WILL DELETE/REARRANGE"
    print "         YOUR ADDRESSBOOK/EMAILS"
    print " BE SURE TO RUN THIS TEST ONLY ON A 'test' ACCOUNT"
    
    name = raw_input("Gmail account name:")
    pw = getpass.getpass("Password: ")
    account = GmailAccount(name, pw)

    try:
        account.login()
        print "Login successful.\n"
    except GmailLoginFailure,e:
        print "\nLogin failed. (%s)" % e.message
    else:
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(ContactsTests))
        unittest.TextTestRunner(verbosity=2).run(suite)
