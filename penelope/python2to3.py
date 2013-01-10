#!/usr/bin/env python
# -*- coding: utf-8 -*-

__license__     = 'GPLv3'
__author__      = 'Alberto Pettarin (pettarin gmail.com)'
__copyright__   = '2013 Alberto Pettarin (pettarin gmail.com)'
__version__     = 'v1.01'
__date__        = '2013-01-10'
__description__ = 'Convert code from Python 2 to Python 3, using code comments'

import re, sys, unicodedata
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
def main():
    fileIn = open(sys.argv[1], 'r')
    text = fileIn.read()
    fileIn.close()
    print convert(text)
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###


### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
def convert(text):

    text2 = re.sub(r"#Python2#\n", "#Python2#", text)
    text2 = re.sub(r"#Python3#", "#Python3#\n", text2)

    return text2
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###

### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
if __name__ == '__main__':

    reload(sys)
    sys.setdefaultencoding("utf-8")
    
    main()
### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ### ###
