"""L{TradeTranche} gas network L{Entity}"""
import numpy
import pulp

#from src.entities.entity import Entity
#from src.utils.util import conditional
import entity
import stdprod
import market
from utils.util import conditional

__very_large_positive_number__ = 1.0e9 # 1 Mio MW capacity

class TradeTranche(entity.Entity):
    """
    @ivar name: unique entity name
    @type name: L{str}
    
    @ivar PRICE: tuple of size two holding bid and ask price
    for trade tranche in [EUR/MWh]
    @type PRICE: L{tuple}, (number, number)
    
    @ivar DELIVERY_PERIOD: tuple of size of two holding indices into
    the L{DISPATCH_PERIODS} array with L{DELIVERY_PERIOD}[0] being the
    start index of the delivery period and L{DELIVERY_PERIOD}[1] being
    the end index of the delivery period.
    @type DELIVERY_PERIOD: (int, int)
    
    @ivar CAPACITY_LIMITS: tuple of size two holding minimal and/or
    maximal allowed trade capacity in [MW] at given bid/ask L{PRICE}.
    for given delivery period L{DELIVERY_PERIOD} 
    If tuple element value is equal to L{None} then limit is not applied.
    @type CAPACITY_LIMITS: (min, max), with min, max in {L{None}, number}
    
    @ivar DISCOUNT_FACTOR: array of cost of size len(L{DISPATCH_PERIODS})
    containing the discount factors to be used for cash flows from sales and
    purchase arising during each given dispatch period. This means that
    DISCOUNT_FACTOR[t] doesn't necessarily need to be the discount factor
    for cash flows payed at the end of DISPATCH_PERIOD[t] but some other
    point in time (for example settlement date of standard product its
    delivery period includes given dispatch period DISPATCH_PERIODS[t])
    @type DISCOUNT_FACTOR: L{numpy.ndarray} of dtype='float'  
    
    @ivar sales_position: array of decision variables of size
    len(L{DISPATCH_PERIODS}) representing volume sold in [MWh]
    at bid L{PRICE} [EUR/MWh]
    @type sales_position: L{numpy.ndarray} of dtype='object'
    where object is L{pulp.LpVariable}
    
    @ivar purch_position: array of decision varaibles of size
    len(L{DISPATCH_PERIODS}) representing the volume purchased
    in [MWh] at ask L{PRICE} [EUR/MWh]
    @type purch_position: L{numpy.ndarray} of dtype='object'
    where object is L{pulp.LpVariable}
    """
    def __init__(self,
                 name,
                 price = (0.0, 0.0),
                 deliveryPeriod = (0,0),
                 capacityLimits = (None, None),
                 discountFactor = None,
                 stdprd = None):
        """
        @param name: unique name of entity
        @type name: L{str}
        
        @param price: tuple of size two holding bid and ask price
        for trade tranche in [EUR/MWh]
        @type PRICE: L{tuple}, (number, number)
        
        @param deliveryPeriod: tuple of size of two holding indices into
        the L{DISPATCH_PERIODS} array with L{deliveryPeriod}[0] being the
        start index of the delivery period and L{deliveryPeriod}[1] being
        the end index of the delivery period.
        @type deliveryPeriod: (int, int)
        
        @param capacityLimits: tuple of size two holding minimal and/or
        maximal allowed trade capacity in [MW] at given bid/ask L{PRICE}.
        for given delivery period L{deliveryPeriod} 
        If tuple element value is equal to L{None} then limit is not applied.
        @type capacityLimits: (min, max), with min, max in {L{None}, number}
        
        @param discountFactor: a number or an array of cost of size
        len(L{DISPATCH_PERIODS}) containing the discount factors to be used
        for cash flows from sales and purchase arising during each given
        dispatch period. This means that L{discountFactor}[t] doesn't
        necessarily need to be the discount factor for cash flows payed at
        the end of L{DISPATCH_PERIODS}[t] but some other
        point in time (for example settlement date of standard product its
        delivery period includes given dispatch period L{DISPATCH_PERIODS}[t]).
        If the value is None then discountFactor is set to 1.0.
        @type DISCOUNT_FACTOR: number, L{numpy.ndarray} of dtype='float'  
        
        @param stdprd: a reference to a L{StandardProduct} entity for which it
        serves as a source as well as a sink.
        @type stdprd: L{StandardProduct}
        """
        super(TradeTranche, self).__init__( name,
                                            conditional( stdprd is not None, [stdprd], [] ),
                                            conditional( stdprd is not None, [stdprd], [] ) )
        
        self.set_PRICE( price )
        self.set_DELIVERY_PERIOD( deliveryPeriod )
        self.set_CAPACITY_LIMITS( capacityLimits )
        self.set_DISCOUNT_FACTOR( discountFactor )
        
        self.purch_position = numpy.empty( 0, dtype='object' )
        self.sales_position = numpy.empty( 0, dtype='object' )

        self.purch_semi_cont_trigger = None
        self.sales_semi_cont_trigger = None


    def set_PRICE(self, value):
        if len(value) != 2:
            raise ValueError, "price: not a tuple of 2 elements"
        self.PRICE = value


    def set_DELIVERY_PERIOD(self, value):
        if len(value) != 2:
            raise ValueError, "deliveryPeriod: not a tuple of 2 elements"
        if value[1] < value[0]:
            raise ValueError, "delvieryPeriod: end dispatch period idx < start dispatch period idx"
        self.DELIVERY_PERIOD = value


    def set_CAPACITY_LIMITS(self, value):
        if len(value) != 2:
            raise ValueError, "capacityLimits: not a tuple of 2 elements"
        if value[0] is not None and value[1] is not None and value[1] < value[0]:
            raise ValueError, "capacityLimits: upper bound below lower bound"
        self.CAPACITY_LIMITS = value
        if self.CAPACITY_LIMITS[1] is None:
            self.CAPACITY_LIMITS = (self.CAPACITY_LIMITS[0], __very_large_positive_number__)


    def set_DISCOUNT_FACTOR(self, value):
        self.DISCOUNT_FACTOR = conditional( value is None, 1.0, value )

        
    def set_DISPATCH_PERIODS(self, dispatchPeriods):
        """
        Set the dispatch periods array (calling parent's
        set method) and set coefficient arrays to the correct
        length and initialise with some meaningful defaults,
        if they haven't been set appropriately beforehand
        (using __init__(...) or setters).
        If coefficient arrays have already been set check
        for appropriate size (and values?).
        
        @param dispatchPeriods: array of dispatch periods
        defining the overall optimisation horizon as well
        as the individual duration of each dispatch period.
        @type dispatchPeriods: L{numpy.ndarray} of dtype='float'
        """
        super(TradeTranche, self).set_DISPATCH_PERIODS( dispatchPeriods )
        
        nSteps = len( self.DISPATCH_PERIODS )
        
        if self.DELIVERY_PERIOD[0] not in range( nSteps ):
            raise ValueError, "deliveryPeriod: start is not a valid index into dispatch periods"
        if self.DELIVERY_PERIOD[1] not in range( nSteps ):
            raise ValueError, "deliveryPeriod: end is not a valid index into dispatch periods"

        # DISCOUNT_FACTOR
        self.DISCOUNT_FACTOR = \
            self.create_coefficient_array( self.DISCOUNT_FACTOR,
                                           nSteps,
                                           "Length of 'discountFactor' must match length of 'dispatchPeriods'" )


    def create_lp_vars(self, prefix=""):
        """
        This function creates (multi-dimensional) arrays of 
        L{pulp.LpVariable}s, L{pulp.LpConstraint}s, etc.
        of the adequate dimensionality and size.
        
        @precondition: Function L{setDISPATCH_PERIODS}
        
        @param prefix: string used as a prefix for naming L{pulp.LpVariable}s,
        L{pulp.LpConstraint}s, etc.
        @type prefix: string 
        """
        super(TradeTranche, self).create_lp_vars( prefix )
        
        nSteps = len( self.DISPATCH_PERIODS )
        
        self.purch_position = numpy.array( pulp.LpVariable.matrix( prefix + self.name + "_purch_pos" , range( nSteps ),
                                                                   lowBound = 0.0 ) )
        self.sales_position = numpy.array( pulp.LpVariable.matrix( prefix + self.name + "_sales_pos" , range( nSteps ),
                                                                   lowBound = 0.0 ) )

        self.purch_semi_cont_trigger = pulp.LpVariable( prefix + self.name + "_purch_semi_cont_trig",
                                                        lowBound = 0.0, upBound = 1.0, cat = pulp.LpInteger )
        self.sales_semi_cont_trigger = pulp.LpVariable( prefix + self.name + "_sales_semi_cont_trig",
                                                        lowBound = 0.0, upBound = 1.0, cat = pulp.LpInteger )

        
    def create_model(self, prefix=""):
        """
        The dynamics of the trade tranche are as follows:
            - Inflow/Outflow restricted to standard product's delivery period
                - Restricted inflow volume:
                L{in_flow}[t] [MWh] == 0, for t not in L{DELIVERY_PERIOD}
                - Restricted outflow volume:
                L{out_flow}[t] [MWh] == 0, for t not in L{DELIVERY_PERIOD}
            - Transacted (sold: L{trade_volume} < 0; purchased: L{trade_volume} > 0) gas volume in [MWh]:
                - Transacted volume balance equation:
                L{trade_volume}[t] [MWh] == L{out_flow}[t] [MWh] - L{in_flow}[t] [MWh]
                - Delivery period volume equations:
                L{trade_volume}[t] [MWh] == L{trade_volume}[u] [MWh], for all t, u in L{DELIVERY_PERIOD}
                must hold
            - Sales (L{trade_volume} < 0) gas volume in [MWh]:
                - Non-negativity constraints:
                L{sales_position}[t] [MWh] >= 0, for all t in L{DISPATCH_PERIODS}
                (see variable construction in method L{create_lp_vars}).
                - Sales volume constraints:
                L{sales_position}[t] [MWh] >= -L{trade_volume}[t] [MWh], for all t in L{DISPATCH_PERIODS}
                - Minimal sales volume equation:
                sum(L{sales_position}[t], t in L{DELIVERY_PERIOD}) [MWh] >=
                L{CAPACITY_LIMITS}[0]*sum(L{DISPATCH_PERIODS}[t], t in L{DELIVERY_PERIOD}) [MW*h]
                (--> semi-continuous: 0 or >= MIN) 
                - Maximal delivery volume equation:
                sum(L{sales_position}[t], t in L{DELIVERY_PERIOD}) [MWh] <=
                L{CAPACITY_LIMITS}[1]*sum(L{DISPATCH_PERIODS}[t], t in L{DELIVERY_PERIOD}) [MW*h]
                - Objective function component:
                sum(L{sales_position}[t]*PRICE[0]*DISCOUNT_FACTOR[t], t in L{DELIVERY_PERIOD})
            - Purchase (L{trade_volume} > 0) gas volume in [MWh]:
                - Non-negativity constraints:
                L{purch_position}[t] [MWh] >= 0, for all t in L{DISPATCH_PERIODS}
                (see variable construction in method L{create_lp_vars}).
                - Purchase volume equation:
                L{purch_position}[t] [MWh] >= L{trade_volume}[t] [MWh], for all t in L{DISPATCH_PERIODS}
                - Minimal purchase volume equation:
                sum(L{purch_position}[t], t in L{DELIVERY_PERIOD}) [MWh] >=
                L{CAPACITY_LIMITS}[0]*sum(L{DISPATCH_PERIODS}[t], t in L{DELIVERY_PERIOD}) [MW*h]
                (--> semi-continuous: 0 or >= MIN)
                - Maximal purchase volume equation:
                sum(L{purch_position}[t], t in L{DELIVERY_PERIOD}) [MWh] <=
                L{CAPACITY_LIMITS}[1]*sum(L{DISPATCH_PERIODS}[t], t in L{DELIVERY_PERIOD}) [MW*h]
                - Objective function component:
                (-1.0)*sum(L{purch_position}[t]*PRICE[1]*DISCOUNT_FACTOR[t], t in L{DELIVERY_PERIOD})
        """
        super(TradeTranche, self).create_model( prefix )

        nSteps = len( self.DISPATCH_PERIODS )
        deliveryPeriodIdx = [t for t in xrange( nSteps ) if self.DELIVERY_PERIOD[0] <= t and t <= self.DELIVERY_PERIOD[1]]
        nonDeliveryPeriodIdx = [t for t in xrange( nSteps ) if t < self.DELIVERY_PERIOD[0] or t > self.DELIVERY_PERIOD[1]]

        # In-/Out-flow volume for non-delivery period:
        for t in nonDeliveryPeriodIdx:
            self.constraint_list.append( self.in_flow[t] == 0.0 )
            self.constraint_list.append( self.out_flow[t] == 0.0 ) 
            self.constraint_list.append( self.sales_position[t] == 0.0 )
            self.constraint_list.append( self.purch_position[t] == 0.0 )

        # Transacted volume:
        for t in deliveryPeriodIdx:
            #                            [MW]                   [h]                         [MWh]
            self.constraint_list.append( self.sales_position[t]*self.DISPATCH_PERIODS[t] == self.in_flow[t] )
            self.constraint_list.append( self.purch_position[t]*self.DISPATCH_PERIODS[t] == self.out_flow[t] )

        ## Delivery period volume equations: ONLY EXECUTE IF DELIVERY PERIOD > 1 DISPATCH_PERIOD!
        for t in xrange( self.DELIVERY_PERIOD[0], self.DELIVERY_PERIOD[1] ):
            # Require uniform position [MW] over whole standard product delivery period 
            self.constraint_list.append( self.sales_position[t] == self.sales_position[t + 1] )
            self.constraint_list.append( self.purch_position[t] == self.purch_position[t + 1] )

        # From now on positions of delivery period are linked and uniform.
        # Use first delivery sub-period as proxy-period.
        proxy_t = self.DELIVERY_PERIOD[0]

        if self.CAPACITY_LIMITS[0] is not None:
            # both are not None

            # Sales volume:
            # Requires a semi-continuous variable
            self.constraint_list.append( self.sales_position[proxy_t] >= self.sales_semi_cont_trigger*self.CAPACITY_LIMITS[0] )
            self.constraint_list.append( self.sales_position[proxy_t] <= self.sales_semi_cont_trigger*self.CAPACITY_LIMITS[1] )
            # Purchase volume
            # Requires a semi-continuous variable
            self.constraint_list.append( self.purch_position[proxy_t] >= self.purch_semi_cont_trigger*self.CAPACITY_LIMITS[0] )
            self.constraint_list.append( self.purch_position[proxy_t] <= self.purch_semi_cont_trigger*self.CAPACITY_LIMITS[1] )
        else:   
            self.constraint_list.append( self.sales_position[proxy_t] <= self.CAPACITY_LIMITS[1] )
            self.constraint_list.append( self.purch_position[proxy_t] <= self.CAPACITY_LIMITS[1] )
        
        all_srcs_stdprods = True
        for src in self.src_list:
            if not isinstance( src, stdprod.StandardProduct ):
                all_srcs_stdprods = False
                break
        
        all_snks_stdprods = True
        for snk in self.snk_list:
            if not isinstance( snk, stdprod.StandardProduct ):
                all_snks_stdprods = False
                break

        if all_srcs_stdprods and all_snks_stdprods:
            self.objective_list.append(  pulp.lpSum( [self.sales_position[t]*self.DISPATCH_PERIODS[t]*self.PRICE[0]*self.DISCOUNT_FACTOR[t] for t in deliveryPeriodIdx] ) )
            self.objective_list.append( -pulp.lpSum( [self.purch_position[t]*self.DISPATCH_PERIODS[t]*self.PRICE[1]*self.DISCOUNT_FACTOR[t] for t in deliveryPeriodIdx] ) )
#        else:
#            for t in deliveryPeriodIdx:
#                self.constraint_list.append( self.in_flow[t] >= self.out_flow[t] )


    def get_lp_vars(self):
        """
        """
        return super(TradeTranche, self).get_lp_vars()\
            + self.sales_position.tolist()\
            + self.purch_position.tolist()\
            + [ self.sales_semi_cont_trigger,\
                self.purch_semi_cont_trigger ] 


if __name__ == "__main__":
    print conditional(True, "Yes", "Nope")
    print conditional(False, "Yes", "Nope")
