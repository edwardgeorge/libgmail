#!/usr/bin/python2.3
#
# mkconstants.py -- Extract constants from Gmail Javascript code
#
# $Revision$ ($Date$)
#
# Author: follower@myrealbox.com
#
# License: GPL 2.0
#
# This tool parses the Javascript file used by Gmail, extracts
# useful constants and then generates an importable Python module.
#

import re
import sys
import time

OUTPUT_FILENAME = "constants.py"

# Used to filter out only the constants we want to use at the moment.
USEFUL_PREFIXES = ["D", "QU", "TS", "T", "CS", "MI"]
RE_CONSTANTS = "var ([A-Z]{1,2}_[A-Z_]+?)=(.+?);"

VAR_JS_VERSION = "js_version"

FMT_DEFINITION = "%s = %s\n"

FILE_HEADER = """\
#
# Generated file -- DO NOT EDIT
#
# %s -- Useful constants extracted from Gmail Javascript code
#
# Source version: %s
#
# Generated: %s
#

""" % (OUTPUT_FILENAME, "%s",
       time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime()))

if __name__ == "__main__":
    lines = []

    try:
        inputFilename = sys.argv[1]
    except IndexError:
        print "Usage: mkconstants.py <gmail.js>"
        raise SystemExit

    print "Reading `%s`..." % inputFilename
    code = open(inputFilename).read()

    jsVersion = re.search("var %s=(.+?);" % VAR_JS_VERSION, code).group(1)

    lines.extend([FMT_DEFINITION % (VAR_JS_VERSION, jsVersion), "\n"])

    matches = re.findall(RE_CONSTANTS, code)

    for name, value in matches:
        prefix = name[:name.index("_")]

        if prefix in USEFUL_PREFIXES:
            lines.append(FMT_DEFINITION % (name, value))

    lines.insert(0, FILE_HEADER % jsVersion.strip("'"))

    print "Writing `%s`..." % OUTPUT_FILENAME
    open(OUTPUT_FILENAME, "w").writelines(lines)

    print "Done."
    