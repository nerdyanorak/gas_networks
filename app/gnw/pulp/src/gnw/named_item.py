# ==============================================================================
#
#   package         :   GasNetWorks (gnw) Python/pulp fuelled LP/MIP modeller 
#   author          :   Marc Roth (re04179)
#   version         :   $Id: named_item.py 1860 2009-09-07 12:09:18Z re04179 $
#   heading         :   $HeadURL: http://subversion.rwe.com/svn/s_and_v_projects/GasNetworks/trunk/app/gnw/pulp/src/gnw/named_item.py $
#
#   Description     :   COM interface sub-package
#
#   Creation Date   :   12Mar2009
#
#   Copyright       :   RWE Supply and Trading GmbH
#
# ==============================================================================
"""
gnw.com: NamedItem, NamedItemAttr, NamedItemData classes to store
data converted from named item (NI) tuples using L{gnw.com.NamedItemParser}. 
"""
from gnw.util import conditional

ni_type_str = 'str'
ni_type_int = 'int'
ni_type_float = 'float'
ni_type_bool = 'bool'
ni_type_named_item = 'NI'
ni_valid_type_list = [ ni_type_str, ni_type_int, ni_type_float, ni_type_bool, ni_type_named_item ]
    
# Forward declarations
class NamedItemAttr:
    pass
class NamedItemData:
    pass


class NamedItem:
    """
    Top level named item class.
    """
    def __init__(self, key = None, attr = NamedItemAttr(), data = NamedItemData()):
        self.key = key
        self.attr = attr
        self.data = data


    def __str__(self):
        return "key=%s,\n\t%s,\n\t%s" % (str(self.key),self.attr.__str__(),self.data.__str__())
    

    def get_dict(self):
        dict_rep = {}
        dict_rep.update( self.get_dict_item() )
        return dict_rep
        
        
    def get_key(self):
        return self.key


    def get_value(self):
        return self.data.value

    
    def get_dict_item(self):
        """
        @raise ValueError:
        """
        dict_rep = {}
        ni_flag = False
        if self.attr.dims == 0:
            if self.attr.types == ni_type_named_item:
                dict_rep.update( [[self.get_key(), self.data.value.get_dict()]] )
                
        elif self.attr.dims == 1:
            if len( self.attr.types ) == 1 and self.attr.sizes[0] > 1:
                types = self.attr.types[:1]*self.attr.sizes[0]
            else:
                types = self.attr.types
             
            for i in xrange( self.attr.sizes[0] ):
                if types[i] == ni_type_named_item:
                    ni_flag = True
                    dict_rep.update( self.data.value[i].get_dict() )
                    
        elif self.attr.dims == 2:
            if len( self.attr.types ) == 1 and self.attr.sizes[0] > 1:
                types = self.attr.types[:1]*self.attr.sizes[0]
            else:
                types = self.attr.types
                
            for i in xrange( self.attr.sizes[0] ):
                if len( types[i] ) == 1 and self.attr.sizes[1] > 1:
                    types_i = types[i][:1]*self.attr.sizes[1]
                else:
                    types_i = types[i]
                    
                for j in xrange( self.attr.sizes[1] ):
                    if types_i[j] == ni_type_named_item:
                        ni_flag = True
                        dict_rep.update( self.data.value[i][j].get_dict() )

        else:
            raise ValueError, "Invalid 'dims' value %d encountered" % self.attr.dims

        if ni_flag:
            return {self.get_key() : dict_rep}
        else:
            return {self.get_key() : self.get_value()}
    

    def get_named_item_tuple(self):
        """
        @raise ValueError:
        """
        ni_tuple = ['key', self.key,
                    'attr', self.attr.get_named_item_attr_tuple(),
                    'data', self.data.get_named_item_data_tuple( self.attr )]
        return ni_tuple

    
class NamedItemAttr:
    """
    Class to hold information corresponding to
    the 'attr' part of a named item (NI) tuple.
    """
    def __init__(self, dims = None, sizes = None, types = None):
        self.dims = dims
        self.sizes = sizes
        self.types = types


    def __str__(self):
        return "dims=%s, sizes=%s, types=%s" % (str(self.dims),str(self.sizes),str(self.types))


    def get_named_item_attr_tuple(self):
        return ['dims', self.dims,
                'sizes', self.sizes,
                'types', self.types]
        
    
class NamedItemData:
    """
    Class to hold information corresponding to
    he <data_attr> part of a named item (NI) tuple.
    """
    def __init__(self, value = None):
        self.value = value


    def __str__(self):
        return "data=%s" % self.value.__str__()
    

    def get_named_item_data_tuple(self, attr):
        if not isinstance( attr, NamedItemAttr ):
            raise TypeError, "parameter 'attr' type 'gnw.com.NamedItemAttr' expected"
        
        data = None
        if attr.dims == 0:
            if attr.types == ni_type_named_item:
                data = self.value.get_named_item_tuple()
            else:
                data = self.value
        
        elif attr.dims == 1:
            types = attr.types
            size = attr.sizes[0]
            if len( types ) == 1 and size > 1:
                types = types[:1]*size
        
            data = []
            for i in xrange( size ):
                if types[i] == ni_type_named_item:
                    data.append( self.value[i].get_named_item_tuple() )
                else:
                    data.append( self.value[i] )
        
        elif attr.dims == 2:
            types = attr.types
            for i in xrange( len( types ) ):
                if len( types[i] ) == 1 and attr.sizes[1] > 1:
                    types[i] = types[i][:1]*attr.sizes[1]
            if len( types ) == 1 and attr.sizes[0] > 1:
                types = types[:1]*attr.sizes[0]

            data = []
            for i in xrange( attr.sizes[0] ):
                sub_data = []
                for j in xrange( attr.sizes[1] ):
                    if types[i][j] == ni_type_named_item:
                        sub_data.append( self.value[i][j].get_named_item_tuple() )
                    else:
                        sub_data.append( self.value[i][j] )
                        
                data.append( sub_data )
                
        return data

        
if __name__ == "__main__":
    print "gnw.named_item.py"

# ==============================================================================
#
#   Revision Control:
#
#   $Revision:: 1860                    $   Revision of last commit
#   $Author:: re04179                   $   Author of last commit
#   $Date:: 2009-09-07 14:09:18 +0200 (#$   Date of last commit
#
# ==============================================================================
