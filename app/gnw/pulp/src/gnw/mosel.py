# ==============================================================================
#
#   package         :   GasNetWorks (gnw) Python/pulp fuelled LP/MIP modeller 
#   author          :   Marc Roth (re04179)
#   version         :   $Id: mosel.py 1860 2009-09-07 12:09:18Z re04179 $
#   heading         :   $HeadURL: http://subversion.rwe.com/svn/s_and_v_projects/GasNetworks/trunk/app/gnw/pulp/src/gnw/mosel.py $
#
#   Description     :   Package file
#
#   Creation Date   :   11Mar2009
#
#   Copyright       :   RWE Supply and Trading GmbH
#
# ==============================================================================
"""
gnw: Facilitates parsing of Mosel initialisation file formated data files  
"""
import csv


class MoselInitFileReader:
    """
    Encapsulation of reader functionality to
    read in Mosel formatted initialisation files 
    """    
    def read_mosel_init_file(fname, aDict = {}):
        """
        @param fname: filename of Mosel initialisation file.
        @type fname: L{str}
        
        @param aDict: optional dictionary to which
            entries read from file fname are inserted.
        @type aDict: L{dict}
        
        @return: aDict with additional elements inserted
            which have been read from file fname
        @rtype: L{dict}
        """
        csvfile = open( fname )
#        dialect = csv.Sniffer().sniff( csvfile.read( 1024 ), delimiters = [':'] )
#        csvfile.seek( 0 )
#        reader = csv.reader( csvfile, dialect, delimiter=':' )
        reader = csv.reader( csvfile, delimiter=':' )
    
        needsListProcessing = False
        currentKey = ""
        for row in reader:
            if len(row) == 2:
                # found an entry of the form "<identifier> : <value>"
                if needsListProcessing:
                    needsListProcessing = False
                    aDict[currentKey] = MoselInitFileParser.parse_array_string( aDict[currentKey] )
    
                currentKey = row[0].strip()
                aDict[currentKey] = row[1].strip( " '," )
                
                needsListProcessing = False
                if aDict[currentKey].startswith( '[' ):
                    needsListProcessing = True
            else:
                aDict[currentKey] += " " + row[0].strip( " '," )
                
        if needsListProcessing:
            needsListProcessing = False
            aDict[currentKey] = MoselInitFileParser.parse_array_string( aDict[currentKey] )
            
        return aDict

    read_mosel_init_file = staticmethod( read_mosel_init_file )

    
class MoselInitFileParser:
    """
    A textual 'Mosel' style multi-dimensional
    array description, i.e., the information in
    a Mosel initialisation file appearing after
    the ':' separator, has the following format
    (in EBNF):
        - array_string [see L{gnw.mosel.MoselInitFileParser.parse_array_string}]
            - : '[' array_elements ']'
            - | EMPTY
        - array_elements [see L{gnw.mosel.MoselInitFileParser.parse_array_elements}]
            - : array_element_list
            - | terminal_element_list
        - array_element_list [see L{gnw.mosel.MoselInitFileParser.parse_array_element_list}]
            - : array_string
            - | array_string SEP_CHAR array_element_list
        - terminal_element_list [see L{gnw.mosel.MoselInitFileParser.parse_terminal_element_list}]
            - : terminal_element
            - | terminal_element SEP_CHAR terminal_element_list
        - terminal_element
            - : quoted__string
            - | un_quoted_string
        - quoted_string
            - : QUOTE_CHAR un_quoted_string_ex QUOTE_CHAR
        - un_quoted_string_ex
            - : [all printable characters except QUOTE_CHAR]+  
        - un_quoted_string
            - : [a-zA-Z0-9_-.]+
    """
    def parse_array_string(array_string,
                           strip_chars = " ,;",
                           split_char = " ",
                           array_start_delim_char = '[',
                           array_end_delim_char = ']'):
        """
        Entry point into the parsing tree of the
        'right-hand-side' (RHS) of a Mosel initialisation
        file entry (having the form "<identifier> : <array_string>".
        
        @param array_string: RHS of a Mosel initialisation
            file entry, which represents a list type
            of 1 or 2 dimensions of atomic/terminal values.
            i.e., a string of the form
            "[ <elem1> <elem2> ... <elemN> ]"
        @type array_string: L{str}
        
        @param strip_chars: characters that are stripped off the
            left and right side of atomic/terminal values.
        @type strip_chars: L{str}
        
        @param split_char: character used to separate atomic/terminal
            values.
        @type split_char: L{str} of length one
        
        @param array_start_delim_char: charactar used to represent the
            start delimiter of a (sub-)list/array
        @type array_start_delim_char: L{str}
         
        @param array_end_delim_char: charactar used to represent the
            end delimiter of a (sub-)list/array
        @type array_end_delim_char: L{str}
        
        @return: list representation of array string with
            its innermost values being strings
        @rtype: L{list} [of L{list}] of L{str}
        
        @raise ValueError: 
        """
        value = array_string.strip( strip_chars )
        if value.startswith( array_start_delim_char ) and value.endswith( array_end_delim_char ):
            return MoselInitFileParser.parse_array_elements(value[1:-1], strip_chars, split_char, array_start_delim_char, array_end_delim_char)
        elif len(value) == 0:
            return []
        else:
            raise ValueError, "parse_array_string: parse error at '%s'" % value
    
    parse_array_string = staticmethod( parse_array_string )


    def parse_array_elements(array_elements,
                             strip_chars,
                             split_char,
                             array_start_delim_char,
                             array_end_delim_char):
        """
        Parse a list of elements with starting and ending
        list delimiter characters stripped.
        
        @param array_elements: represents an array_string with
            its left- and rightmost list delimiter characters
            stripped off, i.e., string of the form
            "<elem1> <elem2> ... <elemN>" 
        @type array_elements: L{str}

        @param strip_chars: characters that are stripped off the
            left and right side of atomic/terminal values.
        @type strip_chars: L{str}
        
        @param split_char: character used to separate atomic/terminal
            values.
        @type split_char: L{str} of length one
        
        @param array_start_delim_char: charactar used to represent the
            start delimiter of a (sub-)list/array
        @type array_start_delim_char: L{str}
         
        @param array_end_delim_char: charactar used to represent the
            end delimiter of a (sub-)list/array
        @type array_end_delim_char: L{str}
        
        @return: list representation of array string with
            its innermost values being strings
        @rtype: L{list} [of L{list}] of L{str}
        """
        value = array_elements.strip( strip_chars )
        if value.startswith( array_start_delim_char ) and value.endswith( array_end_delim_char ):
            return MoselInitFileParser.parse_array_element_list( value, strip_chars, split_char, array_start_delim_char, array_end_delim_char )
        else:
            return MoselInitFileParser.parse_terminal_element_list( value, strip_chars, split_char, array_start_delim_char, array_end_delim_char )
        
    parse_array_elements = staticmethod( parse_array_elements )

    
    def parse_array_element_list(element_list,
                                 strip_chars,
                                 split_char,
                                 array_start_delim_char,
                                 array_end_delim_char):
        """
        Parse list of elements with elements representing
        lists themselves.
        
        @param element_list: string representation of a
            list of lists with its outermost list delimiters
            stripped off, i.e., string of the form
            "[...] [...] ... [...]"
        @type element_list: L{str}
        
        @param strip_chars: characters that are stripped off the
            left and right side of atomic/terminal values.
        @type strip_chars: L{str}
        
        @param split_char: character used to separate atomic/terminal
            values.
        @type split_char: L{str} of length one
        
        @param array_start_delim_char: charactar used to represent the
            start delimiter of a (sub-)list/array
        @type array_start_delim_char: L{str}
         
        @param array_end_delim_char: charactar used to represent the
            end delimiter of a (sub-)list/array
        @type array_end_delim_char: L{str}
        
        @return: list representation of array string with
            its innermost values being strings
        @rtype: L{list} [of L{list}] of L{str}
        """
        theList = []
        value = element_list.strip( strip_chars )
        s = 0
        while s < len( value ):
            s = value.find( array_start_delim_char, s )
            if s == -1:
                break
            e = value.find( array_end_delim_char, s )
            if e == -1:
                break
            theList.append( MoselInitFileParser.parse_array_string( value[s:e+1], strip_chars, split_char, array_start_delim_char, array_end_delim_char ) )
            s = e + 1 
    
        return theList
    
    parse_array_element_list = staticmethod( parse_array_element_list )

    
    def parse_terminal_element_list(element_list,
                                    strip_chars,
                                    split_char,
                                    array_start_delim_char,
                                    array_end_delim_char):
        """
        Parse list of elements with elements representing
        atomic/terminal symbols, i.e., not lists.
        
        @param element_list: string representation of a
            list of terminal symbols with its outermost list delimiters
            stripped off, i.e., string of the form
            "<val1> <val2> ... <valN>"
        @type element_list: L{str}
        
        @param strip_chars: characters that are stripped off the
            left and right side of atomic/terminal values.
        @type strip_chars: L{str}
        
        @param split_char: character used to separate atomic/terminal
            values.
        @type split_char: L{str} of length one
        
        @param array_start_delim_char: charactar used to represent the
            start delimiter of a (sub-)list/array
        @type array_start_delim_char: L{str}
         
        @param array_end_delim_char: charactar used to represent the
            end delimiter of a (sub-)list/array
        @type array_end_delim_char: L{str}
        
        @return: list representation of array string with
            its innermost values being strings
        @rtype: L{list} of L{str}
        """
        value = element_list.strip( strip_chars )
        theList = value.split( split_char )
        for i in xrange( len( theList ) ):
            theList[i] = theList[i].strip( strip_chars )
        return theList

    parse_terminal_element_list = staticmethod( parse_terminal_element_list )


    
if __name__ == "__main__":
    print "gnw.mosel.py"

# ==============================================================================
#
#   Revision Control:
#
#   $Revision:: 1860                    $   Revision of last commit
#   $Author:: re04179                   $   Author of last commit
#   $Date:: 2009-09-07 14:09:18 +0200 (#$   Date of last commit
#
# ==============================================================================
