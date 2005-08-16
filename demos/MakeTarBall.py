#!/usr/bin/env python

# make tarball!
VERSION = '0.1'
PACKAGENAME = 'libgmail-docs_'
import os

print "\nCreate API docs"
os.system('epydoc -o API ../libgmail.py')

def cleanup(*args):
    """Used by os.path.walk to traverse the tree and remove CVS dirs"""
    if os.path.split(args[1])[1] == "CVS":
        print "Remove ",args[1]
        os.system('rm -r %s' % args[1])
    
filelist = open('filelist', 'r')
folderlist = open('folderlist', 'r')
myFiles = filelist.readlines()
myFolders = folderlist.readlines()
os.system('mkdir %s%s' % (PACKAGENAME,VERSION))
for file in myFiles:
    os.system('cp %s %s%s' % (file[:-1], PACKAGENAME,VERSION))

for folder in myFolders:
    os.system('mkdir %s%s/%s' % (PACKAGENAME,VERSION, folder[:-1]))
    os.system('cp -r %s %s%s' % (folder[:-1],PACKAGENAME, VERSION))

# removing the CVS stuff
os.path.walk('%s%s' % (PACKAGENAME,VERSION),cleanup,None)

print "\nCreate a GNU/Linux tarball..."
try:
    execString = 'tar -czf %s%s.tgz %s%s/' % (PACKAGENAME,VERSION,PACKAGENAME, VERSION)
    print execString
    os.system(execString)
except Exception,info:
    print info,"\nYou must have the tar package installed"
else:
    print "Done.\n"
    
print "Create a Windows compatible zipfile..."
try:
    execString = 'zip -rq %s%s.zip ./%s%s' % (PACKAGENAME,VERSION,PACKAGENAME, VERSION)
    print execString
    os.system(execString)
except Exception,info:
    print info,"\nYou must have the zip package installed."
else:
    print "Done\n"
os.system('rm -rf %s%s' % (PACKAGENAME,VERSION))
