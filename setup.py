#!/usr/bin/env python

# Setup script for the libgmail package

from distutils.core import setup
mods = ['libgmail','constants']
setup (name = "libgmail",
       version = "0.1.0",
       description = "python bindings to access Gmail",
       author = "follower@myrealbox.com, wdaher@mit.edu, stas@linux.isbeter.nl",
       author_email = "stas@linux.isbeter.nl",
       url = "http://libgmail.sourceforge.net/",
       license = "GPL",
       py_modules = mods,
      )
