Following are two examples on how to convert a dictionary to the format needed
for the _Cybook Odyssey_ e-book reader. Please refer to the ScriptUsage for a more detailed list of options for [Penelope](Penelope.md).

# Convert a StarDict dictionary #


Since StarDict dictionaries have been quite popular, I decided to code a script
to convert a StarDict dictionary into the format used in the _Cybook Odyssey_. I
release it under _GNU GPL 3_, so you can do a lot with it! It has been developed
and tested on _Debian Wheezy_, with _Python 2.7.2+_, but it should work on most
platform where the same Python version is available.


  * To start, get **[penelope.py](http://code.google.com/p/penelope-dictionary-converter/source/browse/penelope/penelope.py)** and **[empty.idx](http://code.google.com/p/penelope-dictionary-converter/source/browse/penelope/empty.idx)** from [Google Code](http://code.google.com/p/penelope-dictionary-converter/source/browse/#hg%2Fpenelope) and copy them into the same directory.
  * Copy your StarDict dictionary files (say, **`mydict.ifo`**, **`mydict.dict[.dz]`**, and **`mydict.idx[.gz]`**) into the same directory
  * Run the script:```python
$ python penelope.py -p mydict -f en -t en```The above command should create two files in the working directory: **`en.mydict.dict`** and **`en.mydict.dict.idx`**
  * Copy the two files to the **`Dictionaries`** directory of your Odyssey and you are done! You should be able to use your en-en dictionary on your Odyssey!



# Convert a XML dictionary #


  * If you want to create your own dictionary from some data source, you might want to output your dictionary data with the following format:
    * Each entry is represented by a _**entry**_ tag.
    * Each entry has two children tags: _**key**_ and _**def**_, representing the keyword to be inserted in the dictionary index and its definition, respectively.
    * Please see this **[DTD](http://code.google.com/p/penelope-dictionary-converter/source/browse/penelope/dictionary.dtd)** for reference.
  * Click to see the example file **[test.xml](http://code.google.com/p/penelope-dictionary-converter/source/browse/penelope/test.xml)**.
  * Note that my _"XML parser"_ for the input dictionary just perform the following actions:
    * looks for the beginning of the next _**entry**_ tag, say at byte `x` of the input file;
    * looks for the beginning and end of the next _**key**_ tag after `x` and extract the text between them, identifying it as the word to be included in the index;
    * looks for the beginning and end of the next _**def**_ tag after `x` and extract the text between them, identifying it as the definition of the current word;
repeat, starting from byte `x+1` of the input file.
  * This approach is quite fragile (my code does not check that your input file is well-formed!), but it also yields fast code and it allows you to ignore other tags and newlines in the definitions. The assumption is that you know what you are feeding into my script!
Note that you do not need to actually provide a valid XML file, with the proper header and DTD-compliant as in the **[example](http://code.google.com/p/penelope-dictionary-converter/source/browse/penelope/test.xml)**, but doing so helps checking the input file in browsers that are XML-picky, like Firefox; a sequence of _**entry**_ tags is enough for my script.
  * As above, get **[penelope.py](http://code.google.com/p/penelope-dictionary-converter/source/browse/penelope/penelope.py)** and **[empty.idx](http://code.google.com/p/penelope-dictionary-converter/source/browse/penelope/empty.idx)**, and copy them into the same directory.
  * Copy your XML dictionary file (say, **`mydict.xml`**) into the same directory.
  * Run the script:```python
$ python penelope.py --xml -p mydict -f en -t en```The above command should create two files in the working directory: **`en.mydict.dict`** and **`en.mydict.dict.idx`**.
  * Copy the two files to the **`Dictionaries`** directory of your Odyssey and you are done! You should be able to use your en-en dictionary on your Odyssey!
