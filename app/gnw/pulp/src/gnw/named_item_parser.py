# ==============================================================================
#
#   package         :   GasNetWorks (gnw) Python/pulp fuelled LP/MIP modeller 
#   author          :   Marc Roth (re04179)
#   version         :   $Id: named_item_parser.py 2138 2009-09-22 12:02:19Z re04179 $
#   heading         :   $HeadURL: http://subversion.rwe.com/svn/s_and_v_projects/GasNetworks/trunk/app/gnw/pulp/src/gnw/named_item_parser.py $
#
#   Description     :   COM interface sub-package
#
#   Creation Date   :   12Mar2009
#
#   Copyright       :   RWE Supply and Trading GmbH
#
# ==============================================================================
"""
gnw: Parser classes for parsing data passed in form of
named item (NI) tuples. 
"""
from gnw.util import isstring, isint, isfloat, isnumeric, issequence
from gnw.util import conditional

from gnw.named_item import NamedItem, NamedItemAttr, NamedItemData
from gnw.named_item import ni_type_str, ni_type_int, ni_type_float, ni_type_bool, ni_type_named_item
from gnw.named_item import ni_valid_type_list


class NamedItemParser:
    """
    Clients of the COM interface of gnw will pass
    data using, potentially empty, tuples of named items (NI).
    NIs are themselves tuples that provide the features of a
    simplified Variant (as known in VB[A]), a dictionary
    (as known in Python) or Collection (as known in VB[A]).
    The role of this module is to transform such NIs into
    equivalent objects of type L{gnw.com.NamedItem}.
    There are two formats of such NIs that are accepted:
        - long format (keywords included)
        - short format (keywords omitted)
    
    Long NI format:
        - (
            - u'key', u<key_attr>,
            - u'attr', (
                - u'dims', <dims_attr>,
                - u'sizes', <sizes_attr>,
                - u'types', <types_attr>
            - )
            - u'data', <data_attr>
        - )
    Short NI format:
        - (
            - u<key_attr>,
            - (
                - <dims_attr>,
                - <sizes_attr>,
                - <types_attr>
            - )
            - <data_attr>
        - )
        
    where
        - <dims_attr> is a value of type L{int} and
        can currently take on the following values:
            - 0: 0-dimensional array (i.e., data in <data_attr>
            is atomic (scalar) of type <types_attr>)
            - 1: 1-dimensional array (i.e., data in <data_attr>
            is a tuple of size <sizes_attr>[0] of atomic items
            of types as specified in <types_attr>)
            - 2: 2-dimensional array (i.e., data in <data_attr>
            is a
            tuple of size <sizes_attr>[0] of
            tuples of size <sizes_attr>[1] of
            atomic items of types as specified in <types_attr>)
        - <size_tuple> is a
            - empty tuple, if <dims_attr> == 0,
            - tuple of size 1 holding the number of atomic
            elements in <data_attr>, if <dims_attr> == 1,
            - tuple of size 2 holding the number of
            'rows' and 'columns', respectively, of 
            atomic elements in <data_attr>, if <dims_attr> == 2
        - <types_attr> provides information on the data types
        for the atomic items held in <data_attr>. The interpretation
        of <types_attr> depends on the value of the <dims_attr> as
        well as whether the data is homogenous or not.
        <types_attr> is
            - a L{str} specifying the type of the atomic item in
            <data_attr>, if <dims_attr> == 0,
            - a tuple of size 1 or size <sizes_attr>[0] of type
            specification strings for the atomic items in
            <data_attr>, if <dims_attr> == 1. If the tuple size
            is 1 then all atomic items in <data_attr> are 
            of given type, otherwise each atomic item corresponds
            to the type given in the <types_attr> tuple.
            - a tuple of tuples holding the type strings
            for the elements in <data_attr>. The 'outer' tuple
            has size 1 (homogenous column data in <data_attr>)
            or size <sizes_attr>[0] (each row has got its
            own type tuple for the row elements in <data_attr>).
            The 'inner' tuples have all either size 1 (homogenous
            row data in <data_attr>) or size <sizes_attr>[1]
            (each row element has got its own type specification).
        - <data_attr> holds the actual data which has to be
        interpreted depending of the value of <dims_attr> and
        <sizes_attr>:
            - the atomic item corresponds to the type
            given in <types_attr> if <dims_attr> == 0,
            - the atomic items in the tuple of size
            <sizes_attr>[0] correspond to the types in
            <types_attr>, if <dims_attr> == 1,
            - the atomic items in the tuple of
            size <sizes_attr>[0] of tuples of size <sizes_attr>[1],
            correspond to the types in <types_attr>,
            if <dims_attr> == 2.
            
    Admissible type strings for for the <types_attr> are:
        - 'str': string type
        - 'int': integral numeric type
        - 'float': floating point numeric type
        - 'bool': boolean numeric type
        - 'NI': named item (i.e., recursive data structure)
    """
    def parse(niTuple, shortForm=False):
        """
        @param niTuple: is a tuple of the form
            - (
                - u'key', u<key_attr>,
                - u'attr', (
                    - u'dims', <dims_attr>,
                    - u'sizes', <sizes_attr>,
                    - u'types', <types_attr>
                - )
                - u'data', <data_attr>
            - )
        or
            - (
                - u<key_attr>,
                - (
                    - <dims_attr>,
                    - <sizes_attr>,
                    - <types_attr>
                - )
                - <data_attr>
            - )
        @type niTuple: named item L{tuple}
        
        @param shortForm: optional flag indicating whether
            niTuple input is in alternative shorter
            form (i.e., without keywords), or not
        @type shortForm: L{bool} [default=False]
         
        @return: an initialised object instance
        @rtype: L{gnw.com.NamedItem}
        
        @raise TypeError: 
        @raise IndexError:
        @raise ValueError:  
        """
        if shortForm:
            tupleLen = 3
            keyDataIdx = 0
            attrDataIdx = 1
            dataDataIdx = 2
        else:
            tupleLen = 2*3
            keyDataIdx = 1
            attrDataIdx = 3
            dataDataIdx = 5
            
        if not issequence( niTuple ):
            raise TypeError, "parameter 'niTuple' is not a tuple"
        if len( niTuple ) != tupleLen:
            raise IndexError, "parameter 'niTuple' is not a tuple holding NamedItem information. Needs %d elements. Got %d element(s)" % (tupleLen, len( niTuple ))
     
        if not shortForm:
            if not isstring( niTuple[0] ) \
            or not isstring( niTuple[2] ) \
            or not isstring( niTuple[4] ):
                raise TypeError, "parameter 'niTuple' is not a tuple holding NamedItem information. Elements at position %d, %d, and %d must be of type 'str' or 'unicode'" % (0, 2, 4)

            if str( niTuple[0] ) != 'key' \
            or str( niTuple[2] ) != 'attr' \
            or str( niTuple[4] ) != 'data':
                raise ValueError, "parameter 'niTuple' is not a tuple holding NamedItem information. Needs keywords 'key', 'attr', and 'data' in positions %d, %d, and %d, respectively" % (0, 2, 4)
        
        if not isstring( niTuple[keyDataIdx] ):
            raise TypeError, "parameter 'niTuple' 'key' attribute is not of type 'str' or 'unicode' at position %d" % keyDataIdx
        
        ni = NamedItem()
        ni.key = str( niTuple[keyDataIdx] )
        ni.attr = NamedItemAttrParser.parse( niTuple[attrDataIdx] , shortForm )
        ni.data = NamedItemDataParser.parse( niTuple[dataDataIdx], ni.attr, shortForm )
        
        return ni

    parse = staticmethod( parse )
    
        
class NamedItemAttrParser:
    """
    Parses the 'attr' part of named item (NI) tuple.
    """
    def parse(niAttrTuple, shortForm=False):
        """
        @param niAttrTuple: is a tuple of the form
            - (
                - u'dims', <dims_attr>,
                - u'sizes', <sizes_attr>,
                - u'types', <types_attr>
            - )
        or
            - (
                - <dims_attr>,
                - <sizes_attr>,
                - <types_attr>
            - )
        @type niAttrTuple: L{tuple}
        
        @param shortForm: optional flag indicating whether
            niAttrTuple input is in alternative shorter
            form (i.e., without keywords), or not
        @type shortForm: L{bool} [default=False]
         
        @return: an initialised object instance
        @rtype: L{gnw.com.NamedItemAttr}

        @raise TypeError: 
        @raise IndexError:
        @raise ValueError:  
        """
        if shortForm:
            tupleLen = 3
            dimsDataIdx = 0
            sizesDataIdx = 1
            typesDataIdx = 2
        else:
            tupleLen = 2*3
            dimsDataIdx = 1
            sizesDataIdx = 3
            typesDataIdx = 5
            
        if not issequence( niAttrTuple ):
            raise TypeError, "parameter 'niAttrTyple' is not a tuple"
        if len( niAttrTuple ) != tupleLen:
            raise IndexError, "parameter 'niAttrTuple' is not a tuple holding NamedItemAttr information. Needs %d elements. Got %d element(s)" % (tupleLen, len( namedItemTuple ))

        if not shortForm:
            if not isstring( niAttrTuple[0] ) \
            or not isstring( niAttrTuple[2] ) \
            or not isstring( niAttrTuple[4] ):
                raise TypeError, "parameter 'niAttrTuple' is not a tuple holding NamedItemAttr information. Elements at position %d, %d, and %d must be of type 'str' or 'unicode'" % (0, 2, 4)
            
            if str( niAttrTuple[0] ) != 'dims' \
            or str( niAttrTuple[2] ) != 'sizes' \
            or str( niAttrTuple[4] ) != 'types':
                raise ValueError, "parameter 'niAttrTuple' is not a tuple holding NamedItemAttr information. Needs keywords 'dims', 'sizes', and 'types' in positions %d, %d, and %d, respectively" % (0, 2, 4)
        
        if not isint( niAttrTuple[dimsDataIdx] ):
            raise TypeError, "parameter 'niAttrTuple' 'dims' attribute is not of type 'int' at position %d" % dimsDataIdx

        nia = NamedItemAttr()
        nia.dims = niAttrTuple[dimsDataIdx]
        
        if not nia.dims in range( 3 ):
            raise ValueError, "parameter 'niAttrTuple' 'dims' attribute is out of range. Got %d" % nia.dims 
        
        nia.sizes = NamedItemAttrSizesParser.parse( niAttrTuple[sizesDataIdx], nia.dims, shortForm )
        nia.types = NamedItemAttrTypesParser.parse( niAttrTuple[typesDataIdx], nia.dims, nia.sizes, shortForm )
        
        return nia
    
    parse = staticmethod( parse )

    
class NamedItemDataParser:
    """
    Parses the 'data' part of a named item (NI) tuple.
    """
    def parse(niData, aNamedItemAttr = NamedItemAttr(), shortForm=False):
        """
        @param niData: a data object corresponding
            to the specifications as given in parameter
            L{aNamedItemAttr}. This may be an atomic
            data item, a tuple of atomic data items or
            a tuple of tuples of atomic data items.
        @type niData: L{tuple} or atomic item of
            type L{str}, L{int}, L{float}, L{bool}
            
        @param aNamedItemAttr: fully initialised named
            item attribute object instance
        @type aNamedItemAttr: L{gnw.com.NamedItemAttr}
        
        @param shortForm: optional flag indicating whether
            niTuple input is in alternative shorter
            form (i.e., without keywords), or not
        @type shortForm: L{bool} [default=False]
         
        @return: an initialised object instance
        @rtype: L{gnw.com.NamedItemData} 
        """
        dims = aNamedItemAttr.dims
        nid = NamedItemData()
        if dims == 0:
            nid.value = NamedItemData0dParser.parse( niData, aNamedItemAttr.types, shortForm )
        elif dims == 1:
            nid.value = NamedItemData1dParser.parse( niData, aNamedItemAttr.sizes, aNamedItemAttr.types, shortForm )
        elif dims == 2:
            nid.value = NamedItemData2dParser.parse( niData, aNamedItemAttr.sizes, aNamedItemAttr.types, shortForm )
        else:
            nid.value = []

        return nid
    
    parse = staticmethod( parse )
    

class NamedItemAttrSizesParser:
    """
    Parses the <sizes_attr> part of the 'attr' part
    of a named item (NI) tuple.
    """
    def parse(niAttrSizes, dims, shortForm=False):
        """
        @param niAttrSizes: <sizes_attr> part of
            the 'attr' part of a named item (NI)
            tuple.
        @type niAttrSizes: L{None} if parameter dims == 0,
            L{int} or ( L{int}, ) if parameter dims == 1,
            ( L{int}, L{int} ) if parameter dims == 2.
            
        @param shortForm: optional flag indicating whether
            input is in alternative shorter
            form (i.e., without keywords), or not.
            Currently without effect, but maintained
            for interface consistency with other
            named item parser classes.
        @type shortForm: L{bool} [default=False]
         
        @return: size specification
        @rtype: None, [L{int}], or [L{int},L{int}] depending
            on dims being 0, 1, or 2, respectively.
            
        @raise ValueError: 
        """
        if dims == 0:
            sizes = None
            
        elif dims == 1:
            if not isint( niAttrSizes ) \
            and not (issequence( niAttrSizes ) and len( niAttrSizes ) == 1):
                raise ValueError, "parameter 'niAttrSizes' has to be of type 'int' or a sequence holding one element of type 'int'"
            
            size =  conditional( isint( niAttrSizes ), niAttrSizes, niAttrSizes[0] )
            if size < 0:
                raise ValueError, "parameter 'niAttrSizes' holds negative size value (%d)" % size
                        
            sizes = [size]
                        
        elif dims == 2:
            if not (issequence( niAttrSizes ) and len( niAttrSizes ) == 2) \
            and not (isint( niAttrSizes[0] ) and isint( niAttrSizes[1] ) ):
                raise ValueError, "parameter 'niAttrSizes' has to be a sequence holding two elements of type 'int'"
            
            sizes = [niAttrSizes[0], niAttrSizes[1]]
            if sizes[0] < 0 or sizes[1] < 0:
                raise ValueError, "parameter 'niAttrSizes' holds negative size value (%d,%d)" % (sizes[0],sizes[1])
        
        return sizes

    parse = staticmethod( parse )


class NamedItemAttrTypesParser:
    """
    Parses <types_attr> part of 'attr' part of
    named item (NI) tuple.
    """
    def parse(niAttrTypes, dims, sizes, shortForm=False):
        """
        @param niAttrTypes: <types_attr> part of
            the 'attr' part of a named item (NI)
            tuple.
        @type niAttrTypes: valid type string if parameter dims == 0,
            sequence of valid type strings if parameter dims == 1,
            sequency of sequence of valid type strings if parameter dims == 2.
            
        @param shortForm: optional flag indicating whether
            input is in alternative shorter
            form (i.e., without keywords), or not.
            Currently without effect, but maintained
            for interface consistency with other
            named item parser classes.
        @type shortForm: L{bool} [default=False]
         
        @return: type specification
        @rtype: type string, list of type strings, or list of list of type strings
            depending on dims being 0, 1, or 2, respectively.
        
        @raise TypeError: 
        @raise ValueError:
        """
        if dims == 0:
            if not isstring( niAttrTypes ):
                raise TypeError, "parameter 'niAttrTypes' has to be of type 'str' or 'unicode' for dims = %d" % dims
        
            type = str( niAttrTypes )
            if not type in ni_valid_type_list:
                raise ValueError, "parameter 'niAttrTypes' encountered invalid type string '%s'" % type
             
            types = type
            
        elif dims == 1:
            if not issequence( niAttrTypes ):
                raise TypeError, "parameter 'niAttrTypes' has to be a sequence"
            
            if not ( len( niAttrTypes ) == 1 or len( niAttrTypes ) == sizes[0] ):
                raise ValueError, "parameter 'niAttrTypes' sequence has to be of len 1 or sizes[0]"
            
            types = []
            for type in niAttrTypes:
                if not isstring( type ):
                    raise TypeError, "parameter 'niAttrTypes' sequence element(s) have to be of type 'str' or 'unicode' for dims = %d" % dims
                
                type = str( type )
                if not type in ni_valid_type_list:
                    raise ValueError, "parameter 'niAttrTypes' encountered invalid type string '%s'" %  type
                
                types.append( type )
                
        elif dims == 2:
            if not issequence( niAttrTypes ):
                raise TypeError, "parameter 'niAttrTypes' has to be a sequence"
            
            if not ( len( niAttrTypes ) == 1 or len( niAttrTypes ) == sizes[0] ):
                raise ValueError, "parameter 'niAttrTypes' sequence has to be of len 1 or sizes[0]"

            types = []
            for i in xrange( len( niAttrTypes ) ):
                if not issequence( niAttrTypes[i] ):
                    raise TypeError, "parameter 'niAttrTypes' sub-element has to be sequence"
                
                if not ( len( niAttrTypes[i] ) == 1 or len( niAttrTypes[i] ) == sizes[1] ):
                    raise ValueError, "parameter 'niAttrTypes' sub-sequence has to be of len 1 or sizes[1]"

                types.append( NamedItemAttrTypesParser.parse( niAttrTypes[i], dims - 1, sizes[-1:], shortForm ) )

        return types

    parse = staticmethod( parse )


class NamedItemData0dParser:
    """
    Parses 0-dimensional <data_attr> part of
    a named item (NI) tuple.
    """
    def parse(niData, type, shortForm=False):
        """
        @param niData: <data_attr> part of named item (NI) tuple.
        @type niData: atomic data item if type string in <types_attr>
            is one of the valid types strings, except 'NI', or
            a named item (NI) tuple, otherwise.
            
        @param shortForm: optional flag indicating whether
            niData input is in alternative shorter
            form (i.e., without keywords), or not.
            Mainly used for recurvsive call to
            named item parser in case type of niData input
            is L{gnw.named_item.ni_type_named_item}
        @type shortForm: L{bool} [default=False]
         
        @return: parsed <data_attr> value
        @rtype: L{str}, L{int}, L{float}, L{bool} or {gnw.com.NamedItem}
        
        @raise TypeError: 
        """
        if type == ni_type_named_item:
            data = NamedItemParser.parse( niData, shortForm )
        elif niData == None:
            data = niData
        else:
            if type == ni_type_str and isstring( niData ):
                data = str( niData )
            elif type == ni_type_int and isnumeric( niData ):
                data = int( niData )
            elif type == ni_type_float and isnumeric( niData ):
                data = float( niData )
            elif type == ni_type_bool:
                data = bool( niData )
            else:
                raise TypeError, "parameter 'niData' invalid type or value ('%s',%s)" % (type,niData)
        
        return data 
        
    parse = staticmethod( parse )

        
class NamedItemData1dParser:
    """
    Parses 1-dimensional <data_attr> part of
    a named item (NI) tuple.
    """
    def parse(niData, sizes, types, shortForm=False):
        """
        @param niData: <data_attr> part of named item (NI) tuple.
        @type niData: one dimensional sequence type its values
            corresond to specifications given in parameters
            L{sizes} and L{types}.
            
        @param sizes: <sizes_attr> part of 'attr' part of given
            named item (NI) tuple.
        @type sizes: sequence of size 1 holding the length of
            1-dimenisional data given in parameter L{niData}.
            
        @param types: <types_attr> part of 'attr' part of given
            named item (NI) tuple.
        @type types: sequence of size 1 or size L{sizes}[0] holding
            the valid type strings.
            
        @param shortForm: optional flag indicating whether
            niData input is in alternative shorter
            form (i.e., without keywords), or not.
            Mainly used for recurvsive call to
            named item parser in case types of niData input
            is L{gnw.named_item.ni_type_named_item}
        @type shortForm: L{bool} [default=False]
         
        @return: 1-dimensional list of size L{sizes}[0] of
            values appropriately converted to types as given in
            parameter L{types}
        @rtype: L{list}
        
        @raise TypeError:
        @raise ValueError:  
        """
        data = None
        if sizes[0] > 0:
            size = sizes[0]
            if not issequence( niData ):
                raise TypeError, "parameter 'niData' has to be a sequence for dims = 1"
            if not len( niData ) == size:
                raise ValueError, "parameter 'niData' mismatch between size specification and actual len of sequence"
            
            if len( types ) == 1 and size > 1:
                types = types[:1]*size
                
            data = []
            for i in xrange( size ):
                data.append( NamedItemData0dParser.parse( niData[i], types[i], shortForm ) )
    
        return data
    
    parse = staticmethod( parse )

        
class NamedItemData2dParser:
    """
    Parses 2-dimensional <data_attr> part of
    a named item (NI) tuple.
    """
    def parse(niData, sizes, types, shortForm=False):
        """
        @param niData: <data_attr> part of named item (NI) tuple.
        @type niData: two dimensional sequence type its values
            corresond to specifications given in parameters
            L{sizes} and L{types}.
            
        @param sizes: <sizes_attr> part of 'attr' part of given
            named item (NI) tuple.
        @type sizes: sequence of size 2 holding the length for each
            dimension of 2-dimensional sequence given in
            parameter L{niData}.
            
        @param types: <types_attr> part of 'attr' part of given
            named item (NI) tuple.
        @type types: sequence of size 1 or size L{sizes}[0]
            of sequences of size 1 or size L{sizes}[1]
            holding the valid type strings.
            
        @param shortForm: optional flag indicating whether
            niData input is in alternative shorter
            form (i.e., without keywords), or not.
            Mainly used for recurvsive call to
            named item parser in case types of niData input
            is L{gnw.named_item.ni_type_named_item}
        @type shortForm: L{bool} [default=False]
         
        @return: 2-dimensional list of size L{sizes}[0] of
            lists of size L{sizes}[1] of
            values appropriately converted to types as given in
            parameter L{types}
        @rtype: L{list} of L{list}
        
        @raise TypeError:
        @raise ValueError:  
        """
        data = None
        if sizes[0] > 0:
            if not issequence( niData ):
                raise TypeError, "parameter 'niData' has to be a sequence for dims = 2"
            if not len( niData ) == sizes[0]:
                raise ValueError, "parameter 'niData' mismatch between size specification and actual len of data sequence"
            
            if len( types ) == 1 and sizes[0] > 1:
                types = types[:1]*sizes[0]
            
            data = []
            for i in xrange( sizes[0] ):
                data.append( NamedItemData1dParser.parse( niData[i], sizes[1:], types[i], shortForm ) )
        
        return data
    
    parse = staticmethod( parse )


if __name__ == "__main__":
    print "gnw.named_item_parser.py"

    niSplrTuple = \
        (\
            u'key', u'SPLR_DICT_LIST', u'attr',\
            (\
                u'dims',\
                1, u'sizes', (0,)\
                , u'types', (u'NI',)\
            )\
            , u'data', None\
        )    
    
    niTuples = \
        ((u'key', u'strg1', u'attr', (u'dims', 1, u'sizes', (5,), u'types', (u'str', u'str', u'str', u'int', u'int')), u'data', (u'a', u'b', u'c', 3, 5)),
         (u'key', u'tnr1_S_M0', u'attr', (u'dims', 1, u'sizes', (3,), u'types', (u'str',)), u'data', (u'x', u'y', u'z')),
         (u'key', u'key3', u'attr', (u'dims', 1, u'sizes', (4,), u'types', (u'float',)), u'data', (1.0, 2.0, 3.0, 4.0)),
         (u'key', u'key4', u'attr', (u'dims', 0, u'sizes', (), u'types', u'str'), u'data', u'Hello World'),
         (u'key', u'key5', u'attr', (u'dims', 2, u'sizes', (2, 3), u'types', ((u'int', u'int', u'float'),)), u'data', ((1, 2, 5.5), (3, 4, 5.5999999999999996))))

    niTuple = niTuples[4]
    
    ni = NamedItem()
    ni = NamedItemParser.parse( niTuple ) 
    ni = NamedItemParser.parse( niSplrTuple )
    
    from gnw.com.btsf_supplier_tuples import btsfSplrTuples
    ni = NamedItemParser.parse( btsfSplrTuples[0], True )
    
    print ni

# ==============================================================================
#
#   Revision Control:
#
#   $Revision:: 2138                    $   Revision of last commit
#   $Author:: re04179                   $   Author of last commit
#   $Date:: 2009-09-22 14:02:19 +0200 (#$   Date of last commit
#
# ==============================================================================
