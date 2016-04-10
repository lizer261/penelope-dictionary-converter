# Script Usage of `penelope.py` #

The script (**`penelope.py`**) **must** be invoked with **at least** the following three parameters:
  * _**-p prefix**_ : _**prefix**_ is the name of your input StarDict dictionary, without extension
  * _**-f xx**_ : _**xx**_ is the ISO 639-1 code of the language _"from"_ of the dictionary
  * _**-t yy**_ : _**yy**_ is the ISO 639-1 code of the language _"to"_ of the dictionary

The following **optional** parameters are available:
  * _**-h**_ : print usage message and exit
  * _**-d**_ : enable debug mode and do not delete temporary files
  * _**-i**_ : ignore word case while building the dictionary index
  * _**-z**_ : create the **`*.install`** zip file containing the dictionary and the index
  * _**--sd**_ : input dictionary in StarDict format (**default**)
  * _**--xml**_ : input dictionary in XML format (see above)<a href='Hidden comment: see above what? '></a>
  * _**--output-sd**_ : output dictionary in StarDict format
  * _**--title string**_ : set the title string shown on the Odyssey screen to `string`
  * _**--license string**_ : set the license string to _**string**_
  * _**--copyright string**_ : set the copyright string to _**string**_
  * _**--description string**_ : set the description string to _**string**_
  * _**--year string**_ : set the year string to _**string**_
  * _**--parser parser.py**_ : use **`parser.py`** to parse the input dictionary


> The order of the parameters is irrelevant.<br />


# Examples #

  * Print usage message and exit:```sh
$ python penelope.py -h```
  * Create English monolingual dictionary **`en.foo.dict`** and **`en.foo.dict.idx`** from StarDict files **`foo.*`**:```sh
$ python penelope.py -p foo -f en -t en```
  * As above, but the input dictionary **`foo.xml`** is in XML format:```sh
$ python penelope.py --xml -p foo -f en -t en```
  * As above, but output in StarDict format instead of Cybook Odyssey format:```sh
$ python penelope.py --xml -p foo -f en -t en --output-sd```
  * Create English-to-Italian dictionary **`en-it.dict`** and **`en-it.dict.idx`** from StarDict files **`bar.*`**:```sh
$ python penelope.py -p bar -f en -t it```
  * As above but also set _title_, _year_ and _license_ metadata:```sh
$ python penelope.py -p bar -f en -t it --title "My EN-IT dictionary" --year 2012 --license "CC-BY-NC-SA 3.0"```
  * As above but set its _title_ and use **`foo_parser.py`** to parse the input dictionary definitions:```sh
$ python penelope.py -p foo -f en -t en --parser foo_parser.py --title "Custom EN dictionary"```
  * As above but ignore case when inserting words into the index:```sh
$ python penelope.py -p foo -f en -t en --parser foo_parser.py --title "Custom EN dictionary" -i```


# Custom parser for the input dictionary #

  * By default, the script will just convert the given StarDict dictionary to the Cybook Odyssey format. In other words, it will create the same index of words as it appears in the input dictionary, and it will simply copy the associated definitions with their original formatting.

  * However, you might want to aggregate different definitions for the same word into a single index entry, even if in the original dictionary they appeared as separate entries. (Example: `"Word (1)"` and `"Word (2)"`, etc.) Moreover, you might want to perform some changes in the formatting of the definitions. Clearly this operation is input-dependent, as different StarDict dictionaries have different formatting.

  * To do so, you can issue the optional argument _**--parser parser.py**_ to instruct the script to process the input dictionary with the parser defined in file **`parser.py`**

  * Your parser will contain a function```python
parse(data, type_sequence, ignore_case)``` that will take the input dictionary _**data**_ (as a list of pairs _**`[`word, definition`]`**_), the _**type\_sequence**_ of the input dictionary and the _**ignore\_case**_ switch.

  * The output of your parse function is a list of tuples with the following format:```python
[ word, include, synonyms, substitutions, definition ]```where:
    * _**word**_ is the index key (STRING).
    * _**include**_ is a BOOLEAN telling the script if the current record should be included in the index.
    * _**synonyms**_ is a LIST of STRINGs that will be added to the index and will point to the current _**definition**_. It will be used only if _**include**_ is _**True**_.This is useful if you can extract declinated/conjugated forms from the input definition and you want them to point to the base form _**word**_.
    * _**substitutions**_ is a LIST of pairs _**[replace\_what, replace\_with]**_. Each _**replace\_what**_ will be added to the index and will point to _**replace\_with**_, if the latter exists in the dictionary. It will be used only if _**include**_ is _**False**_. This is useful if you can infer that the current word is a declinated/conjugated form and you want to directly refer to its base form instead of showing a rather un-informative definition like _"cats is the plural of cat"_.
    * _**definition**_ is the STRING containing the text of the definition for the current _**word**_.
  * Please see the included **[webster\_parser.py](http://code.google.com/p/penelope-dictionary-converter/source/browse/penelope/webster_parser.py)** parser for the Webster 1913 StarDict dictionary (you can find it as **`StarDict-comn_sdict_axm05_webster_1913-2.4.2.tar.bz2`** on the Web) to get an idea of how the parser is supposed to work. Reading the source code of this parser will help as well.