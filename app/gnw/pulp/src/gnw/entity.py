# ==============================================================================
#
#   package         :   GasNetWorks (gnw) Python/pulp fuelled LP/MIP modeller 
#   author          :   Marc Roth (re04179)
#   version         :   $Id: entity.py 4064 2009-11-03 19:25:24Z re04179 $
#   heading         :   $HeadURL: http://subversion.rwe.com/svn/s_and_v_projects/GasNetworks/trunk/app/gnw/pulp/src/gnw/entity.py $
#
#   Description     :   Package file
#
#   Creation Date   :   06Mar2009
#
#   Copyright       :   RWE Supply and Trading GmbH
#
# ==============================================================================
"""
gnw: 'abstract' base class for GasNetWorks (gnw) entity classes. 
"""
import numpy
import pulp

from gnw.constraint import ConstraintCoeff

from gnw.util import conditional
from gnw.util import isint
from gnw.util import isnumeric
from gnw.util import issequence
from gnw.util import dbg_print

from gnw.named_item import NamedItem, NamedItemAttr, NamedItemData
from gnw.named_item import ni_type_float


class Entity( object ):
    """
    Abstract base class for all GasNetWorks (gnw) entity classes.
    
    @ivar name: unique entity identifier
    @type name: L{str}
    
    @ivar fmt_dict: format dictionary used to hold information for
        dumping class object information to L{file} object.
    @type fmt_dict: L{dict} having keys of type L{str} and values
        of type L{gnw.entity.FmtDictEntry}.
        
    @cvar sfmt: format string used in print statements for printing
        values of type L{str}.
    @type sfmt: L{str}.
    
    @cvar ifmt: format string used in print statements for printing
        values of type L{int}.
    @type ifmt: L{str}.
    
    @cvar ffmt: format string used in print statements for printing
        values of type L{float}.
    @type ffmt: L{str}.
    
    @cvar constraintTypeMask: mask representing the union of
        all constraint types applicable to given entity. This
        class variable is set by (direct or indirect) sub-classes
        of self.
        See L{gnw.constraint.ConstraintCoeff.ConstraintType} for
        constraint type mask definitions.
    @type constraintTypeMask: L{int}   
     
    @ivar constraint_list: list of L{pulp.LpConstraint}
    @type constraint_list: L{list} of L{pulp.LpConstraint}
    
    @ivar objective_list: list of L{pulp.LpAffineExpression}
    @type objective_list: L{list} of L{pulp.LpAffineExpression}
    
    @ivar DISPATCH_PERIOD: array holding the dispatch periods
        in hours [h]. The individual dispatch periods need not
        to be of the same length, allowing for higher
        granularity of dispatch decisions for the short term
        (1 to 2 years) and a lower granularity in the long
        term. This array defines the optimisation horizon.
    @type DISPATCH_PERIOD: L{numpy.array} of positive L{float}
        elements (using dtype='double').
    """
    sfmt="%-s"
    ffmt="%.8f"
    ifmt="%0d"
    constraintTypeMask = 0


    def __init__(self, name):
        """
        Sets unique entity identifier and initialises instance
        variables to required types.
        
        @param name: unique entity identifier
        @type name: L{str}  
        """
        self.set_name( name )
        
        self.constraint_list = []
        self.objective_list = []

        self.CONSTRAINT_COEFF = numpy.empty( 0, dtype='object' )
        self.DISPATCH_PERIOD = numpy.empty( 0, dtype='double' )

        self.fmt_dict = dict()

        
    def create_coefficient_array(member_array, size, message, dtype='double'):
        """
        Defines a static class method used to initialise
        coefficient arrays. Used by child classes of
        class L{gnw.entity.Entity}.
        
        @param member_array: reference to a class' coefficient
            array. After successful execution of this method
            the type of the referenced member_array variable
            will be L{numpy.array} of type dtype. If
            a list or a array is passed the expected length
            must match the length of L{size}.
            If member_array is only a atomic variable (i.e.,
            issequence(member_array) = False)
            then member_array is initialised to an array of
            len( L{size} ) holding that value in each element.
        @type member_array: L{list} of L{float},
            L{numpy.array} of dtype='double', or a simple numeric
            variable.
        
        @param size: required size of L{member_array} array
        @type size: L{int}
        
        @param message: message that should be thrown if
            inconsistent input is encountered.
        @type message: L{str}
        
        @return: appropriately modified input parameter
            L{member_array}.
        @rtype: L{numpy.array} of dtype='double' and length L{size}
        
        @raise TypeError:  
        """
        if isinstance( member_array, numpy.ndarray ):
            if len( member_array ) != size:
                raise TypeError, message
        elif isinstance( member_array, list ):
            if len( member_array ) != size:
                raise TypeError, message
            else:
                member_array = numpy.array( member_array, dtype=dtype )
        elif isnumeric( member_array ):
            member_array = numpy.array( [member_array]*size, dtype=dtype )
        else:
            raise TypeError, message

        return member_array
        
    create_coefficient_array = staticmethod( create_coefficient_array )

    
    def set_name(self, value):
        """
        Sets unique entity identifier. It is the responsibility of the
        client of the class to ensure that a unique identifier is used.
        
        @param value: unique entity identifier.
        @type value: non-empty L{str}
        
        @raise TypeError: 
        @raise ValueError:   
        """
        if not isinstance(value, str):
            raise TypeError, "Name of Entity object must be string"
        if len(value) == 0:
            raise ValueError, "Name of Entity object can not be empty string"
        self.name = value

    
    def set_CONSTRAINT_COEFF(self, value):
        """
        @param value: list of constraints.
        @type value: None or potentially empty
            list of lists of types [L{int},L{int},L{float},L{int},L{int}],
            representing dispatch period start index,
            dispatch period end index, bound, bound type
            and constraint type mask, respectively.
        
        @raise TypeError:
        @raise IndexError:  
        @raise ValueError: 
        """
        value = conditional( value is None, [], value )
        if not isinstance( value, list ):
            raise TypeError, "set_CONSTRAINT: list expected"
        m = len( value )
        for i in xrange( m ):
            if not issequence( value[i] ):
                raise TypeError, "set_CONSTRAINT: list of lists expected for element %d" % i
            n = len( value[i] ) 
            if n != 5:
                raise IndexError, "set_CONSTRAINT: list of lists of length 5 expected, got %d for element %d" % (n,i)
            if not isint( value[i][0] )\
            or not isint( value[i][1] )\
            or not isnumeric( value[i][2] )\
            or not isint( value[i][3] )\
            or not isint( value[i][4] ):
                raise TypeError, "set_CONSTRAINT: list of lists of length 5 expected of types [<int>,<int>,{<int>,<float>},<int>,<int>] for element %d" % i
            if value[i][0] < 0:
                raise ValueError, "set_CONSTRAINT: negative start index into DISPATCH_PERIOD array in CONSTRAINT[%d][0]" % i
            if value[i][1] < 0:  
                raise ValueError, "set_CONSTRAINT: negative final index into DISPATCH_PERIOD array in CONSTRAINT[%d][1]" % i
            if value[i][0] > value[i][1]:
                raise ValueError, "set_CONSTRAINT: CONSTRAINT[%d][0] > CONSTRAINT[%d][1]" % (i,i)
            if value[i][3] not in (ConstraintCoeff.BoundaryType.LB, ConstraintCoeff.BoundaryType.UB, ConstraintCoeff.BoundaryType.EQ ):
                raise ValueError, "set_CONSTRAINT: CONSTRAINT[%d][3] does not hold valid gnw.ConstraintCoeff.BoundaryTypeEnum value" % i
            if (value[i][4] & self.constraintTypeMask) != value[i][4]:
                raise ValueError, "set_CONSTRAINT: CONSTRAINT[%d][4] does hold an unsupported constraint type '%d' for object instance" % (i,value[i][4])

        self.CONSTRAINT_COEFF = numpy.array( [ConstraintCoeff( value[i][0], value[i][1], value[i][2], value[i][3], value[i][4] ) for i in xrange( m )] )
    

    def set_DISPATCH_PERIOD(self, value):
        """
        Set the dispatch period array. This method serves
        as a 'virtual' base class function. Child classes
        of L{gnw.entity.Entity} will most likely overwrite
        it.
                
        @param value: array or list holding the lengths of the individual
            dispatch periods in hours [h]. The time grid need not be uniform. 
        @type value: L{list} of L{float} or
            L{numpy.array} of dtype='double'
        """
        self.DISPATCH_PERIOD = conditional( value is None,
                                            numpy.empty( 0, dtype='double' ),
                                            numpy.array( value, dtype='double' ) )
        

    def create_lp_vars(self, prefix=""):
        """
        This method is used to initialise the lp variables and
        serves as a 'pure virtual' base class function. Child
        classes of L{gnw.entity.Entity} will most likely
        overwrite it.
        
        @param prefix: string used to additionally prefix the names of
            created lp variables.
        @type prefix: L{str} 
        """
        pass
        
    
    def create_model(self, prefix=""):
        """
        This method is used to initialise the lp model construction
        process and serves as a 'virtual' base class function. Child
        classes of L{gnw.entity.Entity} will most likely overwrite it.
        In order to guarantee that the lp model is initialised properly
        it is advisable that child classes call their super class
        create_model function first.
        
        @param prefix: string used to additionally prefix the names of
            created lp variables.
        @type prefix: L{str} 
        """
        self.constraint_list = []
        self.objective_list = []
                

    def get_lp_vars(self):
        """
        This method is used to return a list containing all
        lp variables and serves as a 'pure virtual' base class
        function. Child classes of L{gnw.entity.Entity} will
        most likely overwrite it.
        
        @return: list of lp variables
        @rtype: L{list} of L{pulp.LpVariable}
        """
        return []        
    

    def get_objective(self):
        """
        Returns objective function
        
        @return: objective function.
        @rtype: L{pulp.LpAffineExpression}
        """
#        dbg_print( self.name, True )
        objective = pulp.LpAffineExpression( constant = 0 )
        for item in self.objective_list:
            objective += item
            
        return objective


    def get_constraints(self):
        """
        Returns list of constraints
        
        @return: list of constraints
        @rtype: L{list} of L{pulp.LpConstraint}
        """
        return self.constraint_list
        
        
    def get_objective_value(self):
        """
        Returns affine expression representing
        the objective function
        
        @return: objective function expression.
        @rtype: L{pulp.LpAffineExpression}
        """
        return pulp.LpAffineExpression( constant = 0 )
    
    
    def get_mark_to_market_value(self):
        """
        Returns affine expression representing
        the mark to market function
        
        @return: mark to market function expression
        @rtype: L{pulp.LpAffineExpression}
        """
        return pulp.LpAffineExpression( constant = 0 )

 
    def write_results(self, rslt_dir, basename, extension="txt", canonical=False, sep=";", verbose=False, indent=0):
        """
        This method writes the class instance's information
        to file with path name
        rslt_dir + "/" + basename + "-" + self.name + "." + extension
        using the information contained in the
        class object's L{gnw.entity.Entity.fmt_dict} dictionary.
        See L{gnw.entity.FmtDictEntry} for information on
        the information contained in the L{gnw.entity.Entity.fmt_dict}.
        Child classes of L{gnw.entity.Entity} will most likely
        overwrite this method and set-up the L{gnw.entity.Entity.fmt_dict}
        dictionary with the appropriate information before calling
        their super class' write_results function, which will
        be responsible for the output of the provided information.

        @param rslt_dir: (relative or absolute) path to
            result directory location. Note directory must exist
            on file system
        @type rslt_dir: L{str}
        
        @param basename: base name of file name the results are
            written to.
        @type basename: L{str} conforming to the requirements
            of file names for given file system
            
        @param extension: filename extension
        @type extension: L{str} conforming to the requirements
             of file name extension for given file system

        @param canonical: not used
        @type canonical: L{bool}
        
        @param sep: separator character to be used between elements
            in the output written
        @type sep: L{str} (typically one of '\t', '\b', ';', ':', ',', etc.)
  
        @param verbose: whether progress messages are printed to the console
        @type verbose: L{bool}
        
        @param indent: indentation of progress messages in number of characters.
        @type indent: L{int}     
        
        @raise ValueError: 
        """
        fname = "%s/%s-%s.%s" % (rslt_dir, basename, self.name, extension)
        file = open( fname, "w" )
        if file.closed:
            raise ValueError, "write_results: closed file handle"

        dbg_print( "%s... entity '%s'" % (" "*indent, self.name), verbose )
        
        self.update_fmt_dict({})    # explicit empty initialisation of parameter
                                    # fmt_dict dictionary required here,
                                    # although default value for parameter is {}?! 
        nSteps = len( self.DISPATCH_PERIOD )
        nPoints = nSteps + 1

        key_cmp = lambda x, y : conditional( x[0] !=  y[0],
                                             conditional( x[0] < y[0], -1, 1 ),
                                             0 )

        fmt_dict_item_list = self.fmt_dict.items()
        fmt_dict_item_list.sort( cmp = key_cmp )
        
        for dim in xrange( 3 ):
            if dim == 0 and sum( [1 for k,v in fmt_dict_item_list if v.dim == dim] ) > 0:
                for k,v in fmt_dict_item_list:
                    if v.dim == dim:
                        print >> file, (self.sfmt + sep) % v.label,
                        if v.ref is not None:
                            if v.is_lp_var:
                                if v.ref.varValue is not None:
                                    print >> file, (v.fmt[0] + sep) % pulp.value(v.ref),
                                else:
                                    print >> file, (self.sfmt + sep) % "None",
                            else:
                                print >> file, (v.fmt[0] + sep) % v.ref,
                        else:
                            print >> file, (self.sfmt + sep) % "None",
                        print >> file
                         
            elif dim == 1 and sum( [1 for k,v in fmt_dict_item_list if v.dim == dim] ) > 0:
                # header line
                print >> file, (self.sfmt + sep) % "t",
                for k,v in fmt_dict_item_list:
                    if v.dim == dim:
                        print >> file, (self.sfmt + sep) % v.label,
                print >> file
                # values line
                done = False
                t = 0
                while (not done):
                    done = True
                    print >> file, (self.ifmt + sep) % t,
                    for k,v in fmt_dict_item_list:
                       if v.dim == dim:
                            num_rows = v.dim_sizes[0]
                            if t < num_rows:
                                done = False
                                if v.ref[t] is not None: 
                                    if v.is_lp_var:
                                        if v.ref[t].varValue is not None:
                                            print >> file, (v.fmt[0] + sep) % pulp.value(v.ref[t]),
                                        else:
                                            print >> file, (self.sfmt + sep) % "None",
                                    else:
                                        print >> file, (v.fmt[0] + sep) % v.ref[t],
                                else:
                                    print >> file, (self.sfmt + sep) % "None",
                            else:
                                print >> file, (self.sfmt + sep) % "N/A",
                    print >> file
                    t += 1
                    
            elif dim == 2 and sum( [1 for k,v in fmt_dict_item_list if v.dim == dim] ) > 0:
                # header line
                print >> file, (self.sfmt + sep) % "i",
                for k,v in fmt_dict_item_list:
                    if v.dim == dim:
                        num_cols = v.dim_sizes[1]
                        # repeat label num_cols time
                        for j in xrange( num_cols ):
                            print >> file, (self.sfmt + sep) % (v.label % j),
                print >> file
                #values line
                done = False
                i = 0
                while (not done):
                    done = True
                    print >> file, (self.ifmt + sep) % i,
                    for k,v in fmt_dict_item_list:
                        if v.dim == dim:
                            num_rows = v.dim_sizes[0]
                            num_cols = v.dim_sizes[1]
                            if i < num_rows:
                                done = False
                                for j in xrange( num_cols ):
                                    if v.ref[i,j] is not None:
                                        if v.is_lp_var:
                                            if v.ref[i,j].varValue is not None:
                                                print >> file, (v.fmt[j] + sep) % pulp.value(v.ref[i,j]),
                                            else:
                                                print >> file, (self.sfmt + sep) % "None",
                                        else:
                                            print >> file, (v.fmt[j] + sep) % v.ref[i,j],
                                    else:
                                        print >> file, (self.sfmt + sep) % "None",
                            else:
                                for j in xrange( num_cols ):
                                    print >> file, (self.sfmt + sep) % "N/A",
                    print >> file
                    i += 1
                    
        file.flush()
        file.close()


    def get_keys(self):
        """
        Returns a list of L{gnw.entity.Entity.fmt_dict}'s keys.
        
        @return: list of keys
        @rtype: list of L{str}
        """
        self.update_fmt_dict() 
        return self.fmt_dict.keys()


    def get_lp_var_values(self, key_list=[]):
        """
        Returns a L{gnw.named_item.NamedItem} class instance
        encapsulating values of all decision variables
        for given L{gnw.entity.Entity} class instance (or any
        of its sub-classes) by retrieving the
        appropriate information from the L{gnw.entity.Entity.fmt_dict}.

        @param key_list: optional list holding the keys into the
            internal L{gnw.entity.Entity.fmt_dict} dictionary.
            If key_list is empty then all instance's decision variables
            values are in the return value, otherwise only
            the decision variables with keys in key_list are in the
            return value. Strings in key_list that are not keys of
            decision variables or are not proper keys are ignored.
        @type key_list: List of {str}

        @return: A L{gnw.named_item.NamedItem} class instance holding
            a one-dimensional array of L{gnw.named_item.NamedItem}
            elements, etc.
        @rtype: L{gnw.named_item.NamedItem}
        """
        self.update_fmt_dict()
        named_item_list = []
        for k,v in self.fmt_dict.iteritems():
            if v.ref is not None and v.is_lp_var:

                if len( key_list ) and k not in key_list:
                    continue

                if v.dim == 0:
                    
                    attr = NamedItemAttr( v.dim, v.dim_sizes, ni_type_float )
                    data = NamedItemData( v.ref.varValue )

                elif v.dim == 1:

                    attr = NamedItemAttr( v.dim, v.dim_sizes, [ni_type_float] )
                    data = NamedItemData( [v.ref[t].varValue for t in xrange( v.dim_sizes[0] )] )

                elif v.dim == 2:

                    attr = NamedItemAttr( v.dim, v.dim_sizes, [[ni_type_float]] )
                    data = NamedItemData( [[v.ref[i,j].varValue for j in xrange( v.dim_sizes[1] )] for i in xrange( v.dim_sizes[0] )] )

                named_item_list.append( NamedItem( k, attr, data ) )

        return named_item_list


    def update_fmt_dict(self, fmt_dict={}):
        """
        Called once by any instance of L{gnw.entity.Entity}
        (or any of its sub-classes) before calling
        either
        L{gnw.entity.Entity.write_results} or
        L{gnw.entity.Entity.get_lp_var_values}. This updates
        the internal format information dictionary
        L{gnw.entity.Entity.fmt_dict} with the values given
        in parameter L{fmt_dict}.
        
        @param fmt_dict: dictionary of keys of type
            L{str} and value of type L{gnw.entity.FmtDictEntry}
        @type fmt_dict: L{dict} 
        """
        nSteps = len( self.DISPATCH_PERIOD )
        self.fmt_dict.update({'DP' : FmtDictEntry( [ self.ffmt ], 'DP[t] [h]', 1, (nSteps,), False, self.DISPATCH_PERIOD )})
        
        nConstraints = len( self.CONSTRAINT_COEFF )
        if nConstraints > 0:
            self.fmt_dict.update({'CONSTRAINT_START' : FmtDictEntry( [ self.ifmt ], 'CONSTRAINT[i].START', 1, (nConstraints,), False, [self.CONSTRAINT_COEFF[i].START for i in xrange( nConstraints )] ),
                                  'CONSTRAINT_FINAL' : FmtDictEntry( [ self.ifmt ], 'CONSTRAINT[i].FINAL', 1, (nConstraints,), False, [self.CONSTRAINT_COEFF[i].FINAL for i in xrange( nConstraints )] ),
                                  'CONSTRAINT_BOUND' : FmtDictEntry( [ self.ffmt ], 'CONSTRAINT[i].BOUND', 1, (nConstraints,), False, [self.CONSTRAINT_COEFF[i].BOUND for i in xrange( nConstraints )] ),
                                  'CONSTRAINT_BTYPE' : FmtDictEntry( [ self.ifmt ], 'CONSTRAINT[i].BTYPE', 1, (nConstraints,), False, [self.CONSTRAINT_COEFF[i].BTYPE for i in xrange( nConstraints )] ),
                                  'CONSTRAINT_CTYPE' : FmtDictEntry( [ self.ifmt ], 'CONSTRAINT[i].CTYPE', 1, (nConstraints,), False, [self.CONSTRAINT_COEFF[i].CTYPE for i in xrange( nConstraints )] )})

        self.fmt_dict.update( fmt_dict )


    def get_results(self):
        """
        This method is used to return a list containing all
        lp variables in simple sequence type form
        and serves as a 'pure virtual' base class
        function. Child classes of L{gnw.entity.Entity} will
        most likely overwrite it.
        
        @return: list [of list [...]]
        @rtype: L{list}
        """
        pass



class FmtDictEntry( object ):
    """
    Helper class rather used as simple 'structure' for storing
    information on how to print L{gnw.entity.Entity} class' and
    sub-class' instance variables.
    See L{gnw.entity.Entity.write_results}
    and L{gnw.entity.Entity.fmt_dict} for more details.
    
    @ivar fmt: element format string. L{gnw.entity.Entity} provides
        three predefined format strings class object variables:
            - L{gnw.entity.Entity.sfmt}: string format string
            - L{gnw.entity.Entity.ifmt}: integer format string
            - L{gnw.entity.Entity.ffmt}: float format string
        If additional formatting requirements are needed, it is
        advisable to extend the set of format string variables in
        L{gnw.entity.Entity} rather than use explicit custom
        format strings in setting up objects of type
        L{gnw.entity.FmtDictEntry}.
    @type fmt: L{str}
    @ivar label: this entry's print label
    @type label:L{str}
    @ivar dim: dimensionality of data structure given in
        L{gnw.entity.FmtDictEntry.ref}. Currently only dimensions
        0, 1 or 2 are supported.
    @type dim: L{int}
    @ivar dim_sizes: the extensions in each dimension given
        in L{gnw.entity.FmtDictEntry.dim}:
            - L{gnw.entity.FmtDictEntry.dim}=0: L{gnw.entity.FmtDictEntry.dim_sizes}=None
            - L{gnw.entity.FmtDictEntry.dim}=1: L{gnw.entity.FmtDictEntry.dim_sizes}=(numRows,)
            - L{gnw.entity.FmtDictEntry.dim}=2: L{gnw.entity.FmtDictEntry.dim_sizes}=(numRows,numCols)
    @type dim_sizes: L{tuple} of size L{dim} holding number of rows and columns.
    @ivar is_lp_var: flag indicating whether data structure given in
        L{gnw.entity.FmtDictEntry.ref} holds elements of type L{pulp.LpVariable}
        or just basic problem coefficients.
    @type is_lp_var: L{bool}
    @ivar ref: reference to class member variable.
    @type ref: L{pulp.LpVariable} or basic problem coefficent (array)  
    """
    def __init__(self, fmt="", label="", dim=0, dim_sizes=None, is_lp_var=False, ref=None):
        """
        Initialising constructor. This class is rather used as
        a simple 'structure'. 

        @param fmt: element format string. L{gnw.entity.Entity} provides
            three predefined format strings class object variables:
                - L{gnw.entity.Entity.sfmt}: string format string
                - L{gnw.entity.Entity.ifmt}: integer format string
                - L{gnw.entity.Entity.ffmt}: float format string
            If additional formatting requirements are needed, it is
            advisable to extend the set of format string variables in
            L{gnw.entity.Entity} rather than use explicit custom
            format strings in setting up objects of type
            L{gnw.entity.FmtDictEntry}.
        @type fmt: L{str}
        @param label: this entry's print label
        @type label:L{str}
        @param dim: dimensionality of data structure given in
            L{gnw.entity.FmtDictEntry.ref}. Currently only dimensions
            0, 1 or 2 are supported.
        @type dim: L{int}
        @param dim_sizes: the extensions in each dimension given
            in L{gnw.entity.FmtDictEntry.dim}:
                - L{gnw.entity.FmtDictEntry.dim}=0: L{gnw.entity.FmtDictEntry.dim_sizes}=None
                - L{gnw.entity.FmtDictEntry.dim}=1: L{gnw.entity.FmtDictEntry.dim_sizes}=(numRows,)
                - L{gnw.entity.FmtDictEntry.dim}=2: L{gnw.entity.FmtDictEntry.dim_sizes}=(numRows,numCols)
        @type dim_sizes: L{tuple} of size L{dim} holding number of rows and columns.
        @param is_lp_var: flag indicating whether data structure given in
            L{gnw.entity.FmtDictEntry.ref} holds elements of type L{pulp.LpVariable}
            or just basic problem coefficients.
        @type is_lp_var: L{bool}
        @param ref: reference to class member variable.
        @type ref: L{pulp.LpVariable} or basic problem coefficent (array)  
        """
        self.fmt = fmt
        self.label = label
        self.dim = dim
        self.dim_sizes = dim_sizes
        self.is_lp_var = is_lp_var
        self.ref = ref



if __name__ == "__main__":
    print "gnw.entity.py"

# ==============================================================================
#
#   Revision Control:
#
#   $Revision:: 4064                    $   Revision of last commit
#   $Author:: re04179                   $   Author of last commit
#   $Date:: 2009-11-03 20:25:24 +0100 (#$   Date of last commit
#
# ==============================================================================
