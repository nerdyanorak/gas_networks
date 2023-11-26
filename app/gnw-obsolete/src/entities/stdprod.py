"""L{StandardProduct} gas network L{Entity}"""
import pulp
import numpy

#from src.entities.entity import Entity
#from src.utils.util import conditional
import entity
import market
import ttranche

from utils.util import conditional

__very_large_positive_number__ = 1.0e9 # 1 Mio MW capacity

class StandardProduct(entity.Entity):
    """
    The StandardProduct class object's role is to
    store information on the standard product that
    are tradable in the market. The StandardProduct
    class object collaborates with the L{Market}
    L{Entity} and one or more L{TradeTranche} L{Entity}
    objects 

    @ivar DELIVERY_PERIOD: This is a tuple (t_s, t_e) of index values into the
    L{DISPATCH_PERIODS} array and define as such the delivery
    period of the given standard product.
    It is the user's responsibility to assure the consistency of
    L{DISPATCH_PERIODS} array contents and the L{DELIVERY_PERIOD}
    tuple values. This means that the
    standard product's delivery period must be representable by one
    or more consecutive dispatch periods given in L{DISPATCH_PERIODS}.
    @type DELIVERY_PERIOD: (number,number)

    @ivar CURRENT_POSITION: Is a floating point number representing the current
    hedge position of that standard product at the time of
    optimisation in [MW].
    The equivalent [MWh] position is calculated as
        - t_s = L{DELIVERY_PERIOD}[0]
        - t_e = L{DELIVERY_PERIOD}[1]
        - positionMWh [MWh] = L{CURRENT_POSITION}*sum(DISPATCH_PERIODS[t]; t in t_s..t_e) [MW*h]
        - L{CURRENT_POSITION} > 0 for long position
        - L{CURRENT_POSITION} < 0 for short position.
    @type CURRENT_POSITION: number

    @ivar MIN_TRADE_SIZE: This is a non-negative floating point number representing the
    minimal trade size in [MW] that can be executed in the market.
    The equivalent [MWh] minimal trade size is calculated as
        - t_s = L{DELIVERY_PERIOD}[0]
        - t_e = L{DELIVERY_PERIOD}[1]
        - minTradeSizeMWh [MWh] = MIN_TRADE_SIZE*sum(DISPATCH_PERIODS[t]; t in t_s..t_e) [MW*h].
    @type MIN_TRADE_SIZE: number
    
    @ivar MAX_TRADE_SIZE: Hypothetical upper limit trade size in [MW]
    in order to model a semi-continuous variables, such that
    for a binary variable b and a continuous variable s the following
    constraint hold:
        - b*MIN_TRADE_SIZE <= s <= b*MAX_TRADE_SIZE
    and therefore
        - s == 0, if b == 0, or
        - MIN_TRADE_SIZE <= s <= MAX_TRADE_SIZE, if b == 1.
    Note that MAX_TRADE_SIZE should not represent a real upper boundary to s
    but is used to force s <= 0, if b == 0.
    @type MAX_TRADE_SIZE: number (very large)
    
    @ivar CLIP_SIZE: This is a positive floating point number or None
    representing the standard product clip size in [MW] that
    can be executed in the market for quantities above the
    L{MIN_TRADE_SIZE}.
    If it is set to a positive number any quantity traded
    above the L{MIN_TRADE_SIZE} will have to be an integral multiple
    of the L{CLIP_SIZE}. If it is set to None it will be
    ignored and any quantity above the L{MIN_TRADE_SIZE}
    can be traded.
    The equivalent [MWh] clip size is calculated as
        - t_s = L{DELIVERY_PERIOD}[0]
        - t_e = L{DELIVERY_PERIOD}[1]
        - clipSizeMWh [MWh] = L{CLIP_SIZE}*sum(DISPATCH_PERIODS[t]; t in t_s..t_e) [MW*h]
    """
    def __init__(self,
                 name,
                 deliveryPeriod = (0, 0),
                 position = 0.0,
                 minTradeSize = 0.0,
                 clipSize = None,
                 discountFactor = None,
                 fwdCurveBid = None,
                 fwdCurveAsk = None,
                 srcs = None,
                 snks = None):
        
        super(StandardProduct, self).__init__( name,
                                               conditional( srcs is not None, srcs, [] ),
                                               conditional( srcs is not None, snks, [] ) )
        # @todo: do we need special list holding
        # TradeTranche objects passed in lists of srcs and snks?
        
        self.set_DELIVERY_PERIOD( deliveryPeriod )
        self.CURRENT_POSITION = position
        self.MIN_TRADE_SIZE = minTradeSize
        self.MAX_TRADE_SIZE = __very_large_positive_number__
        self.CLIP_SIZE = clipSize

        self.set_DISCOUNT_FACTOR( discountFactor )
        self.set_FWD_CURVE_BID( fwdCurveBid )
        self.set_FWD_CURVE_ASK( fwdCurveAsk )

        self.long_position = numpy.empty( 0, dtype='object' )
        self.shrt_position = numpy.empty( 0, dtype='object' )

        self.long_semi_cont_trigger = None
        self.shrt_semi_cont_trigger = None
        
        self.long_clip_count = None
        self.shrt_clip_count = None


    def set_DELIVERY_PERIOD(self, value):
        if len(value) != 2:
            raise ValueError, "deliveryPeriod: not a tuple of 2 elements"
        if value[1] < value[0]:
            raise ValueError, "delvieryPeriod: end dispatch period idx < start dispatch period idx"
        self.DELIVERY_PERIOD = value


    def set_DISCOUNT_FACTOR(self, value):
        self.DISCOUNT_FACTOR = conditional( value is None, 1.0, value )


    def set_FWD_CURVE_BID(self, value):
        self.FWD_CURVE_BID = conditional( value is None, 24.0, value )
        
    
    def set_FWD_CURVE_ASK(self, value):
        self.FWD_CURVE_ASK = conditional( value is None, 26.0, value )


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
        super(StandardProduct, self).set_DISPATCH_PERIODS( dispatchPeriods )
        
        nSteps = len( self.DISPATCH_PERIODS )
        
        if self.DELIVERY_PERIOD[0] not in range( nSteps ):
            raise ValueError, "deliveryPeriod: start index %d is not a valid index into dispatch periods ('%s')" % (self.DELIVERY_PERIOD[0], self.name) 
        if self.DELIVERY_PERIOD[1] not in range( nSteps ):
            raise ValueError, "deliveryPeriod: end index %d is not a valid index into dispatch periods ('%s')" % (self.DELIVERY_PERIOD[1], self.name)

        self.DISCOUNT_FACTOR = \
            self.create_coefficient_array( self.DISCOUNT_FACTOR,
                                           nSteps,
                                           "Length of 'discountFactor' must match length of 'dispatchPeriods'" )
        self.FWD_CURVE_BID = \
            self.create_coefficient_array( self.FWD_CURVE_BID,
                                           nSteps,
                                           "Length of 'fwdCurveBid' must match length of 'dispatchPeriods'" )
        self.FWD_CURVE_ASK = \
            self.create_coefficient_array( self.FWD_CURVE_ASK,
                                           nSteps,
                                           "Length of 'fwdCurveAsk' must match length of 'dispatchPeriods'" )


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
        super(StandardProduct, self).create_lp_vars( prefix )
        
        nSteps = len( self.DISPATCH_PERIODS )
        
        self.long_position = numpy.array( pulp.LpVariable.matrix( prefix + self.name + "_long_pos", range( nSteps ),
                                                                  lowBound = 0.0 ) )
        self.shrt_position = numpy.array( pulp.LpVariable.matrix( prefix + self.name + "_shrt_pos", range( nSteps ),
                                                                  lowBound = 0.0 ) )

        self.long_semi_cont_trigger = pulp.LpVariable( prefix + self.name + "_long_semi_cont_trig",
                                                       lowBound = 0.0, upBound = 1.0, cat = pulp.LpInteger )
        self.shrt_semi_cont_trigger = pulp.LpVariable( prefix + self.name + "_shrt_semi_cont_trig",
                                                       lowBound = 0.0, upBound = 1.0, cat = pulp.LpInteger )
        
        self.long_clip_count = pulp.LpVariable( prefix + self.name + "_long_clip_cnt",
                                                lowBound = 0.0, cat = pulp.LpInteger )
        self.shrt_clip_count = pulp.LpVariable( prefix + self.name + "_shrt_clip_cnt",
                                                lowBound = 0.0, cat = pulp.LpInteger )

        
    def create_model(self, prefix=""):
        """
        The dynamics of the standard product is as follows:

        The L{StandardProduct} model assumes that on the one
        hand it is linked to a L{Market} L{Entity} (as source
        and sink) and to one or more L{TradeTranche} L{Entity}(s)
        (each as a sink and a source). Furthermore, the
        L{StandardProduct} holds an array of L{position}
        L{pulp.LpVariable}(s) of size len(L{DISPATCH_PERIODS}).
        Given that the
            - sum(src.out_flow[t], src in srcList) == L{in_flow}[t], and
            - sum(snk.in_flow[t], snk in snkList) == L{out_flow}[t], for all t in L{DISPATCH_PERIODS}
        (see method L{Entity.create_model}) the following
        additional constraints must hold:
            - Inflow/outflow restricted to standard product's delivery period:
                - Restricted inflow volumes:
                L{in_flow}[t] [MWh] == 0, for t not in L{DELIVERY_PERIOD}
                - Restricted outflow volumes:
                L{out_flow}[t] [MWh] == 0, for t not in L{DELIVERY_PERIOD}
            - Transacted (sold: L{position}[t] < 0; purchased: L{position}[t] > 0)
            gas position in [MW]:
                - Inflow/outflow balance equations:
                L{position}[t]*DISPATCH_PERIODS[t] [MW*h] == L{CURRENT_POSITION}*DISPATCH_PERIODS[t] [MW*h] + L{out_flow}[t] [MWh] - L{in_flow}[t] [MWh],
                for all t in L{DISPATCH_PERIODS},
                i.e., if we sell then L{in_flow}[t] > L{out_flow}[t] and hence,
                L{position}[t] < 0,
                if we buy then L{out_flow}[t] > L{in_flow}[t] and L{position}[t] > 0,
                L{position}[t] == 0, otherwise.
                - Delivery period volume equations:
                L{position}[t] [MWh] == L{position}[u] [MWh], for all t, u in L{DELIVERY_PERIOD}
            - Sales (L{position} < 0) gas position in [MW]:
                - Non-negativity constraints:
                L{shrt_position}[t] [MW] >= 0, for all t in L{DISPATCH_PERIODS}
                (see variable construction in method L{create_lp_vars}).
                - Sales position constraints:
                L{shrt_position}[t] [MW] >= -L{position}[t] [MW], for all t in L{DISPATCH_PERIODS}
                - Minimum trade size constraint:
                    - sum(L{shrt_position}[t]*L{DISPATCH_PERIODS}[t], t in L{DELIVERY_PERIOD}) [MW*h] >=
                    L{shrt_semi_cont_trigger}*L{MIN_TRADE_SIZE}*sum(L{DISPATCH_PERIODS}[t], t in L{DELIVERY_PERIOD}) [MW*h],
                    - sum(L{shrt_position}[t]*L{DISPATCH_PERIODS}[t], t in L{DELIVERY_PERIOD}) [MW*h] <=
                    L{shrt_semi_cont_trigger}*L{MAX_TRADE_SIZE}*sum(L{DISPATCH_PERIODS}[t], t in L{DELIVERY_PERIOD}) [MW*h],
                where L{shrt_semi_cont_trigger} is a binary variable (i.e., is L{pulp.LpInteger}, 0 <= L{shrt_semi_cont_trigger} <= 1)
                (--> semi-continuous)
            - Purchase (L{position} > 0) gas position in [MW]:
                - Non-negativity constraints:
                L{long_position}[t] [MW] >= 0, for all t in L{DISPATCH_PERIODS}
                (see variable construction in method L{create_lp_vars}).
                - Purchase position constraints:
                L{long_position}[t] [MW] >= L{position}[t] [MW], for all t in L{DISPATCH_PERIODS}
                - Minimum trade size constraint:
                    - sum(L{long_position}[t]*L{DISPATCH_PERIODS}[t], t in L{DELIVERY_PERIOD}) [MW*h] >=
                    L{long_semi_cont_trigger}*L{MIN_TRADE_SIZE}*sum(L{DISPATCH_PERIODS}[t], t in L{DELIVERY_PERIOD}) [MW*h],
                    - sum(L{long_position}[t]*L{DISPATCH_PERIODS}[t], t in L{DELIVERY_PERIOD}) [MW*h] <=
                    L{long_semi_cont_trigger}*L{MAX_TRADE_SIZE}*sum(DISPATCH_PERIODS[t], t in L{DELIVERY_PERIOD}) [MW*h],
                where L{long_semi_cont_trigger} is a binary variable (i.e., is L{pulp.LpInteger}, 0 <= L{shrt_semi_cont_trigger} <= 1)
                (--> semi-continuous)
            - Exclusivity constraint:
                L{shrt_semi_cont_trigger} + L{long_semi_cont_trigger} <= 1, (only one of the variables can be one, redundant constraint)
            - Clip size constraints (if CLIP_SIZE is not None):
                - sum(L{shrt_position}[t]*L{DISPATCH_PERIODS}[t], t in L{DELIVERY_PERIOD}) [MW*h] ==
                L{shrt_semi_cont_trigger}*L{MIN_TRADE_SIZE}*sum(L{DISPATCH_PERIODS}[t], t in L{DELIVERY_PERIOD}) [MW*h] +
                L{shrt_clip_count}*L{CLIP_SIZE}*sum(DISPATCH_PERIODS[t], t in L{DELIVERY_PERIOD}) [MW*h]  
                - sum(L{long_position}[t]*L{DISPATCH_PERIODS}[t], t in L{DELIVERY_PERIOD}) [MW*h] ==
                L{long_semi_cont_trigger}*L{MIN_TRADE_SIZE}*sum(DISPATCH_PERIODS[t], t in L{DELIVERY_PERIOD}) [MW*h] +
                L{long_clip_count}*L{CLIP_SIZE}*sum(DISPATCH_PERIODS[t], t in L{DELIVERY_PERIOD}) [MW*h]
        """
        super(StandardProduct, self).create_model( prefix )

        nSteps = len( self.DISPATCH_PERIODS )
        deliveryPeriodIdx = [t for t in xrange( nSteps ) if self.DELIVERY_PERIOD[0] <= t and t <= self.DELIVERY_PERIOD[1]]
        nonDeliveryPeriodIdx = [t for t in xrange( nSteps ) if t < self.DELIVERY_PERIOD[0] or t > self.DELIVERY_PERIOD[1]]
        
        ttran_src_list = [src for src in self.src_list if isinstance( src, ttranche.TradeTranche )]
        ttran_snk_list = [snk for snk in self.snk_list if isinstance( snk, ttranche.TradeTranche )]

        other_src_list = [src for src in self.src_list if not isinstance( src, ttranche.TradeTranche )]
        other_snk_list = [snk for snk in self.snk_list if not isinstance( snk, ttranche.TradeTranche )]

        # In-/Out-flow volume for non-delivery period:
        for t in nonDeliveryPeriodIdx:
            self.constraint_list.append( self.in_flow[t] == 0.0 )
            self.constraint_list.append( self.out_flow[t] == 0.0 )
            self.constraint_list.append( self.long_position[t] == 0.0 )
            self.constraint_list.append( self.shrt_position[t] == 0.0 )

        for t in deliveryPeriodIdx:
            if len( ttran_src_list ) > 0 and len( other_snk_list ) > 0:
                self.constraint_list.append( pulp.lpSum( [src.out_flow[t] for src in ttran_src_list] )
                                             >= pulp.lpSum( [snk.in_flow[t] for snk in other_snk_list] ) )
            if len( other_src_list ) > 0 and len( ttran_snk_list ) > 0:
                self.constraint_list.append( pulp.lpSum( [src.out_flow[t] for src in other_src_list] )
                                             >= pulp.lpSum( [snk.in_flow[t] for snk in ttran_snk_list] ) )
            
        # Transacted volume:
        for t in deliveryPeriodIdx:
            #                             [MW]                    [MW]                   [h]                         [MWh]
            self.constraint_list.append( (self.long_position[t] - self.CURRENT_POSITION)*self.DISPATCH_PERIODS[t] == self.in_flow[t] )
            self.constraint_list.append( (self.shrt_position[t] + self.CURRENT_POSITION)*self.DISPATCH_PERIODS[t] == self.out_flow[t] )
            
        ## Delivery period volume equations: ONLY EXECUTE IF DELIVERY PERIOD > 1 DISPATCH_PERIOD!
        for t in xrange( self.DELIVERY_PERIOD[0], self.DELIVERY_PERIOD[1] ):
            # Require uniform position over whole standard product delivery period 
            self.constraint_list.append( self.long_position[t] == self.long_position[t + 1] )
            self.constraint_list.append( self.shrt_position[t] == self.shrt_position[t + 1] )

        # From now on positions of delivery period are linked and uniform.
        # Use first delivery sub-period as proxy-period.
        proxy_t = self.DELIVERY_PERIOD[0]
            
        if self.MIN_TRADE_SIZE > 0.0:
            # Sales volume:
            ## Sales position constraints:
            ## Minimum trade size constraint:
            self.constraint_list.append( self.long_position[proxy_t] >= self.long_semi_cont_trigger*self.MIN_TRADE_SIZE )
            self.constraint_list.append( self.long_position[proxy_t] <= self.long_semi_cont_trigger*self.MAX_TRADE_SIZE )
            # Purchase position:
            ## Purchase position constraints:
            ## Minimum trade size constraint:
            self.constraint_list.append( self.shrt_position[proxy_t] >= self.shrt_semi_cont_trigger*self.MIN_TRADE_SIZE )
            self.constraint_list.append( self.shrt_position[proxy_t] <= self.shrt_semi_cont_trigger*self.MAX_TRADE_SIZE )

            if self.CLIP_SIZE is not None:
                self.constraint_list.append( self.long_position[proxy_t] == self.long_semi_cont_trigger*self.MIN_TRADE_SIZE + self.long_clip_count*self.CLIP_SIZE )
                self.constraint_list.append( self.shrt_position[proxy_t] == self.shrt_semi_cont_trigger*self.MIN_TRADE_SIZE + self.shrt_clip_count*self.CLIP_SIZE )
        else:
            # Clip size:
            if self.CLIP_SIZE is not None:
                self.constraint_list.append( self.long_position[proxy_t] == self.long_clip_count*self.CLIP_SIZE )
                self.constraint_list.append( self.shrt_position[proxy_t] == self.shrt_clip_count*self.CLIP_SIZE )
            
        all_srcs_markets = True
        for src in self.src_list:
            if not isinstance( src, market.Market ):
                all_srcs_markets = False
                break
                
        all_snks_markets = True
        for snk in self.snk_list:
            if not isinstance( snk, market.Market ):
                all_snks_markets = False
                break
            
        if all_srcs_markets and all_snks_markets:
            self.objective_list.append(  pulp.lpSum( [self.long_position[t]*self.DISPATCH_PERIODS[t]*self.FWD_CURVE_BID[t]*self.DISCOUNT_FACTOR[t] for t in deliveryPeriodIdx] ) )
            self.objective_list.append( -pulp.lpSum( [self.shrt_position[t]*self.DISPATCH_PERIODS[t]*self.FWD_CURVE_ASK[t]*self.DISCOUNT_FACTOR[t] for t in deliveryPeriodIdx] ) )
        else:
            # Inflow/outflow balance equation:
            for t in deliveryPeriodIdx:
                self.constraint_list.append( self.in_flow[t] == self.out_flow[t] )


    def get_lp_vars(self):
        """
        """
        return super(StandardProduct, self).get_lp_vars()\
            + self.long_position.tolist()\
            + self.shrt_position.tolist()\
            + [ self.long_semi_cont_trigger,\
                self.shrt_semi_cont_trigger,\
                self.long_clip_count,\
                self.shrt_clip_count ]
                

if __name__ == "__main__":
    print conditional(True, "Yes", "Nope")
    print conditional(False, "Yes", "Nope")
