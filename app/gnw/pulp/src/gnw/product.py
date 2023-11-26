# ==============================================================================
#
#   package         :   GasNetWorks (gnw) Python/pulp fuelled LP/MIP modeller 
#   author          :   Marc Roth (re04179)
#   version         :   $Id: product.py 2138 2009-09-22 12:02:19Z re04179 $
#   heading         :   $HeadURL: http://subversion.rwe.com/svn/s_and_v_projects/GasNetworks/trunk/app/gnw/pulp/src/gnw/product.py $
#
#   Description     :   Package file
#
#   Creation Date   :   06Mar2009
#
#   Copyright       :   RWE Supply and Trading GmbH
#
# ==============================================================================
"""
gnw: provides standard product abstraction 
"""
import numpy
import pulp

from gnw.entity import FmtDictEntry 
from gnw.container_entity import ContainerEntity

from gnw.tranche import Tranche

from gnw.util import isnumeric
from gnw.util import isint
from gnw.util import issequence
from gnw.util import conditional

from gnw.named_item import NamedItem, NamedItemAttr, NamedItemData
from gnw.named_item import ni_type_named_item

from __init__ import __eSell__
from __init__ import __eBuy___
from __init__ import __very_large_positive_number__


class Product( ContainerEntity ):
    """
    This class provides an abstraction for
    a standard product and encapsulates
    entities as given in entity_type_list
    (currently only L{gnw.tranche.Tranche}
    in order to model volume dependent
    bid/ask prices)
     
    The most important characteristic of a
    standard product is the delivery period
    over which it delivers gas at a constant
    rate or capacity. Additional characteristics
    are whether product is sold or bought,
    standard clip sizes or minimal/maximal trading
    sizes apply, what the current position is and
    its (mid) price.
    
    @ivar SB: sell or buy indicator
    @type SB: L{int} in {L{__eSell__}, L{__eBuy___}}
    
    @ivar MID_PRICE: Mid price for standard product in [EUR/MWh]. Used
        to mark-to-market L{gnw.product.Product.CURRENT_POSITION}.
    @type MID_PRICE: L{float}
    
    @ivar CLIP_SIZE: clip size in [MW]. If set (i.e., not None) then
        lp variable L{gnw.product.Product.pos} is forced to take on
        only integral multiples of CLIP_SIZE. 
    @type CLIP_SIZE: None or positive L{float}
    
    @ivar CURRENT_POSITION: current product position.
        If we buy (SB = -1) the product then we are
        long CURRENT_POS, if CURRENT_POS > 0,
        short otherwise.
        If we sell (SB = 1) the product then we are
        short CURRENT_POS, if CURRENT_POS > 0,
        long otherwise.
    @type CURRENT_POSITION: L{float}
    
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
        None and as a positive value, then it is guaranteed
        that if L{gnw.product.Product.pos} takes on a
        non-zero value that its larger than CAPACITY_LIMIT[0]. 
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
    
    @ivar num_clips: integer lp decision variable representing
        the number of clips to be transacted.
    @type num_clips: L{pulp.LpVariable}, cat=L{pulp.LpInteger}
    
    @ivar semcont_trig: binary lp decision variable used to
        model L{gnw.product.Product.pos} as a semi-continuous
        variable.
    @type semcont_trig: L{pulp.LpVariable}, cat=L{pulp.LpInteger}

    @ivar vol: lp decision variables representing the volume
        in [MWh] of the standard product during each
        L{gnw.entity.Entity.DISPATCH_PERIOD}. They are equal
        to 0 for dispatch periods not belonging to the
        products delivery period and
        L{gnw.entity.Entity.DISPATCH_PERIOD}[t]*L{gnw.product.Product.pos}, 
        forall t in xrange( DELIVERY_PERIOD[0], DELIVERY_PERIOD[1] + 1 ).
    @type vol: L{pulp.LpVariable}
    """
    entity_type_list = (Tranche,)

    
    def __init__(self, name,
                 entityList = [],
                 sellbuy = __eSell__,
                 midPrice = None,
                 clipSize = None,
                 currentPosition = None,
                 deliveryPeriod = (0,0),
                 capacityLimit = (None,None),
                 discountFactor = None,
                 dispatchPeriod = None):
        """
        @param name: unique product identifier
        @type name: L{str}

        @param sellbuy: sell or buy indicator
        @type sellbuy: L{int} in {L{__eSell__}, L{__eBuy___}},
            [default=__eSell__]
        
        @param midPrice: Mid price for standard product in [EUR/MWh]. Used
            to mark-to-market L{gnw.product.Product.CURRENT_POSITION}.
        @type midPrice: L{float}, [default=0.0]
        
        @param clipSize: clip size in [MW]. If set (i.e., not None) then
            lp variable L{gnw.product.Product.pos} is forced to take on
            only integral multiples of CLIP_SIZE. 
        @type clipSize: None or positive L{float}, [default=None]
        
        @param currentPosition: current product position.
            (see CURRENT_POSITION member variable for details)
        @type currentPosition: None, L{float}, [default=None, implying 0.0]
        
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
            that if L{gnw.product.Product.pos} takes on a
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
        # filter out the tranches that matter for
        # this product
        entity_list = [item for item in entityList \
                       if isinstance( item, Product.entity_type_list ) \
                       and item.SB == sellbuy \
                       and item.DELIVERY_PERIOD[0] == deliveryPeriod[0] \
                       and item.DELIVERY_PERIOD[1] == deliveryPeriod[1]]

        super( Product, self ).__init__( name, Product.entity_type_list, entity_list )
        
        self.set_SB( sellbuy )
        self.set_MID_PRICE( midPrice )
        self.set_CLIP_SIZE( clipSize )
        self.set_CURRENT_POSITION( currentPosition )
        self.set_DELIVERY_PERIOD( deliveryPeriod )
        self.set_CAPACITY_LIMIT( capacityLimit )
        self.set_DISCOUNT_FACTOR( discountFactor )
        self.set_DISPATCH_PERIOD( dispatchPeriod )
        

    def get_tranche(self, name):
        """
        """
        return self.get_entity( name, Tranche )
    
    
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

        
    def set_MID_PRICE(self, value):
        """
        @param value: mid price of standard product in [EUR/MWh]
        @type value: L{float} or L{int}
        
        @raise TypeError:
        """
        self.MID_PRICE = conditional( value is None, 0.0, value )


    def set_CLIP_SIZE(self, value):
        """
        @param value: clip size of standard product in [MW]
        @param value: non-negative L{float} or L{int}
        
        @raise TypeError:
        @raise ValueError:  
        """
        if value is not None:
            if not isnumeric( value ):
                raise TypeError, "clipSize: None or numeric value expected"
            if value < 0.0:
                raise ValueError, "clipSize: None-negative numeric value expected"
        self.CLIP_SIZE = value
        

    def set_CURRENT_POSITION(self, value):
        """
        @param value: current position of standard product in [MW]
        @type value:  L{float} or L{int}
        
        @raise TypeError: 
        """  
        self.CURRENT_POSITION = conditional( value is not None, value, 0.0 )
        
        
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
            raise ValueError, "deliveryPeriod: value[1] > value[0]"
        self.DELIVERY_PERIOD = value


    def set_CAPACITY_LIMIT(self, value):
        """
        @param value: tuple of length two representing minimal/maximal
            trade size limit for standard product in [MW] (@see
            L{gnw.product.Product.__init__} for further details).
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
                raise ValueError, "capacityLimits: value[1] is negative" 
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
            
        @raise ValueError:
        """
        super( Product, self ).set_DISPATCH_PERIOD( value )
        
        nSteps = len( self.DISPATCH_PERIOD )
        
        if self.DELIVERY_PERIOD[0] not in range( nSteps ):
            raise ValueError, "deliveryPeriod: start is not a valid index into dispatch periods"
        if self.DELIVERY_PERIOD[1] not in range( nSteps ):
            raise ValueError, "deliveryPeriod: end is not a valid index into dispatch periods"

        # DISCOUNT_FACTOR
        self.DISCOUNT_FACTOR = \
            self.create_coefficient_array( self.DISCOUNT_FACTOR,
                                           nSteps,
                                           "Length of 'discountFactor' must match length of 'DISPATCH_PERIOD' (gnw.product.Product.set_DISPATCH_PERIOD)" )


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
        super( Product, self ).create_lp_vars( prefix )
        
        nSteps = len( self.DISPATCH_PERIOD )
        
        self.pos = pulp.LpVariable( prefix + self.name + "_pos" , lowBound = 0.0 )
        
        self.num_clips = pulp.LpVariable( prefix + self.name + "_num_clips", lowBound = 0, cat = pulp.LpInteger )
        self.semcont_trig = pulp.LpVariable( prefix + self.name + "_semcont_trig", lowBound = 0, upBound = 1, cat = pulp.LpInteger )

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
        super( Product, self ).create_model( prefix )

        nSteps = len( self.DISPATCH_PERIOD )
        deliveryPeriodIdx = [t for t in xrange( nSteps ) if self.DELIVERY_PERIOD[0] <= t and t <= self.DELIVERY_PERIOD[1]]
        nonDeliveryPeriodIdx = [t for t in xrange( nSteps ) if t < self.DELIVERY_PERIOD[0] or self.DELIVERY_PERIOD[1] < t]

        if self.CAPACITY_LIMIT[0] is not None and self.CAPACITY_LIMIT[0] > 0.0:
            if self.CAPACITY_LIMIT[1] is None:
                self.CAPACITY_LIMIT[1] = __very_large_positive_number__
            self.constraint_list.append( self.CAPACITY_LIMIT[0]*self.semcont_trig <= self.pos )
            self.constraint_list.append( self.pos <= self.CAPACITY_LIMIT[1]*self.semcont_trig )
        elif self.CAPACITY_LIMIT[1] is not None:
            self.constraint_list.append( self.pos <= self.CAPACITY_LIMIT[1] )
            
        if self.CLIP_SIZE is not None and self.CLIP_SIZE > 0.0:
            self.constraint_list.append( self.pos == self.num_clips*self.CLIP_SIZE )
            self.constraint_list.append( self.num_clips*self.CLIP_SIZE <= self.CAPACITY_LIMIT[1] ) 
        
        for t in deliveryPeriodIdx:
            self.constraint_list.append( self.vol[t] == (self.pos + self.CURRENT_POSITION)*self.DISPATCH_PERIOD[t] )
        for t in nonDeliveryPeriodIdx:
            self.constraint_list.append( self.vol[t] == 0.0 )

        # Standard product/trade tranche balance equation: The position
        # for a given standard product with given delivery period and
        # sell/buy flag (it is assumed that no more than one standard
        # product with such features exist in the network) must equate
        # to the sum of the positions of all trade tranches with
        # equivalent features (it is assumed that there exists at least
        # one trade tranche with exactly such equivalent features in
        # the network).
        self.constraint_list.append( self.pos == \
            pulp.lpSum( [trn.pos for trn in self.get_entity_list( Tranche )
                         if trn.SB == self.SB and \
                         trn.DELIVERY_PERIOD[0] == self.DELIVERY_PERIOD[0] and
                         trn.DELIVERY_PERIOD[1] == self.DELIVERY_PERIOD[1]] ) )

        self.objective_list.append( self.get_objective_value() )
            

    def get_lp_vars(self):
        """
        This method returns a list containing all
        lp variables contained in self and any
        of its super classes.
        
        @return: list of lp variables
        @rtype: L{list} of L{pulp.LpVariable}
        """
        return super( Product, self ).get_lp_vars()\
            + self.vol.tolist()\
            + [self.pos, self.semcont_trig, self.num_clips] 


    def update_fmt_dict(self, fmt_dict={}):
        """
        Overwrites base class method by updating
        dictionary L{fmt_dict} with product
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
                         'MID_PRICE' :         FmtDictEntry( [ self.ffmt ],
                                                              'MID_PRICE [EUR/MWh]',
                                                              0, None, False,
                                                              self.MID_PRICE ),
                         'CLIP_SIZE' :          FmtDictEntry( [ self.ffmt ],
                                                              'CLIP_SIZE',
                                                              0, None, False,
                                                              self.CLIP_SIZE ),
                         'CURRENT_POSITION' :   FmtDictEntry( [ self.ffmt ],
                                                              'CURRENT_POSITION [MW]',
                                                              0, None, False,
                                                              self.CURRENT_POSITION ),
                         'START_IDX' :          FmtDictEntry( [ self.ifmt ],
                                                              'START_IDX',
                                                              0, None, False,
                                                              self.DELIVERY_PERIOD[0] ),
                         'FINAL_IDX' :          FmtDictEntry( [ self.ifmt ],
                                                              'FINAL_IDX',
                                                              0, None, False,
                                                              self.DELIVERY_PERIOD[1] ),
                         'CAPACITY_LIMIT_MIN' : FmtDictEntry( [ self.ffmt ],
                                                              'CAPACITY_LIMIT_MIN [MW]',
                                                              0, None, False,
                                                              self.CAPACITY_LIMIT[0] ),
                         'CAPACITY_LIMIT_MAX' : FmtDictEntry( [ self.ffmt ],
                                                              'CAPACITY_LIMIT_MAX [MW]',
                                                              0, None, False,
                                                              self.CAPACITY_LIMIT[1] ),
                         'DF' :                 FmtDictEntry( [ self.ffmt ],
                                                              'DF[t]',
                                                              1, (nSteps,), False,
                                                              self.DISCOUNT_FACTOR ),
                         'pos' :                FmtDictEntry( [ self.ffmt ],
                                                              'pos [MW]',
                                                              0, None, True, self.pos ),
                         'num_clips' :          FmtDictEntry( [ self.ifmt ],
                                                              'num_clips',
                                                              0, None, True,
                                                              self.num_clips ),
                         'semcont_trig' :       FmtDictEntry( [ self.ifmt ],
                                                              'semcont_trig',
                                                              0, None, True, self.semcont_trig ),
                         'vol' :                FmtDictEntry( [ self.ffmt ],
                                                              'vol[t] [MWh]',
                                                              1, (nSteps,), True, self.vol )})
        super( Product, self ).update_fmt_dict( fmt_dict )


    def get_results(self):
        """
        """
        sb = self.SB
        start_idx = self.DELIVERY_PERIOD[0]
        final_idx = self.DELIVERY_PERIOD[1]
        cap_min = self.CAPACITY_LIMIT[0]
        cap_max = self.CAPACITY_LIMIT[1]
        mid_price = self.MID_PRICE
        clip_size = self.CLIP_SIZE
        current_pos = self.CURRENT_POSITION
        pos = self.pos.varValue
        
        return (sb, start_idx, final_idx, cap_min, cap_max, mid_price, clip_size, current_pos, pos)


    def get_objective_value(self):
        """
        """
        return self.get_mark_to_market_value()
    

    def get_mark_to_market_value(self):
        """
        Returns affine expression function representing
        the mark to market value corresponding to the
        objective value but using mid prices.
        
        @return: mark to market value function.
        @rtype: L{pulp.LpAffineExpression}
        """
        mtm = super( Product, self ).get_mark_to_market_value()

        nSteps = len( self.DISPATCH_PERIOD )
        deliveryPeriodIdx = [t for t in xrange( nSteps ) if self.DELIVERY_PERIOD[0] <= t and t <= self.DELIVERY_PERIOD[1]]
        mtm += pulp.LpAffineExpression( self.SB*self.MID_PRICE*self.pos*             sum( [self.DISPATCH_PERIOD[t]*self.DISCOUNT_FACTOR[t] for t in deliveryPeriodIdx] ) )
        mtm += pulp.LpAffineExpression( self.SB*self.MID_PRICE*self.CURRENT_POSITION*sum( [self.DISPATCH_PERIOD[t]*self.DISCOUNT_FACTOR[t] for t in deliveryPeriodIdx] ) )

        return mtm


    def get_lp_var_values(self, key_list=[]):
        """
        Retrieve solution values of all decision variables
        contained in internal entity list 
        as well as this instances itself.
        
        @return: L{gnw.named_item.NamedItem} class instance
            encapsulating all solutions values of the
            decision variables of this
            network L{gnw.entity.Entity} instance and
            all contained L{gnw.entity.Entity} sub-class
            instances.
        @rtype: L{gnw.named_item.NamedItem}
        """
        trn_named_item_list = []
        for trn in self.get_entity_list( Tranche ):
            named_item_list = trn.get_lp_var_values( key_list )
            trn_named_item_list.append( NamedItem( trn.name,
                                                   NamedItemAttr( 1, [len( named_item_list )], [ni_type_named_item] ),
                                                   NamedItemData( named_item_list ) ) )

        named_item_list = []
        named_item_list.append( super( Product, self).get_lp_var_values( key_list ) )
        named_item_list.append( NamedItem( 'TRN_DICT_LIST',
                                           NamedItemAttr( 1, [len( trn_named_item_list )], [ni_type_named_item] ),
                                           NamedItemData( trn_named_item_list ) ) )

        return named_item_list 

        
    def get_tranche_results(self):
        """
        """
        # order by 'sb' (descending), 'start_idx' (ascending), 'final_idx' (ascending)
        trn_compare = lambda x, y : conditional(x[0] != y[0],
                                                y[0] - x[0],                            # descending
                                                conditional(x[1] != y[1],
                                                            x[1] - y[1],                # ascending    
                                                            conditional(x[2] != y[2],
                                                                        x[2] - y[2],    # ascending
                                                                        0)))

        trn_rslts = []
        for trn in self.get_entity_list( Tranche ):
            (sb, start_idx, final_idx, cap_min, cap_max, bid_ask_adj, pos) = trn.get_results()
            trn_rslts.append( [sb, start_idx, final_idx, cap_min, cap_max, bid_ask_adj, pos] )

        trn_rslts.sort( cmp = trn_compare )

        return trn_rslts



if __name__ == "__main__":
    print "gnw.product.py"

# ==============================================================================
#
#   Revision Control:
#
#   $Revision:: 2138                    $   Revision of last commit
#   $Author:: re04179                   $   Author of last commit
#   $Date:: 2009-09-22 14:02:19 +0200 (#$   Date of last commit
#
# ==============================================================================
