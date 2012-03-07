#!/usr/bin/env python

__license__     = 'GPLv3'
__author__      = 'Alberto Pettarin (pettarin gmail.com)'
__copyright__   = '2012 Alberto Pettarin (pettarin gmail.com)'
__version__     = 'v1.04'
__date__        = '2012-03-07'
__description__ = 'Parse the given definition list for penelope.py'


### BEGIN parse ###
# parse(data, type_sequence, ignore_case)
# parse the given list of pairs
# data = [ [word, definition] ]
# with type_sequence and ignore_case options,
# and outputs the following list:
# parsed = [ word, include, synonyms, substitutions, definition ]
#
# where:
#        word is the sorting key
#        include is a boolean saying whether the word should be included
#        synonyms is a list of alternative strings for word
#        substitutions is a list of pairs [ word_to_replace, replacement ]
#        definition is the definition of word

# default implementation, just copy the content of the stardict dictionary
def parse(data, type_sequence, ignore_case):
    parsed_data = []
    for d in data:
        parsed_data += [ [ d[0], True, [], [], d[1] ] ]
    return parsed_data
### END parse ###

