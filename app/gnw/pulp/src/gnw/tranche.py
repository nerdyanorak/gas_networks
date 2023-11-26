# ==============================================================================
#
#   package         :   GasNetWorks (gnw) Python/pulp fuelled LP/MIP modeller 
#   author          :   Marc Roth (re04179)
#   version         :   $Id: tranche.py 2138 2009-09-22 12:02:19Z re04179 $
#   heading         :   $HeadURL: http://subversion.rwe.com/svn/s_and_v_projects/GasNetworks/trunk/app/gnw/pulp/src/gnw/tranche.py $
#
#   Description     :   Package file
#
#   Creation Date   :   06Mar2009
#
#   Copyright       :   RWE Supply and Trading GmbH
#
# ==============================================================================
"""
gnw: provides trade or price tranche abstraction
"""
import pulp

from gnw.entity import Entity, FmtDictEntry

from gnw.util import isnumeric
from gnw.util import isint
from gnw.util import issequence

from gnw.util import conditional

from __init__ import __eSell__
from __init__ import __eBuy___
from __init__ import __very_large_positive_number__


class Tranche( Entity ):
    """
    The most important characteristic of a
    tranche is the delivery period
    over which it delivers gas at a constant
    rate or capacity and is priced below/above
    the corresponding standard products mid price
    given bid/ask adjustment.
    Additional characteristics
    are whether product is sold or bought, and
    whether minimal/maximal trading
    sizes apply. For each standard product
    L{gnw.product.Product} there exists at least
    one tranche object sharing the same
    sell or buy indicator and delivery period.
    If there are more than one such
    tranche for a given product then their
    bid/ask adjustments should exhibit a
    increasing value.
    Furthermore, such tranches should provide an
    upper bound for the trade size limit in order
    that this rachet pricing structure takes effect
    in the optimisation.
    The trade size for the tranche with the highest
    bid/ask adjustment may be
    unconstrained from above and serve as slack
    tranche (having potentially a punitive adjustment).   
    
    @ivar SB: sell or buy indicator
    @type SB: L{int} in {L{__eSell__}, L{__eBuy___}}
    
    @ivar BID_ASK_ADJ: tranche bid/ask adjustment for
        to corresponding standard product's mid price in [EUR/MWh].
        If L{gnw.tranche.Tranche.SB} is equal to L{__eSell__}
        then BID_ASK_ADJ represents the 'bid' to 'mid' adjustment,
        if L{gnw.tranche.Tranche.SB} is equal to L{__eBuy___}
        then BID_ASK_ADJ represents the 'mid' to 'ask' adjustment,
        that a hedger receives or pays, respectively.
    @type BID_ASK_ADJ: L{float}
    
    @ivar DELIVERY_PERIOD: tuple of length two representing
        the start index and the end index into the dispatch
        period array L{gnw.entity.Entity.DISPATCH_PERIOD},
        respectively.
    @type DELIVERY_PERIOD: (L{int},L{int})
    
    @ivar CAPACITY_LIMIT: tuple of length two representing
        minimal and maximal trade size in [MW] for given
        standard product. The elements of the tuple can
        be either None, representing no limit applies or
        a positive numerical value.
        In case CAPACITY_LIMIT[0] (lower bound) is not
        None and has a positive value, then it is guaranteed
        that if L{gnw.tranche.Tranche.pos} takes on a
        non-zero value that is at least of size CAPACITY_LIMIT[0]. 
        In case CAPACITY_LIMIT[1] (upper bound) is set to
        None, then an upper limit of
        L{gnw.__very_large_positive_number__} is
        implicitly used.
    @type CAPACITY_LIMIT: tuple of size two with elements
        set to None or of type L{float}
    
    @ivar DISCOUNT_FACTOR: dispatch period dependent discount
        factor.
    @type DISCOUNT_FACTOR: L{numpy.array} of dtype='double'
    
    @ivar pos: lp decision variable representing the
        position in [MW] to be transacted.
    @type pos: L{pulp.LpVariable}    

    @ivar semcont_trig: binary lp decision variable used to
        model L{gnw.tranche.Tranche.pos} as a semi-continuous
        variable.
    @type semcont_trig: L{pulp.LpVariable}, cat=L{pulp.LpInteger}
    """
    def __init__(self, name,
                 sellbuy = __eSell__,
                 bidAskAdj = None,
                 deliveryPeriod = (0, 0),
                 capacityLimit = (None, None),
                 discountFactor = None,
                 dispatchPeriod = None):
        """
        @param name: unique tranche identifier
        @type name: L{str}

        @param sellbuy: sell or buy indicator
        @type sellbuy: L{int} in {L{__eSell__}, L{__eBuy___}},
            [default=__eSell__]
        
        @param bidAskAdj: tranche bid/ask adjustment for
            to corresponding standard product's mid price in [EUR/MWh].
            If L{gnw.tranche.Tranche.SB} is equal to L{__eSell__}
            then bidAskAdj represents the 'bid' to 'mid' adjustment,
            if L{gnw.tranche.Tranche.SB} is equal to L{__eBuy___}
            then bidAskAdj represents the 'mid' to 'ask' adjustment,
            that a hedger receives or pays, respectively.
        @type bidAskAdj: L{float}
        
        @param deliveryPeriod: tuple of length two representing
            the start index and the end index into the dispatch
            period array L{gnw.entity.Entity.DISPATCH_PERIOD},
            respectively.
        @type deliveryPeriod: (L{int},L{int}), [default=(0,0)]
        
        @param capacityLimit: tuple of length two representing
            minimal and maximal trade size in [MW] for given
            standard product. The elements of the tuple can
            be either None, representing no limit applies or
            a positive numerical value.
            In case capacityLimit[0] (lower bound) is not
            None and as a positive value, then it is guaranteed
            that if L{gnw.tranche.Tranche.pos} takes on a
            non-zero value that its larger than capacityLimit[0]. 
            In case capacityLimit[1] (upper bound) is set to
            None, then an upper limit of
            L{gnw.__very_large_positive_number__} is
            implicitly used.
        @type capacityLimit: tuple of size two with elements
            set to None or of type L{float}, [default=(None,None)]
        
        @param discountFactor: dispatch period dependent
            discount factor.
        @type discountFactor: None, L{float}, L{list} of L{float}
            or L{numpy.array} of dtype='double', [default=1.0]
        
        @param dispatchPeriod: dispatch periods in hours [h] that
            do not need to be uniform. This array defines the
            optimisation period in total and the individual
            storage exercise periods individually. If the
            dispatch period is not set during object construction
            it must be set later via call to 
            L{gnw.entity.Entity.set_DISPATCH_PERIOD}
        @type dispatchPeriod: None, L{list} of L{float}
            or L{numpy.array} of dtype='double'
        """
        super( Tranche, self ).__init__( name )
        
        self.set_SB( sellbuy )
        self.set_BID_ASK_ADJ( bidAskAdj )
        self.set_DELIVERY_PERIOD( deliveryPeriod )
        self.set_CAPACITY_LIMIT( capacityLimit )
        self.set_DISCOUNT_FACTOR( discountFactor )
        self.set_DISPATCH_PERIOD( dispatchPeriod )

        
    def set_SB(self, value):
        """
        @param value: sell or buy indicator
        @type value: L{int} in {L{__eSell__}, L{__eBuy___}}
        
        @raise TypeError:
        @raise ValueError: 
        """
        if not isint( value ):
            raise TypeError, "sellbuy: not of 'int' type"
        if value != __eSell__ and value != __eBuy___:
            raise ValueError, "sellbuy: 1 for sell, -1 for buy"
        self.SB = value

        
    def set_BID_ASK_ADJ(self, value):
        """
        @param value: tranche bid/ask adjustment for
            to corresponding standard product's mid price in [EUR/MWh].
            If L{gnw.tranche.Tranche.SB} is equal to L{__eSell__}
            then value represents the 'bid' to 'mid' adjustment,
            if L{gnw.tranche.Tranche.SB} is equal to L{__eBuy___}
            then value represents the 'mid' to 'ask' adjustment,
            that a hedger receives or pays, respectively.
        @type value: L{float}
        
        @raise TypeError: 
        """
        self.BID_ASK_ADJ = conditional( value is None, 0.0, value )


    def set_DELIVERY_PERIOD(self, value):
        """
        @param value: tuple of length two representing start
            and end period indices into L{gnw.entity.Entity.DISPATCH_PERIOD}
            array.
        @type value: (L{int},L{int})
        
        @raise TypeError:
        @raise IndexError:
        @raise ValueError:   
        """
        if not issequence( value ):
            raise TypeError, "deliveryPeriod: tuple expected"
        if len( value ) != 2:
            raise IndexError, "deliveryPeriod: not a tuple of 2 elements"
        if not isint( value[0] ) or not isint( value[1] ):
            raise TypeError, "deliveryPeriod: elements not of 'int' type"
        if not value[0] <= value[1]:
            raise ValueError, "delvieryPeriod: value[1] > value[0]"
        self.DELIVERY_PERIOD = value


    def set_CAPACITY_LIMIT(self, value):
        """
        @param value: tuple of length two representing minimal/maximal
            trade size limit for standard product in [MW] (@see
            L{gnw.tranche.Tranche.__init__} for further details).
        @param value: tuple of size two with elements
            set to None or of type L{float}

        @raise TypeError:
        @raise IndexError:
        @raise ValueError:   
        """
        if not issequence( value ):
            raise TypeError, "capacityLimits: tuple expected"
        if len( value ) != 2:
            raise IndexError, "capacityLimits: not a tuple of 2 elements"
        if value[0] is not None:
            if not isnumeric( value[0] ):
                raise TypeError, "capacityLimits: value[0] is not numeric"
            if value[0] < 0:
                raise ValueError, "capacityLimits: value[0] is negative"
        if value[1] is not None:
            if not isnumeric( value[1] ):
                raise TypeError, "capacityLimits: value[1] is not numeric"
            if value[1] < 0:
                raise ValueError, "capacityLimtis: value[1] is negative"
        if value[0] is not None and value[1] is not None:
            if not value[0] <= value[1]:
                raise ValueError, "capacityLimits: upper bound below lower bound"
        self.CAPACITY_LIMIT = value


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
            storage exercise periods individually. If the
            dispatch period is not set during object construction
            it must be set later via call to 
            L{gnw.entity.Entity.set_DISPATCH_PERIOD}
        @type value: L{list} of L{float}
            or L{numpy.array} of dtype='double'
        """
        super( Tranche, self ).set_DISPATCH_PERIOD( value )
        
        nSteps = len( self.DISPATCH_PERIOD )
        
        if self.DELIVERY_PERIOD[0] not in range( nSteps ):
            raise ValueError, "deliveryPeriod: start is not a valid index into dispatch periods"
        if self.DELIVERY_PERIOD[1] not in range( nSteps ):
            raise ValueError, "deliveryPeriod: end is not a valid index into dispatch periods"

        # DISCOUNT_FACTOR
        self.DISCOUNT_FACTOR = \
            self.create_coefficient_array( self.DISCOUNT_FACTOR,
                                           nSteps,
                                           "Length of 'discountFactor' must match length of 'DISPATCH_PERIOD' (gnw.tranche.Tranche.set_DISPATCH_PERIOD)" )


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
        super( Tranche, self ).create_lp_vars( prefix )
        self.pos = pulp.LpVariable( prefix + self.name + "_pos" , lowBound = 0.0 )
        self.semcont_trig = pulp.LpVariable( prefix + self.name + "_semcont_trig", lowBound = 0, upBound = 1, cat = pulp.LpInteger )

        
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
        super( Tranche, self ).create_model( prefix )

        nSteps = len( self.DISPATCH_PERIOD )
        deliveryPeriodIdx = [t for t in xrange( nSteps ) if self.DELIVERY_PERIOD[0] <= t and t <= self.DELIVERY_PERIOD[1]]

        if self.CAPACITY_LIMIT[0] is not None and self.CAPACITY_LIMIT[0] > 0.0:
            if self.CAPACITY_LIMIT[1] is None:
                self.CAPACITY_LIMIT[1] = __very_large_positive_number__
            self.constraint_list.append( self.CAPACITY_LIMIT[0]*self.semcont_trig <= self.pos )
            self.constraint_list.append( self.pos <= self.CAPACITY_LIMIT[1]*self.semcont_trig )
        elif self.CAPACITY_LIMIT[1] is not None:
            self.constraint_list.append( self.pos <= self.CAPACITY_LIMIT[1] )
        
        self.objective_list.append( self.get_objective_value() )


    def get_lp_vars(self):
        """
        This method returns a list containing all
        lp variables contained in self and any
        of its super classes.
        
        @return: list of lp variables
        @rtype: L{list} of L{pulp.LpVariable}
        """
        return super( Tranche, self ).get_lp_vars()\
            + [self.pos, self.semcont_trig] 


    def update_fmt_dict(self, fmt_dict={}):
        """
        Overwrites base class method by updating
        dictionary L{fmt_dict} with tranche
        specific information and calls base class'
        method L{update_fmt_dict}.
        
        @param fmt_dict: dictionary of keys of type
            L{str} and values of type
            L{gnw.entity.Entity.FmtDictEntry}
        @type fmt_dict: L{dict} 
        """
        nSteps = len( self.DISPATCH_PERIOD )
        
        fmt_dict.update({'SB' :                    FmtDictEntry( [ self.sfmt ], 'sell/buy [1/-1]',          0, None,      False, self.SB ),
                         'BID_ASK_ADJ' :           FmtDictEntry( [ self.ffmt ], 'BID_ASK_ADJ [EUR/MWh]',    0, None,      False, self.BID_ASK_ADJ ),
                         'START_IDX' :             FmtDictEntry( [ self.ifmt ], 'START_IDX',                0, None,      False, self.DELIVERY_PERIOD[0] ),
                         'FINAL_IDX' :             FmtDictEntry( [ self.ifmt ], 'FINAL_IDX',                0, None,      False, self.DELIVERY_PERIOD[1] ),
                         'CAPACITY_LIMIT_MIN' :    FmtDictEntry( [ self.ffmt ], 'CAPACITY_LIMIT_MIN [MW]',  0, None,      False, self.CAPACITY_LIMIT[0] ),
                         'CAPACITY_LIMIT_MAX' :    FmtDictEntry( [ self.ffmt ], 'CAPACITY_LIMIT_MAX [MW]',  0, None,      False, self.CAPACITY_LIMIT[1] ),
                         'pos' :                   FmtDictEntry( [ self.ffmt ], 'pos [MW]',                 0, None,      True,  self.pos ),
                         'semcont_trig' :          FmtDictEntry( [ self.ffmt ], 'semcont_trig',             0, None,      True,  self.semcont_trig ),
                         'DF' :                    FmtDictEntry( [ self.ffmt ], 'DF[t]',                    1, (nSteps,), False, self.DISCOUNT_FACTOR )})

        super( Tranche, self ).update_fmt_dict( fmt_dict )


    def get_results(self):
        """
        """
        sb = self.SB
        start_idx = self.DELIVERY_PERIOD[0]
        final_idx = self.DELIVERY_PERIOD[1]
        cap_min = self.CAPACITY_LIMIT[0]
        cap_max = self.CAPACITY_LIMIT[1]
        bidAskAdj = self.BID_ASK_ADJ
        pos = self.pos.varValue
        
        return (sb, start_idx, final_idx, cap_min, cap_max, bidAskAdj, pos)


    def get_objective_value(self):
        """
        """
        obj = super( Tranche, self ).get_objective_value()
        
        nSteps = len( self.DISPATCH_PERIOD )
        deliveryPeriodIdx = [t for t in xrange( nSteps ) if self.DELIVERY_PERIOD[0] <= t and t <= self.DELIVERY_PERIOD[1]]
        # if SB = -1 (i.e., __eBuy___) then
        #    we have to add the adjustment to the mid price (i.e., MID_PRICE + BID_ASK_ADJ)
        #    to get the asking price, but have to multiply position times price with SB to
        #    reduce objective function value
        #    SB*pos*(MID_PRICE + BID_ASK_ADJ)
        #        = SB*pos*MID_PRICE + SB*pos*BID_ASK_ADJ
        #        = SB*pos*MID_PRICE - pos*BID_ASK_ADJ
        # if SB = +1 (i.e., __eSell__) then
        #    we have to subtrace the adjustment from the mid price (i.e.e, MID_PRICE - BID_ASK_ADJ)
        #    to get the bid price. For symmetry we multiply position times price with SB.
        #    Objective function value will increase by
        #    SB*pos*(MID_PRICE - BID_ASK_ADJ)
        #        = SB*pos*MID_PRICE - SB*pos*BID_ASK_ADJ
        #        = SB*pos*MID_PRICE - pos*BID_ASK_ADJ
        # In both cases term SB*pos*MID_PRICE is handled by gnw.product.Product.get_objective_value().
        # Here only term -pos*BID_ASK_ADJ is handled
        obj += pulp.LpAffineExpression( -self.BID_ASK_ADJ*self.pos*sum( [self.DISPATCH_PERIOD[t]*self.DISCOUNT_FACTOR[t] for t in deliveryPeriodIdx ] ) )
        return obj



if __name__ == "__main__":
    print "gnw.tranche.py"

# ==============================================================================
#
#   Revision Control:
#
#   $Revision:: 2138                    $   Revision of last commit
#   $Author:: re04179                   $   Author of last commit
#   $Date:: 2009-09-22 14:02:19 +0200 (#$   Date of last commit
#
# ==============================================================================
