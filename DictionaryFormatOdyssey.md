In this page I report my findings about the dictionary management of the
_[Bookeen](http://bookeen.com/en/)_
_[Cybook Odyssey](http://bookeen.com/en/cybook/odyssey)_ e-reader, firmware
1485. Bear in mind that no official specifications are published by Bookeen
(as of 2012-03-23), so what follows is the result of my speculations.

# Dictionary management on the _Odyssey_ #

  * Dictionaries are located in the **`Dictionaries/`** directory in the user-accessible internal data partition of the _Odyssey_, **not** the SD-Card
  * Each dictionary has two files: an index (**`$NAME.dict.idx`**) and a definition file (**`$NAME.dict`**), where _**$NAME**_ is the dictionary name.
  * For a monolingual dictionary, _**$NAME**_ must be _**$XX.$STRING**_, where _**$XX**_ is the `ISO 639-1` code of the language, and _**$STRING**_ is an arbitrary label.
    * Example: **`en.foo.dict`** and **`en.foo.dict.idx`**.
  * For a bilingual dictionary, _**$NAME**_ must be _**$XX-$YY**_, where _**$XX**_ (resp., _**$YY**_) is the `ISO 639-1` code of the language from (resp., to) of the dictionary.
    * Example 1: **`en-it.dict`** and **`en-it.dict.idx`** is the English-to-Italian dictionary.
    * Example 2: **`it-fr.dict`** and **`it-fr.dict.idx`** is the Italian-to-French dictionary.
  * Right now, the selection of a dictionary is done in the following order:
    1. If the book you are reading has no language metadatum, then the default French dictionary is used. (This dictionary is stored in the system partition of the Odyssey, which is not accessible by the user.)
    1. Otherwise, let _**$XX**_ be the language of the book, and let _**$YY**_ be the language of the _Odyssey's_ interface.
      1. If the bilingual dictionary **`$XX-$YY.dict`** exists, then it is used.
      1. Otherwise, if the monolingual dictionary **`$XX.*.dict`** exists, then it is used.
      1. Finally, the default French dictionary is used.
  * Right now, the user cannot directly select the dictionary to be used. I hope Bookeen will implement this feature in a future firmware. Apparently, you can have only one bilingual dictionary for each language pair (_**$XX-$YY**_) while it is not clear to me which dictionary is used if you have two monolingual dictionaries **`$XX.1.dict`** and **`$XX.2.dict`** for the same language _**$XX**_.
  * Apparently, when you select a word, the index is queried for a stemmed version of the word. The rules applied might vary depending on the language. Unfortunately, I have not been able to look at this issue extensively, but I noticed that, for example, plurals are recognized in English and French, but not in Italian. However, you can bypass this issue by inserting declinated/conjugated forms in the index, making them point to the definition of the base form. **Note:** this might not be language, but dictionary dependend as the supplied dictionaries in the _Odyssey_ for lack of better word do not posess acceptable quality, especially the formating of descriptions in the en-en dictionary.
  * When more than one entry per word exists in the dictionary, the _Odyssey_ awkwardly displays a list with no decernible differentiation from one to the other, keeping you guessing which definition you just looked up. The lookup itself is always case-insensitive, but the display of those entries in the list is not. It would be nice if there was at least a number infront of each entry in that list.
  * In firmware 1485 there is no lookup function for a dictionary, unless you "click" on a word in an e-book or pdf file. Especially you cannot lookup a word while inside the dictionary looking at another word. Keep that in mind when creating your dictionary, since references inside a definition are useless as you cannot acess them with the _Odyssey_. Hopefully _Bookeen_ will include a "search in book", "lookup in dictionary", "link/refer in dictionary", and the very basic "manually choose which dictionary to use" in a future firmware update.


# Format of the definition file #


  * The dictionary file (say, **`en.foo.dict`**) is simply a zip file of plain text files, **`c_1`**, **`c_2`**, ..., **`c_n`**.
  * Each chunk file **`c_i`** contains utf-8 encoded definitions of words, concatenated one after another. Two consecutive definitions do not need to be separated by newlines or other special separator, since the index specifies the boundaries of each definition as an offset and a length, in bytes, from the beginning of the chunk (see below).
  * Apparently, each definition is an HTML fragment. Hence, you can use HTML tags to specify bold or italic face, divs, etc.. I have not performed an exhaustive search for the supported tags yet.
  * Each chunk file has (uncompressed) size between 2<sup>18</sup> = 262,144 bytes and 2<sup>19</sup> = 524,288 bytes. This is probably due to the memory management of the device, and it is consistent with the EPUB requirement of having single files of at most 300 KB. In fact, the script closes the current chunk (and opens a new one) whenever its size reaches 2<sup>18</sup> bytes.


# Format of the index file #


  * The index file (say, **`en.foo.dict.idx`**) is an _sqlite3_ database, with four tables (_**T\_DictVersion**_, _**T\_DictInfo**_, _**T\_DictIndex**_, _**T\_RefKey**_) and an index (_**F\_WordIndex**_) based on a collation (_**IcuNoCase**_).
  * Table _**T\_DictVersion**_ contains two fields: _**F\_Version**_ `(INTEGER)` and _**F\_DictType**_ `(TEXT)`. There is only one record, and it seems to me that the latter is used for documentation reasons only.
  * Table T\_DictInfo contains the metadata associated with the dictionary. It has only one record, with the following `TEXT` fields:
    * _**F\_Title**_
    * _**F\_Description**_
    * _**F\_Licence**_
    * _**F\_Copyright**_
    * _**F\_Year**_
    * _**F\_LanguageFrom**_
    * _**F\_LanguageTo**_
    * _**F\_Alphabet**_
    * _**F\_xhtmlHeader**_
  * Fields names are quite self-explanatory. Let me observe that _**F\_Title**_ represents the string shown on the _Odyssey_ as the dictionary's heading. I do not know what _**F\_Alphabet**_ means (it always has value _**"Z"**_), perhaps it represents the encoding used in the dictionary definitions.
  * Table _**T\_DictIndex**_ contains the dictionary lookup table. It has one record for each word, with the following fields:
    * _**F\_Key**_ `(INTEGER)`
    * _**F\_Word**_ `(TEXT)`
    * _**F\_Offset**_ `(INTEGER)`
    * _**F\_Size**_ `(INTEGER)`
    * _**F\_ChunckNum**_ `(INTEGER)`
> For example _**(0, foo, 350, 45, 7)**_ means that the definition of word _**foo**_ starts at byte _**350**_ of file **`c_7`** and it has length _**45**_ bytes.
  * Table _**T\_RefKey**_ contains two fields: _**F\_Key**_ `(INTEGER)` and _**F\_RefKey**_ `(INTEGER)`. In all the index files from _Bookeen_ I have seen this table is empty, and its meaning is unknown to me.