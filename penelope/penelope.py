#!/usr/bin/env python

__license__     = 'GPLv3'
__author__      = 'Alberto Pettarin (pettarin gmail.com)'
__copyright__   = '2012 Alberto Pettarin (pettarin gmail.com)'
__version__     = 'v1.06'
__date__        = '2012-11-29'
__description__ = 'Penelope allows you to format your dictionaries for the Bookeen Cybook Odyssey e-reader'


### BEGIN changelog ###
#
# 1.05 Added StarDict output
# 1.04 Code refactoring before uploading to Google Code
# 1.03 Fixed a bug when using --xml and --parser
# 1.02 Added XML dictionary input
# 1.01 Initial release
#
### END changelog ###


import getopt, gzip, imp, os, sqlite3, struct, subprocess, sys, zipfile



### BEGIN collate_function ###
# collate_function(string1, string2)
# define the string comparison function for the index file
def collate_function(string1, string2):

    return cmp(string1.lower(), string2.lower())

### END collate_function ###


### BEGIN read_from_stardict_format ###
# read_from_stardict_format(idx_input_filename,
#   dict_input_filename, ignore_case)
# read data from the given stardict dictionary
# and return a list of [ [word, definition] ]
# if ignore_case = True, lowercase all the index word
def read_from_stardict_format(idx_input_filename,
        dict_input_filename, ignore_case):

    data = []

    # open files
    idx_input_file = open(idx_input_filename, 'rb')
    dict_input_file = open(dict_input_filename, 'rb')

    # read the whole dictionary in memory
    dict_input = dict_input_file.read()

    # read the index file byte-by-byte
    # TODO: is there a better way to handle this?
    word = ""
    byte = idx_input_file.read(1)
    while byte:
        if (byte == '\0'):
            # end of current word: read offset and size
            o = idx_input_file.read(4)
            oi = int((struct.unpack('>i', o))[0])
            s = idx_input_file.read(4)
            si = int((struct.unpack('>i', s))[0])

            # if ignore_case = True, lowercase word
            if ignore_case:
                word = word.lower()

            # extract the proper definition for word
            # and append it to current data
            data += [ [word, dict_input[oi:oi+si] ] ]

            # reset current word
            word = ""
        else:
            # append current character to current word
            word += str(byte)

        byte = idx_input_file.read(1)

    idx_input_file.close()
    dict_input_file.close()

    return data

### END read_from_stardict_format ###


### BEGIN read_from_xml_format ###
# read_from_xml_format(xml_input_filename, ignore_case)
# read data from the given XML dictionary
# and return a list of [ [word, definition] ]
# if ignore_case = True, lowercase all the index word
def read_from_xml_format(xml_input_filename, ignore_case):

    data = []

    # open file
    xml_input_file = open(xml_input_filename, 'rb')

    # read the whole dictionary in memory
    xml_input = xml_input_file.read()

    # TODO: not really robust code
    entry_pos = 0
    entry_pos = xml_input.find('<entry>', entry_pos)
    while entry_pos > -1:
        pos = xml_input.find('<key>', entry_pos)
        end_pos = xml_input.find('</key>', pos)
        key = xml_input[pos + len('<key>'): end_pos].strip()

        if ignore_case:
            key = key.lower()

        pos = xml_input.find('<def>', entry_pos)
        end_pos = xml_input.find('</def>', pos)
        definition = xml_input[pos + len('<def>'): end_pos].strip()

        data += [ [ key, definition ] ]

        entry_pos = xml_input.find('<entry>', entry_pos + 1)

    xml_input_file.close()

    return data

### END read_from_xml_format ###


### BEGIN write_to_Odyssey_format ###
# write_to_Odyssey_format(config, data, debug)
# write data to the Odyssey format, using the config settings
#
# config = [ dictionary_filename, index_filename, language_from, language_to,
#            license_string, copyright_string, title, description, year, info_filename ]
#
# data = [ word, include, synonyms, substitutions, definition ]
#
# where:
#        word is the sorting key
#        include is a boolean saying whether the word should be included
#        synonyms is a list of alternative strings for word
#        substitutions is a list of pairs [ word_to_replace, replacement ]
#        definition is the definition of word
def write_to_Odyssey_format(config, data, debug):

    # Note: chunks on Odyssey seems have size between
    # 262144 = 2^18 and 524288 = 2^19 bytes
    SPLIT_CHUNK_SIZE = 262144
    CHUNK_STRING = "c_"

    # read config parameters
    [ dictionary_filename,
      index_filename,
      language_from,
      language_to,
      license_string,
      copyright_string,
      title,
      description,
      year,
      info_filename ] = config

    # copy empty.idx into index_filename
    input_file = open('empty.idx', 'r')
    output_file = open(index_filename, 'w')
    output_file.write(input_file.read())
    input_file.close()
    output_file.close()

    # open index
    sql_connection = sqlite3.connect(index_filename)

    # install collation in the index
    sql_connection.create_collation("IcuNoCase", collate_function)
    sql_connection.text_factory = str

    # get a cursor
    sql_cursor = sql_connection.cursor()
    # delete any data from the index (just for safety...)
    sql_cursor.execute('delete from T_DictIndex ')

    # open debug file
    if debug:
        debug_file = open("debug." + dictionary_filename, "w")

    # split data in chunks of size between MAX_CHUNK_SIZE and 2*MAX_CHUNK_SIZE bytes
    byte_count = 0
    current_chunk = 1
    current_chunk_filename = CHUNK_STRING + str(current_chunk)
    current_chunk_file = open(current_chunk_filename, "w")
    chunk_filenames = [ current_chunk_filename ]

    # keep a dictionary of words, with their sql_tuples
    global_dictionary = dict()

    # keep a global list of substitutions
    global_substitutions = []

    # sort input data
    data.sort()

    for d in data:

        # get data
        word = d[0]
        include = d[1]
        synonyms = d[2]
        substitutions = d[3]
        if debug:
            # augment readability of c_* files
            definition = d[4] + "\n"
        else:
            # save 1 byte
            definition = d[4]
        definition_length = len(definition)

        if (include):
            # write definition to debug file
            if debug:
                debug_file.write(definition)

            # write definition to current chunk file
            current_chunk_file.write(definition)

            # insert word into index file
            sql_tuple = (0, word, byte_count, definition_length, current_chunk)
            sql_cursor.execute('insert into T_DictIndex values (?,?,?,?,?)', sql_tuple)

            # insert word into global dictionary
            global_dictionary[word] = sql_tuple

            # insert synonyms into index file, pointing at current definition
            for s in synonyms:
                sql_tuple = (0, s, byte_count, definition_length, current_chunk)
                sql_cursor.execute('insert into T_DictIndex values (?,?,?,?,?)', sql_tuple)

            # update byte count
            byte_count += definition_length

            # if the current chunk is complete, start new chunk Note: 262144 = 2^18
            if (byte_count > SPLIT_CHUNK_SIZE):
                current_chunk_file.close()
                current_chunk += 1
                current_chunk_filename = CHUNK_STRING + str(current_chunk)
                current_chunk_file = open(current_chunk_filename, "w")
                chunk_filenames += [ current_chunk_filename ]
                byte_count = 0
        else:
            if len(substitutions) > 0 :
                global_substitutions += substitutions

    # close output files
    if debug:
        debug_file.close()
    current_chunk_file.close()

    # zip chunk files into dictionary_filename
    dictionary_zip_file = zipfile.ZipFile(dictionary_filename, 'w', zipfile.ZIP_DEFLATED)
    for current_chunk_filename in chunk_filenames:
        dictionary_zip_file.write(current_chunk_filename)
    dictionary_zip_file.close()

    # delete chunk files unless debug mode is on
    if not debug:
        for current_chunk_filename in chunk_filenames:
            os.remove(current_chunk_filename)

    # process substitutions
    for substitution in global_substitutions:
        sub_from = substitution[0]
        sub_to = substitution[1]

        if sub_to in global_dictionary:
            sql_tuple = global_dictionary[sub_to]
            sql_tuple = ( sql_tuple[0], sub_from, sql_tuple[2], sql_tuple[3], sql_tuple[4] )
            sql_cursor.execute('insert into T_DictIndex values (?,?,?,?,?)', sql_tuple)

    # update index metadata
    header = "<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Strict//EN\"  \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd\" [<!ENTITY ns \"&#8226;\">]><html xml:lang=\"%s\" xmlns=\"http://www.w3.org/1999/xhtml\"><head><title></title></head><body>" % (language_from)

    sql_cursor.execute('update T_DictInfo set F_xhtmlHeader=?', (header,))
    sql_cursor.execute('update T_DictInfo set F_LangFrom=?', (language_from,))
    sql_cursor.execute('update T_DictInfo set F_LangTo=?', (language_to,))
    sql_cursor.execute('update T_DictInfo set F_Licence=?', (license_string,))
    sql_cursor.execute('update T_DictInfo set F_Copyright=?', (copyright_string,))
    sql_cursor.execute('update T_DictInfo set F_Title=?', (title,))
    sql_cursor.execute('update T_DictInfo set F_Description=?', (description,))
    sql_cursor.execute('update T_DictInfo set F_Year=?', (year,))
    sql_cursor.execute('update T_DictInfo set F_Alphabet=?', ('Z',))

    # these two fields might be unused
    sql_cursor.execute('update T_DictVersion set F_DictType=?', ('stardict',))
    sql_cursor.execute('update T_DictVersion set F_Version=?', ('1',))

    # compact and close index
    sql_cursor.execute('VACUUM')
    sql_cursor.close()
    sql_connection.close()

### END write_to_Odyssey_format ###


### BEGIN write_to_StarDict_format ###
# write_to_StarDict_format(config, data, debug)
# write data to the StarDict format, using the config settings
#
# config = [ dictionary_filename, index_filename, language_from, language_to,
#            license_string, copyright_string, title, description, year, info_filename ]
#
# data = [ word, include, synonyms, substitutions, definition ]
#
# where:
#        word is the sorting key
#        include is a boolean saying whether the word should be included
#        synonyms is a list of alternative strings for word
#        substitutions is a list of pairs [ word_to_replace, replacement ]
#        definition is the definition of word
def write_to_StarDict_format(config, data, debug):

    # read config parameters
    [ dictionary_filename,
      index_filename,
      language_from,
      language_to,
      license_string,
      copyright_string,
      title,
      description,
      year,
      info_filename ] = config


    # open debug file
    if debug:
        debug_file = open("debug." + dictionary_filename, "w")

    # keep a dictionary of words, with their sql_tuples
    global_dictionary = dict()

    # keep a global list of substitutions
    global_substitutions = []

    # sort input data
    # data.sort()

    # open dictionary file
    dictionary_file = open(dictionary_filename, "w")
    byte_count = 0

    for d in data:

        # get data
        word = d[0]
        include = d[1]
        synonyms = d[2]
        substitutions = d[3]
        if debug:
            # augment readability of c_* files
            definition = d[4] + "\n"
        else:
            # save 1 byte
            definition = d[4]
        definition_length = len(definition)

        if (include):
            # write definition to debug file
            if debug:
                debug_file.write(definition)

            # write definition to current chunk file
            dictionary_file.write(definition)

            # insert word into global dictionary
            sql_tuple = (word, byte_count, definition_length, 0)
            global_dictionary[word] = sql_tuple

            # insert synonyms into index file, pointing at current definition
            for s in synonyms:
                sql_tuple = (s, byte_count, definition_length, 0)
                global_dictionary[s] = sql_tuple
        else:
            if len(substitutions) > 0 :
                global_substitutions += substitutions

        byte_count += definition_length



    # close output files
    if debug:
        debug_file.close()
    dictionary_file.close()


    # process substitutions
    for substitution in global_substitutions:
        sub_from = substitution[0]
        sub_to = substitution[1]

        if sub_to in global_dictionary:
            sql_tuple = global_dictionary[sub_to]
            sql_tuple = ( sub_from, sql_tuple[1], sql_tuple[2], sql_tuple[3] )
            global_dictionary[sub_from] = sql_tuple


    # sort keys (needed by StarDict format)
    keys = global_dictionary.keys()
    keys.sort()

    # write index file
    index_file = open(index_filename, "w")
    for k in keys:
        sql_tuple = global_dictionary[k]
        index_file.write(sql_tuple[0])
        index_file.write('\0')
        index_file.write(struct.pack('>i', sql_tuple[1]))
        index_file.write(struct.pack('>i', sql_tuple[2]))
    index_file.close()


    # write info file
    info_file = open(info_filename, "w")
    info_file.write("StarDict's dict ifo file\n")
    info_file.write("version=2.4.2\n")
    info_file.write("wordcount=" + str(len(keys)) + "\n")
    info_file.write("idxfilesize=" + str(os.path.getsize(index_filename)) + "\n")
    info_file.write("bookname=" + title + "\n")
    info_file.write("date=" + year + "\n")
    info_file.write("sametypesequence=m\n")
    info_file.write("description=" + description + "<br/>" + license_string + "<br/>" + copyright_string + "\n")
    # These fields are available and optional in .ifo StarDict files:
    # info_file.write("author=" + XXX + "\n")
    # info_file.write("email=" + XXX + "\n")
    # info_file.write("website=" + XXX + "\n")
    info_file.close()

### END write_to_Odyssey_format ###


### BEGIN compress_install_file ###
# compress_install_file(dictionary_filename, index_filename, zip_filename)
# compress dictionary_filename and index_filename into zip_filename
#
def compress_install_file(dictionary_filename, index_filename, zip_filename):

    print_info("Creating zip file " + zip_filename + "...")
    zip_file = zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED)
    zip_file.write(dictionary_filename)
    zip_file.write(index_filename)
    zip_file.close()
    print_info("File " + zip_filename + " created successfully!")


### END compress_StarDict_dictionary ###


### BEGIN compress_StarDict_dictionary ###
# compress_StarDict_dictionary(dictionary_filename, compressed_dictionary_filename, delete_uncompressed)
# compress dictionary_filename into compressed_dictionary_filename
# if delete_uncompressed is True, delete dictionary_filename
#
# Note: if dictzip is not found, simply keep the dictionary uncompressed
#
def compress_StarDict_dictionary(dictionary_filename, compressed_dictionary_filename, delete_uncompressed):

    # TODO: compressing with gzip library seems not working, I need to call dictzip

    # compress the dictionary file with dictzip
    print_info("Creating compressed dictionary file " + compressed_dictionary_filename + "...") 
    return_code = subprocess.call(["dictzip", "-k", dictionary_filename])

    # check whether the compression was successful
    if return_code == 0:
        print_info("File " + compressed_dictionary_filename + " created successfully!")

        # delete the uncompressed dictionary
        if delete_uncompressed:
            os.remove(dictionary_filename)
    else:
        print_info("File " + compressed_dictionary_filename + " cannot be created. Check that dictzip is installed in your system.")

    return return_code

### END compress_StarDict_dictionary ###


### BEGIN read_command_line_parameters ###
# read_command_line_parameters()
# read the command line parameters, and return the following list:
# config = [ prefix, language_from, language_to,
#            license, copyright, title, description, year
#            debug, ignore_case, parser_filename, create_zip, input_format ]
# -p : prefix
# -f : language from
# -t : language to
# -d : debug mode
# -h : print usage and exit
# -i : ignore word case
# -z : create *.install zip file
# --license : license
# --copyright : copyright
# --title : title
# --description : description
# --year : year
# --parser : parser to be used while parsing input dictionary
# --sd : input format is StarDict (default)
# --xml : input format is XML
# --output-sd : output format is StarDict
def read_command_line_parameters(argv):

    try:
        optlist, free = getopt.getopt(argv[1:], 'dhizf:p:t:',
            ['license=', 'copyright=', 'title=',
                'description=', 'year=', 'parser=',
                'sd', 'xml', 'output-sd'])
    except getopt.GetoptError, err:
        print_error(str(err))
        usage()
        sys.exit(1)

    optdict = dict(optlist)

    if '-h' in optdict:
        usage()
        sys.exit(0)

    prefix = ''
    if '-p' in optdict:
        prefix = optdict['-p']
    else:
        print_error('No prefix parameter was supplied.')

    input_format = 'sd'
    if '--sd' in optdict:
        input_format = 'sd'
    if '--xml' in optdict:
        input_format = 'xml'

    output_format = 'odyssey'
    if '--output-sd' in optdict:
        output_format = 'sd'

    language_from = ''
    if '-f' in optdict:
        language_from = optdict['-f']
    else:
        if output_format == 'odyssey':
            print_error('No language_from parameter was supplied.')

    language_to = ''
    if '-t' in optdict:
        language_to = optdict['-t']
    else:
        if output_format == 'odyssey':
            print_error('No language_to parameter was supplied.')

    if '--license' in optdict:
        license_string = optdict['--license']
    else:
        license_string = 'GNU GPL 3'

    if '--copyright' in optdict:
        copyright_string = optdict['--copyright']
    else:
        copyright_string = 'GNU GPL 3'

    if '--title' in optdict:
        title = optdict['--title']
    else:
        title = 'Dictionary ' + language_from + ' -> ' + language_to 

    if '--description' in optdict:
        description = optdict['--description']
    else:
        description = title

    if '--year' in optdict:
        year = optdict['--year']
        print year
    else:
        year = '2012'

    if '--parser' in optdict:
        parser_filename = optdict['--parser']
    else:
        parser_filename = None

    debug = False
    if '-d' in optdict:
        debug = True

    ignore_case = False
    if '-i' in optdict:
        ignore_case = True

    create_zip = False
    if '-z' in optdict:
        create_zip = True

    return [ prefix, language_from, language_to,
             license_string, copyright_string, title, description, year,
             debug, ignore_case, parser_filename, create_zip,
             input_format, output_format ]

### END read_command_line_parameters ###


### BEGIN print_config ###
# print_config(config)
# print the configuration that will be used in the dictionary conversion
#
# config = [ dictionary_filename, index_filename, language_from, language_to,
#            license, copyright, title, description, year ]
def print_config(config):
    print_info("Dictionary file: " + config[0])
    print_info("Index file:      " + config[1])
    print_info("Language from:   " + config[2])
    print_info("Language to:     " + config[3])
    print_info("License:         " + config[4])
    print_info("Copyright:       " + config[5])
    print_info("Title:           " + config[6])
    print_info("Description:     " + config[7])
    print_info("Year:            " + config[8])

### END print_config ###


### BEGIN check_ifo_file ###
# check_ifo_file(ifo_filename)
# checks that ifo_filename exists and has the right format
def check_ifo_file(ifo_filename):
    if not os.path.isfile(ifo_filename):
        return False, None

    type_sequence = ''
    ifo_file = open(ifo_filename, 'r')
    for line in ifo_file:
        if line.strip().find('sametypesequence') > -1:
            type_sequence = line.strip().split('=')[1]
    ifo_file.close()

    if type_sequence in ['m', 'l', 'x', 'w']:
        return True, type_sequence
    else:
        return False, type_sequence

### END check_ifo_file ###


### BEGIN check_idx_file ###
# check_idx_file(idx_filename)
# checks that idx_filename exists, uncompressing it if it was compressed
def check_idx_file(idx_filename):
    uncompressed = idx_filename
    compressed = idx_filename + ".gz"

    if os.path.isfile(uncompressed):
        return True

    if os.path.isfile(compressed):
        uncompressed_idx_file = open(uncompressed, 'w')
        compressed_idx_file = gzip.open(compressed, 'r')
        uncompressed_idx_file.write(compressed_idx_file.read())
        compressed_idx_file.close()
        uncompressed_idx_file.close()
        return True

    return False

### END check_idx_file ###


### BEGIN check_dict_file ###
# check_dict_file(dict_filename)
# checks that dict_filename exists, uncompressing it if it was compressed
def check_dict_file(dict_filename):
    uncompressed = dict_filename
    compressed = dict_filename + ".dz"

    if os.path.isfile(uncompressed):
        return True

    if os.path.isfile(compressed):
        uncompressed_idx_file = open(uncompressed, 'w')
        compressed_idx_file = gzip.open(compressed, 'r')
        uncompressed_idx_file.write(compressed_idx_file.read())
        compressed_idx_file.close()
        uncompressed_idx_file.close()
        return True

    return False

### END check_dict_file ###


### BEGIN check_xml_file ###
# check_xml_file(xml_filename)
# checks that xml_filename exists
def check_xml_file(xml_filename):

    return os.path.isfile(xml_filename)

### END check_xml_file ###


### BEGIN check_parser ###
# check_parser(parser_filename)
# checks that parser_filename exists and can be loaded
def check_parser(parser_filename):
    if parser_filename == None:
        return None

    if not os.path.isfile(parser_filename):
        return None
    try:
        parser = imp.load_source('', parser_filename)
        parser.parse([], 'x', False)
    except Exception:
        return None

    return parser

### END check_parser ###


### BEGIN check_existence ###
# check_existence(filename)
# checks whether filename exists
def check_existence(filename):
    if filename == None:
        return False

    return os.path.isfile(filename)

### END check_existence ###


### BEGIN print_error ###
# print_error(error, displayusage=True)
# print the given error, call usage, and exit
# optional displayusage to skip usage

def print_error(error, displayusage = True):
    sys.stderr.write ("[ERROR] " + error + " Aborting.\n")
    if displayusage :
        usage()
    sys.exit(1)

### END print_error ###


### BEGIN print_info ###
# print_info(info)
# print the given info string
def print_info(info):
    print "[INFO] " + info

### END print_info ###


### BEGIN usage ###
# usage()
# print script usage
def usage():
    print ''
    print '$ python penelope.py -p <prefix> -f <language_from> -t <language_to> [OPTIONS]'
    print ''
    print 'Required arguments include:'
    print ' -p <prefix>            : name of the dictionary to be converted (prefix.ifo, prefix.idx[.gz], prefix.dict[.dz])'
    print ' -f <language_from>     : ISO 631-2 code language_from of the dictionary to be converted'
    print ' -t <language_to>       : ISO 631-2 code language_to of the dictionary to be converted'
    print ''
    print 'Optional arguments include:'
    print ' -d                     : enable debug mode and do not delete temporary files'
    print ' -h                     : print this usage message and exit'
    print ' -i                     : ignore word case while building the dictionary index'
    print ' -z                     : create the .install zip file containing the dictionary and the index'
    print ' --sd                   : input dictionary in StarDict format (default)'
    print ' --xml                  : input dictionary in XML format (<entry><key>...</key><def>...</def></entry> ...)'
    print ' --output-sd            : output dictionary in StarDict format'
    print ' --title <string>       : set the title string shown on the Odyssey screen to <string>'
    print ' --license <string>     : set the license string to <string>'
    print ' --copyright <string>   : set the copyright string to <string>'
    print ' --description <string> : set the description string to <string>'
    print ' --year <string>        : set the year string to <string>'
    print ' --parser <parser.py>   : use <parser.py> to parse the input dictionary'
    print ''
    print 'Examples:'
    print '$ python penelope.py -h'
    print ' Print usage message and exit'
    print ''
    print '$ python penelope.py -p foo -f en -t en'
    print ' Create English monolingual dictionary en.foo.dict and en.foo.dict.idx from StarDict files foo.*'
    print ''
    print '$ python penelope.py --xml -p foo -f en -t en'
    print ' As above, but the input dictionary foo.xml is in XML format'
    print ''
    print '$ python penelope.py --xml --output-sd -p foo -f en -t en'
    print ' As above, but outputs in StarDict format'
    print ''
    print '$ python penelope.py -p bar -f en -t it'
    print ' Create English-to-Italian dictionary en-it.dict and en-it.dict.idx from StarDict files bar.*'
    print ''
    print '$ python penelope.py -p bar -f en -t it --title "My EN->IT dictionary" --year 2012 --license "CC-BY-NC-SA 3.0"'
    print ' As above but also set title, year and license metadata'
    print ''
    print '$ python penelope.py -p foo -f en -t en --parser foo_parser.py --title "Custom EN dictionary"'
    print ' As above but set its title and use foo_parser.py to parse the input dictionary definitions'
    print ''
    print '$ python penelope.py -p foo -f en -t en --parser foo_parser.py --title "Custom EN dictionary" -i'
    print ' As above but ignore case when inserting words into the index'
    print ''

### END usage ###


### BEGIN main ###
def main():

    # read command line parameters
    [ prefix,
      language_from,
      language_to,
      license_string,
      copyright_string,
      title,
      description,
      year,
      debug,
      ignore_case,
      parser_filename,
      create_zip,
      input_format,
      output_format ] = read_command_line_parameters(sys.argv)

    type_sequence = 'unknown'
    if input_format == 'sd':
        # check ifo input file
        ifo_input_filename = prefix + ".ifo"
        readable, type_sequence = check_ifo_file(ifo_input_filename)
        if not readable:
            print_error("File " + ifo_input_filename + " not found or with wrong format.")
        print_info("Input dictionary has sequence type '" + type_sequence + "'.")

        # check idx input file, uncompressing it if it was compressed
        idx_input_filename = prefix + ".idx"
        readable = check_idx_file(idx_input_filename)
        if not readable:
            print_error("File " + idx_input_filename + " not found (even compressed).")

        # check dict input file, uncompressing it if it was compressed
        dict_input_filename = prefix + ".dict"
        readable = check_dict_file(dict_input_filename)
        if not readable:
            print_error("File " + dict_input_filename + " not found (even compressed).")


    if input_format == 'xml':
        # check xml input file
        xml_input_filename = prefix + ".xml"
        readable = check_xml_file(xml_input_filename)
        if not readable:
            print_error("File " + xml_input_filename + " not found.")


    # check parser input file, if one was given
    parser = check_parser(parser_filename)
    if parser_filename != None and parser == None:
        print_error("Parser " + parser_filename + " not found or with no parse(data, type_sequence, ignore_case) function.")


    # set default dictionary, index and info filenames
    if output_format == 'odyssey':
        if language_from == language_to:
            dictionary_filename = language_from + "." + prefix + ".dict"
        else:
            dictionary_filename = language_from + "-" + language_to + ".dict"
        index_filename =  dictionary_filename + ".idx"
        info_filename = ''

    if output_format == 'sd':
        dictionary_filename = prefix + ".dict"
        index_filename = prefix + ".idx"
        info_filename = prefix + ".ifo"
        compressed_dictionary_filename = dictionary_filename + ".dz"

        existing = False
        existing = existing or check_existence(dictionary_filename)
        existing = existing or check_existence(index_filename)
        existing = existing or check_existence(info_filename)
        existing = existing or check_existence(compressed_dictionary_filename)

        if existing:
            dictionary_filename = "new." + prefix + ".dict"
            index_filename = "new." + prefix + ".idx"
            info_filename = "new." + prefix + ".ifo"
            compressed_dictionary_filename = dictionary_filename + ".dz"


    # set the config list
    config = [ dictionary_filename,
               index_filename,
               language_from,
               language_to,
               license_string,
               copyright_string,
               title,
               description,
               year,
               info_filename ]


    # let the user know whether debug mode is on
    if debug:
        print_info('Debug mode is on.')


    # let the user know whether ignore_case mode is on
    if ignore_case:
        print_info('Ignoring word case while building the index.')


    # let the user know what is going on
    print_info('Starting conversion with the following parameters:')
    print ""
    print_config(config)
    print ""


    # read input files
    print_info('Reading input dictionary...')
    # data = [ [word, definition] ]
    if input_format == 'sd':
        data = read_from_stardict_format(idx_input_filename,
            dict_input_filename, ignore_case)

    if input_format == 'xml':
        data = read_from_xml_format(xml_input_filename, ignore_case)


    # parse input files
    print_info('Parsing the input dictionary...')
    parsed_data = []
    if parser == None:
        print_info('Using the built-in parser...')
        for d in data:
            parsed_data += [ [ d[0], True, [], [], d[1] ] ]
    else:
        print_info("Using the custom parser defined in " + parser_filename + " ...")
        parsed_data = parser.parse(data, type_sequence, ignore_case)


    # write out to Odyssey format
    if output_format == 'odyssey':
        print_info('Outputting in Odyssey format to file...')
        write_to_Odyssey_format(config, parsed_data, debug)
        print_info("Files " + dictionary_filename + " and " + index_filename + " created successfully!")

        # create zip .install file, if the user asked for it
        if create_zip:
            zip_filename = dictionary_filename + ".install"
            compress_install_file(dictionary_filename, index_filename, zip_filename)

    # write out to StarDict format
    if output_format == 'sd':
        print_info('Outputting in StarDict format to file...')
        write_to_StarDict_format(config, parsed_data, debug)
        delete_uncompressed = not debug
        return_code = compress_StarDict_dictionary(dictionary_filename, compressed_dictionary_filename, delete_uncompressed)

        if return_code == 0:
            print_info("Files " + compressed_dictionary_filename + ", " + index_filename + ", and " + info_filename + " created successfully!")
        else:
            print_info("Files " + dictionary_filename + ", " + index_filename + ", and " + info_filename + " created successfully!")

### END main ###



if __name__ == '__main__':
    main()



