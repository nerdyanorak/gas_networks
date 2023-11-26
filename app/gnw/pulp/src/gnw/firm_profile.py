# ==============================================================================
#
#   package         :   GasNetWorks (gnw) Python/pulp fuelled LP/MIP modeller 
#   author          :   Marc Roth (re04179)
#   version         :   $Id: firm_profile.py 2138 2009-09-22 12:02:19Z re04179 $
#   heading         :   $HeadURL: http://subversion.rwe.com/svn/s_and_v_projects/GasNetworks/trunk/app/gnw/pulp/src/gnw/firm_profile.py $
#
#   Description     :   Package file
#
#   Creation Date   :   10Aug2009
#
#   Copyright       :   RWE Supply and Trading GmbH
#
# ==============================================================================
"""
gnw: provides firm delivery/supply profile abstraction 
"""
import numpy
import pulp

from gnw.entity import Entity, FmtDictEntry 

from gnw.util import isint
from gnw.util import conditional

from __init__ import __eSell__
from __init__ import __eBuy___


class FirmProfile( Entity ):
    """
    This class provides an abstraction of a
    firm delivery/supply (short/long) profile,
    that has to be covered by the network (by
    way of storage dispatch, supply
    contract dispatch, or market transaction).
    This class does not actually hold any
    decision variables for the LP but only
    constants that affect other entities held
    in the network during optimisation.
    
    @ivar SB: sell or buy indicator.
    @type SB: L{int} in {L{gnw.__eSell__}, L{gnw.__eBuy___}}

    @ivar CURRENT_POSITION: holds a position for each
        dispatch period, i.e., a basket of positions.
        If we buy (SB = -1) the firm profile then we are
        long a basket of {CURRENT_POSITION[t], t in range( len( DISPATCH_PERIOD ) )},
        i.e., we are long CURRENT_POSITION[t], if CURRENT_POSITION[t] > 0,
        short otherwise.
        If we sell (SB = 1) the firm profile then we are
        short a basket of of {CURRENT_POSITION[t], t in range( len( DISPATCH_PERIOD ) )},
        i.e., we are short CURRENT_POSITION[t], if CURRENT_POSITION[t] > 0,
        long otherwise.
        This means that if -self.SB*self.CURRENT_POSITION > 0 we are long,
        short or flat otherwise
    @type CURRENT_POSITION: L{numpy.array} of dtype='double'
        of length len(L{DISPATCH_PERIOD})
    
    @ivar DISCOUNT_FACTOR: dispatch period dependent discount
        factor.
    @type DISCOUNT_FACTOR: L{numpy.array} of dtype='double'
        of length len(L{DISPATCH_PERIOD})

    @ivar vol: lp affine expression variables
        representing the volume
        in [MWh] of the firm profile during each
        L{DISPATCH_PERIOD}. They correspond to
        L{DISPATCH_PERIOD}[t]*L{CURRENT_POSITION}[t], 
        forall t in range(len(DISPATCH_PERIOD))
    @type vol: L{numpy.array} of dtype='object' of
        length len(L{DISPATCH_PERIOD}) of L{pulp.LpVariable}
    """
    def __init__(self, name,
                 sellbuy = __eSell__,
                 currentPosition = None,
                 discountFactor = None,
                 dispatchPeriod = None):
        """
        @param name: unique identifier such as 'Firm'
        @type name: L{str}

        @param sellbuy: sell or buy indicator
        @type sellbuy: L{int} in {L{gnw.__eSell__}, L{gnw.__eBuy___}},
            [default=__eSell__]
        
        @param currentPosition: holds a position for each
            dispatch period, i.e., a basket of positions.
            (see CURRENT_POSITION member variable for details)
        @type currentPosition: None, L{float}, L{list} of L{float}
            or L{numpy.array} of dtype='double' of length
            len(L{DISPATCH_PERIOD}), [default=0.0]
        
        @param discountFactor: dispatch period dependent
            discount factor.
        @type discountFactor: None, L{float}, L{list} of L{float}
            or L{numpy.array} of dtype='double' of length
            len(L{DISPATCH_PERIOD}), [default=1.0]
        
        @param dispatchPeriod: dispatch periods in hours [h] that
            do not need to be uniform. This array defines the
            optimisation period in total and the individual
            dispatch periods individually. If the
            dispatch period is not set during object construction
            it must be set later via call to 
            L{gnw.entity.Entity.set_DISPATCH_PERIOD}
        @type dispatchPeriod: None, L{list} of L{float}
            or L{numpy.array} of dtype='double'
        """
        super( FirmProfile, self ).__init__( name )
        
        self.set_SB( sellbuy )
        self.set_CURRENT_POSITION( currentPosition )
        self.set_DISCOUNT_FACTOR( discountFactor )
        self.set_DISPATCH_PERIOD( dispatchPeriod )
        
        self.vol = numpy.empty( 0, dtype='object' )

        
    def set_SB(self, value):
        """
        @param value: sell or buy indicator
        @type value: L{int} in {L{gnw.__eSell__}, L{gnw.__eBuy___}}
        
        @raise TypeError:
        @raise ValueError: 
        """
        if not isint( value ):
            raise TypeError, "sellbuy: not of 'int' type"
        if value != __eSell__ and value != __eBuy___:
            raise ValueError, "sellbuy: 1 for sell, -1 for buy"
        self.SB = value
    
    
    def set_CURRENT_POSITION(self, value):
        """
        @param value: dispatch period dependent
            current position(s) in [MW].
        @type value: None, L{float}, L{list} of L{float}
            or L{numpy.array} of dtype='double', [default=0.0]
        """
        self.CURRENT_POSITION = conditional( value is None, 0.0, value )
    
    
    def set_DISCOUNT_FACTOR(self, value):
        """
        @param value: dispatch period dependent
            discount factor.
        @type value: None, L{float}, L{list} of L{float}
            or L{numpy.array} of dtype='double', [default=1.0]
        """
        self.DISCOUNT_FACTOR = conditional( value is None, 1.0, value )
    
    
    def set_DISPATCH_PERIOD(self, value):
        """
        Sets dispatch period in super class and
        resizes/checks lengths of coefficient
        arrays that are dispatch period dependent.

        @param value: dispatch periods in hours [h] that
            do not need to be uniform. This array defines the
            optimisation period in total and the individual
            dispatch periods individually. If the
            dispatch period is not set during object construction
            it must be set later via call to 
            L{gnw.entity.Entity.set_DISPATCH_PERIOD}
        @type value: L{list} of L{float}
            or L{numpy.array} of dtype='double'
            
        @raise ValueError:
        """
        super( FirmProfile, self ).set_DISPATCH_PERIOD( value )
        
        nSteps = len( self.DISPATCH_PERIOD )
        
        # CURRENT_POSITION
        self.CURRENT_POSITION = \
            self.create_coefficient_array( self.CURRENT_POSITION,
                                           nSteps,
                                           "Length of 'currentPosition' must match length of 'DISPATCH_PERIOD' (gnw.firm_profile.FirmProfile.set_DISPATCH_PERIOD)" )
        
        # DISCOUNT_FACTOR
        self.DISCOUNT_FACTOR = \
            self.create_coefficient_array( self.DISCOUNT_FACTOR,
                                           nSteps,
                                           "Length of 'discountFactor' must match length of 'DISPATCH_PERIOD' (gnw.firm_profile.FirmProfile.set_DISPATCH_PERIOD)" )


    def create_lp_vars(self, prefix=""):
        """
        Creates lp variables in super class and
        and initialises lp variable (arrays) to
        correct dimensions, sizes, bounds and
        characteristics.
        
        @param prefix: prefix string prepended to all symbolic
            lp variable names
        @type prefix: L{str}
        """
        super( FirmProfile, self ).create_lp_vars( prefix )
        
        nSteps = len( self.DISPATCH_PERIOD )

        self.vol = numpy.array( pulp.LpVariable.matrix( prefix + self.name + "_vol", range( nSteps ) ) )


    def create_model(self, prefix=""):
        """
        Creates lp model in super class by
        calling L{gnw.entity.Entity.create_model}.
        Then sets up constraints and objective
        function by adding corresponding L{pulp}
        expressions to
        L{gnw.entity.Entity.constraint_list} and
        L{gnw.entity.Entity.objective_list}, respectively.
        
        @param prefix: prefix string prepended to all symbolic
            lp variable names
        @type prefix: L{str}
        """
        super( FirmProfile, self ).create_model( prefix )
        
        nSteps = len( self.DISPATCH_PERIOD )
        
        for t in xrange( nSteps ):
            self.constraint_list.append( self.vol[t] == self.CURRENT_POSITION[t]*self.DISPATCH_PERIOD[t] )

    
    def get_lp_vars(self):
        """
        This method returns a list containing all
        lp variables.
        
        @return: list of lp variables
        @rtype: L{list} of L{pulp.LpVariable}
        """
        return super( FirmProfile, self ).get_lp_vars() \
            + self.vol.tolist()

    
    def update_fmt_dict(self, fmt_dict={}):
        """
        Overwrites base class method by updating
        dictionary L{fmt_dict} with class
        specific information and calls base class'
        method L{update_fmt_dict}.
        
        @param fmt_dict: dictionary of keys of type
            L{str} and values of type
            L{gnw.entity.Entity.FmtDictEntry}
        @type fmt_dict: L{dict} 
        """
        nSteps = len( self.DISPATCH_PERIOD )
        
        fmt_dict.update({'SB' :                 FmtDictEntry( [ self.ifmt ],
                                                              'sell/buy [1/-1]',
                                                              0, None, False, 
                                                              self.SB ),
                         'CURRENT_POSITION' :   FmtDictEntry( [ self.ffmt ],
                                                              'CURRENT_POSITION [MW]',
                                                              1, (nSteps,), False,
                                                              self.CURRENT_POSITION ),
                         'DF' :                 FmtDictEntry( [ self.ffmt ],
                                                              'DF[t]',
                                                              1, (nSteps,), False,
                                                              self.DISCOUNT_FACTOR ),
                         'vol' :                FmtDictEntry( [ self.ffmt ],
                                                              'vol[t] [MWh]',
                                                              1, (nSteps,), True,
                                                              self.vol )})
        
        super( FirmProfile, self ).update_fmt_dict( fmt_dict )


    def get_results(self):
        """
        Return 'optimisation' results related to self
        in simple sequence type form.
        """
        nSteps = len( self.DISPATCH_PERIOD )

        vol = [-self.SB*self.vol[t].varValue for t in xrange( nSteps )]
        cashflow = [0.0]*nSteps
        
        return (vol, cashflow)



if __name__ == "__main__":
    print "gnw.firm_profile.py"

# ==============================================================================
#
#   Revision Control:
#
#   $Revision:: 2138                    $   Revision of last commit
#   $Author:: re04179                   $   Author of last commit
#   $Date:: 2009-09-22 14:02:19 +0200 (#$   Date of last commit
#
# ==============================================================================
