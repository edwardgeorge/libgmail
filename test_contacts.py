#!/usr/bin/env python

import unittest
import getpass

from libgmail_new import *
from lgconstants import *
from lgcontacts import GContacts,GmailContact,GmailContactList


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
        contacts = GC.getContacts()
        for contact in contacts.getAllContacts():
            #print "Removing", contact
            GC.removeContact(contact)

    def tearDown(self):
        """
        Delete all entries in the
        addressbook so we start fresh
        """
        #print "Tearing down!"
        contacts = GC.getContacts()
        for contact in contacts.getAllContacts():
            #print "Removing", contact
            GC.removeContact(contact)


    def test1_BasicAddContact(self):
        """Create and retrieve an entry-level contact"""
        name = 'John Smith'
        email = 'john.smith@gmail.com'
        notes = 'I am average'
        GC.addContact(name, email, notes)
        myContacts = GC.getContacts()
        contact = myContacts.getContactByName(name)
        self.assertEqual(contact.getName(), name, "Returned name isn't the one we created initially")
        self.assertEqual(contact.getEmail(), email, "Returned email isn't the one we created initially")
        self.assertEqual(contact.getNotes(), notes, "Returned note isn't the one we created initially")

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
        GC.addContact('Waseem', 'wdaher@gmail.com', 'Is awesome')
        myContacts = GC.getContacts()
        waseem = myContacts.getContactByName('Waseem')
        self.assertEqual(waseem, myContacts.getContactByEmail('wdaher@gmail.com'))
        self.assertEqual(waseem, myContacts.getContactById(waseem.getId()))

    def test5_GetByLists(self):
        """Get a contact list by name, email, and id"""
        GC.addContact('Waseem', 'wdaher@gmail.com', 'Is awesome')
        GC.addContact('Daher', 'test@foo.bar')
        myContacts = GC.getContacts()
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
            GC.addContact(str(x), str(x))
        myContactList = GC.getContacts()
        self.assertEqual(myContactList.getCount(), count)

        # Now remove them all
        for x in range(count):
            self.assertEqual(True, GC.removeContact(myContactList.getContactByName(str(x))))
        myContactList = GC.getContacts()
        self.assertEqual(myContactList.getCount(), 0)


if __name__ == '__main__':
    
    print "\n=============================================="
    print "Start 'libgmail_new contacts' testsuite"
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
        GC = GContacts(account)
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(ContactsTests))
        unittest.TextTestRunner(verbosity=2).run(suite)


print "\nDone"


