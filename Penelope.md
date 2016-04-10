# Penelope #

Penelope is a utility that allows you to format a dictionary for the _[Bookeen Cybook Odyssey e-reader](http://bookeen.com/en/cybook/odyssey)_.

# Details #

With the current version (v. 1.05, 2012-03-19) you can convert a _StarDict_ or _XML_ dictionary into the Odyssey format, and define your own parser for each word/definition. You can also output to _StarDict_ format instead of _Cybook Odyssey_ (this is useful when converting dictionaries from _XML_ to _StarDict_, or when you are writing your own parser for a given _StarDict_).

Future versions will include support for more advanced XML input parsing and for merging multiple input dictionaries into a single one.

Please have a look at this web page for details until the documentation is completely moved over to this Wiki: http://www.albertopettarin.it/penelope.html



# Manual #

As mentioned above the documentation including a manual is not completely
ported over to GoogleCode. The documentation can be found on these
WikiPages: [ScriptUsage](ScriptUsage.md), [Conversion](Conversion.md), [DictionaryFormatOdyssey](DictionaryFormatOdyssey.md)

For more information, follow http://www.albertopettarin.it/penelope.html
for now, as the WikiPages are not linked together yet for a complete manual.




# History #

Penelope started as a personal collection of scripts, partly in Python, partly
in shell scripts, partly in some unknown formats you don't even want ot know
about. As interest grew by other people in my reverse-engeneering of the
dictionary format in the _Cybook Odyssey_, _Penelope_ started to evolve. A
suggestions of making it platform independent resulted in me rewriting parts of
those original scripts into Python. Another suggestions made me check out
revision control systems that don't depend on me keeping the source files and
documentation updated all by myself.

[GoogleCode](http://code.google.com/) combinded with Mercurial as Repository
turned out to be a nice choice. This provides easy access to developers and
end-users both. Just having it moved over not too long ago (2012-03-07) it
still needs to be converted for _GoogleCode_, especially the Wiki itself. If
you want to join the project, or have suggestions please contact me (see
email adress on bottom of page). Leaving a comment is also a viable option.


# Download #

You can download all files for Penelope from this
[Google Code](http://penelope-dictionary-converter.googlecode.com/hg/penelope/)
page. That will have the current most up to date versions of files necessary
for Penelope. A _Python 2.7.2+_ installation on your computer is also required.
**Note:** _Python 3+_ is not supported at the moment, and the code is not compatible
with it.

If you are interested in viewing the files  online with syntax
highlighting and option to browse older revisions, please check out the
[Browse Source page](http://code.google.com/p/penelope-dictionary-converter/source/browse/#hg%2Fpenelope).
Alternativly you are welcome to check out the whole Mercurial Repository from the
[Checkout](http://code.google.com/p/penelope-dictionary-converter/source/checkout)
to view all files offline with all revisions included. **Note:** additional
Software might need to be downloaded and installed to do so.

As of right now there will not be a _**one button download**_ for _Penelope_, since
it is mainly a Python script with supporting files. Different dictionaries are
going to need different settings to run, especially if your input dictionary is
not of perfect quality. The dictionaries included in the _**dictionary beta**_
from _Bookeen_ are not formated really nice for display on the _Odyssey_ for
example. Penelope gives more control back into your hands, if you so desire.
Furthermore it is your responsibility to ensure that what you are feeding this
script is in the correct format needed, otherwise unexpected results may occur.

# Disclaimer #

_Penelope_ and the developers are **NOT** affiliated in any way shape or form with
[Bookeen](http://bookeen.com/), the manufacturer of the _Cybook Odyssey_. This is **NOT** an official
tool from _Bookeen_, nor does _Bookeen_ provide any support for it. Use of
_Penelope_ and resulting possible damaging outcome to your computer or _Odyssey_
or data is _**at your own risk**_. Please use _Penelope_ responsibly. Make sure
to backup your input-dictionary and only work on a copy while using _Penelope_.
_Penelope_ is not designed to change your input files, but that behavior cannot
be guranteed in every case.



---


If you want to contribute some code or you have suggestions, please let me know by sending an email to pettarin AT gmail DOT com  containing the word "Penelope" in the subject. Thanks!