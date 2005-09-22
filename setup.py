#!/usr/bin/env python

# Setup script for the libgmail package
# Usage: 
# To create a source package; python setup.py sdist
# To install to your system; python setup.py install

from distutils.core import setup
mods = ['libgmail','lgconstants']
setup (name = "libgmail",
       version = "0.1.3.1",
       description = "python bindings to access Gmail",
       author = "wdaher@mit.edu, stas@linux.isbeter.nl,follower@myrealbox.com",
       author_email = "stas@linux.isbeter.nl",
       url = "http://libgmail.sourceforge.net/",
       license = "GPL",
       py_modules = mods,
      )

