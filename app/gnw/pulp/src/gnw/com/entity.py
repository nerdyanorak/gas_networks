# ==============================================================================
#
#   package         :   GasNetWorks (gnw) Python/pulp fuelled LP/MIP modeller 
#   author          :   Marc Roth (re04179)
#   version         :   $Id: entity.py 1860 2009-09-07 12:09:18Z re04179 $
#   heading         :   $HeadURL: http://subversion.rwe.com/svn/s_and_v_projects/GasNetworks/trunk/app/gnw/pulp/src/gnw/com/entity.py $
#
#   Description     :   COM interface sub-package
#
#   Creation Date   :   24Mar2009
#
#   Copyright       :   RWE Supply and Trading GmbH
#
# ==============================================================================
"""
gnw.com: provides base class for all COM classes that are
callable from VB[A] 
"""
import winerror

from win32com.server.exception import COMException

from gnw.named_item_parser import NamedItemParser 
from gnw.com.util import err_value
from gnw.util import issequence

from gnw.com import __debugging__


class COM_Entity( object ):
    """
    @ivar data_dict: dictionary holding the raw data
        to initialise the L{gnw} object instance.
        data_dict is set using method
        L{gnw.com.entity.COM_Entity.set_data}
    @type data_dict: L{dict}
    
    @ivar gnw: object reference to
        any of the available sub-classes of
        L{gnw.Entity}. gnw is set by sub-classes of
        L{gnw.com.entity.COM_Entity} by calling
        one of the set_all_data or set_data methods
        passing appropriate initialisation data
    @type gnw: L{gnw.Entity}
    
    @ivar dispatcher: although we are able to register
        our Parent object for debugging, our Child object
        is not registered, so this won't work. To get
        the debugging behaviour for our wrapped objects,
        we must do it ourself by setting the dispatcher
        to
        L{win32com.server.dispatcher.DefaultDebugDispatcher}.
        We control whether dispatcher is set to
        DefaultDebugDispatcher by the value of flag
        L{debugging}.
    @type dispatcher: None or
        L{win32com.server.dispatcher.DefaultDebugDispatcher}
        
    @ivar debugging: internal flag initialised to value
        L{gnw.com.__debugging__}. Triggers whether L{dispatcher}
        is set from None to a proper dispatcher object instance.
    @type debugging: any type that evaluates to True/False. 
    """
    def __init__(self):
        """
        Initialise object
        """
        self.data_dict = {}
        self.gnw = None

        debugging = __debugging__
        self.dispatcher = None
        if debugging:
            from win32com.server.dispatcher import DefaultDebugDispatcher
            self.dispatcher = DefaultDebugDispatcher
        
    
    def set_data(self, niTuples):
        """
        Set problem data. Scans each item in the L{niTuples}
        using L{gnw.named_item_parser.NamedItemParser} and
        appends result to a list of L{gnw.named_item.NamedItem}s.
        Each such named item element is then added to
        L{data_dict} by calling L{gnw.named_item.NamedItem.get_dict}
        method.
        
        @todo: routine set_data probably should be factored out
            or at least renamed to 'set_data_dict'
        
        @param niTuples: We expect this to be a, potentially
            empty, tuple of named item (NI) elements, that combine a
            simplified Variant (as known in VB[A]) with a dictionary
            (as known in Python) or Collection (as known in VB[A]).
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
                    is a tuple size <sizes_attr>[0] of atomic items
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
                interpreted depnding of the value of <dims_attr> and
                <sizes_attr>:
                    - the atomic item corresponds to the type
                    given in <types_attr> if <dims_attr> == 0,
                    - the atomic items in the tuple of size
                    <sizes_attr>[0] correspond to the types in
                    <types_attr>, if <dims_attr> == 1,
                    - the atomic itmes in the tuple of
                    size <sizes_attr>[0] of tuples of size <sizes_attr>[1],
                    correspond to the types in <types_attr>,
                    if <dims_attr> == 2.
            Admissible type strings for for the <types_attr> are:
                - 'str': string type
                - 'int': integral numeric type
                - 'float': floating point numeric type
                - 'bool': boolean numeric type
                - 'NI': named item (i.e., recursive data structure)
        @type niTuples: L{tuple} [of L{tuple}s [...]]
        
        @raise win32com.server.exception.COMException: 
        """
        try:
            named_item_list = []
            for item in niTuples:
                named_item_list.append( NamedItemParser.parse( item, str( item[0] ) != 'key' ) )
                
            self.data_dict = {}
            for item in named_item_list:
                self.data_dict.update( item.get_dict() )
                
        except ( TypeError, ValueError ):
            raise COMException( err_value(), winerror.DISP_E_TYPEMISMATCH )
        except ( IndexError, KeyError ):
            raise COMException( err_value(), winerror.DISP_E_BADINDEX )
        except:
            raise COMException( err_value(), winerror.DISP_E_EXCEPTION )


    def get_keys(self):
        """
        Returns a list of L{gnw.entity.Entity.fmt_dict}'s keys.
        
        @return: list of keys
        @rtype: list of L{str}
        """ 
        return self.gnw.get_keys()


    def get_lp_var_values(self, keys=[]):
        """
        Returns a list of named item (NI) elements holding
        the values of the object's LP variables.
        
        @param keys: optional list holding the keys into the
            internal L{gnw.entity.Entity.fmt_dict} dictionary.
            If key_list is empty then all instance's decision variables
            values are in the return value, otherwise only
            the decision variables with keys in keys are in the
            return value. Strings in keys that are not keys of
            decision variables or are not proper keys are ignored.
        @type keys: List of L{str}

        @return: a named item tuple holding the requested result
        @rtype: list in named item tuple format
            (see L{gnw.named_item.NamedItem})

        @raise win32com.server.exception.COMException:
        """ 
        try:
            if keys is None or not issequence( keys ):
                keys = []
                
            # convert from potential unicode strings
            key_list = [str( k ) for k in keys]    

            named_item_list = self.gnw.get_lp_var_values( key_list )
            named_item_tuple_list = []
            for named_item in named_item_list:
                named_item_tuple_list.append( named_item.get_named_item_tuple() )

            return named_item_tuple_list

        except ( TypeError, ValueError ):
            raise COMException( err_value(), winerror.DISP_E_TYPEMISMATCH )
        except ( IndexError, KeyError ):
            raise COMException( err_value(), winerror.DISP_E_BADINDEX )
        except:
            raise COMException( err_value(), winerror.DISP_E_EXCEPTION )



if __name__ == "__main__" :
    print "gnw.com.entity.py"

# ==============================================================================
#
#   Revision Control:
#
#   $Revision:: 1860                    $   Revision of last commit
#   $Author:: re04179                   $   Author of last commit
#   $Date:: 2009-09-07 14:09:18 +0200 (#$   Date of last commit
#
# ==============================================================================
