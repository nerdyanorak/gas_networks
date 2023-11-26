"""L{Market} gas network L{Entity}"""
import numpy
import pulp

#from src.entities.entity import Entity
#from src.utils.util import conditional
import entity
import storage
import stdprod
import ttranche

from utils.util import conditional

class Market(entity.Entity):
    """
    The L{Market} entity's sole role is to
    balance the sum of all in flows with the
    sum of all out flows. Typically, the L{Market}
    entity is linked to many L{StandardProduct}
    entities covering the entire L{DISPATCH_PERIODS}
    with their delivery periods and to one or more
    other entities that have some optimisation
    potential (such as a Storage, Supplier, Consumer).
    In most cases, all entities the L{Market} entity
    is linked with are linked as source entity as
    well as sink entity (but other constellations
    are possible).
    
    In order to construct a L{Market} entity that supports
    volume dependent bid/ask price spreads the L{Market}
    entity links, for each standard product delivery period,
    to a corresponding L{StandardProduct} entity, that itself
    links to multiple L{TradeTranche} entities that have
        - restricted capacity limits, and
        - a widening spread between bid/ask prices.
    This will cause the optimiser to transact volumes for
    the given standard product first at the most favourable
    trade tranche up to its upper capacity limit, before the
    second most favourable trade tranche is considered, etc.
    The least favourable trade tranche shouldn't have an upper
    capacity limit set and have a punishing bid/ask price spread
    and serves as so called 'slack' tranche.  

    @todo: Add features to the L{Market} entity that allows
    check for validity of all linked to source and sink entities,
    such as:
        - test the L{DISPATCH_PERIODS} are fully covered by
        L{StandardProduct} delivery periods
        - test that L{StandardProduct} delivery periods do not
        overlap (in a first instance, later this restriction
        may have to be relaxed)
    """
    def __init__(self,
                 name,
                 discountFactor = None,
                 fwdCurveBid = None,
                 fwdCurveAsk = None,
                 srcs = None,
                 snks = None):
        """
        """
        super(Market, self).__init__( name,
                                      conditional( srcs is not None, srcs, [] ),
                                      conditional( snks is not None, snks, [] ) )

        self.set_DISCOUNT_FACTOR( discountFactor )
        self.set_FWD_CURVE_BID( fwdCurveBid )
        self.set_FWD_CURVE_ASK( fwdCurveAsk )

    def set_DISCOUNT_FACTOR(self, value):
        self.DISCOUNT_FACTOR = conditional( value is None, 1.0, value )


    def set_FWD_CURVE_BID(self, value):
        self.FWD_CURVE_BID = conditional( value is None, 24.0, value )
        
    
    def set_FWD_CURVE_ASK(self, value):
        self.FWD_CURVE_ASK = conditional( value is None, 26.0, value )


    def set_DISPATCH_PERIODS(self, dispatchPeriods):
        """
        """
        super(Market, self).set_DISPATCH_PERIODS( dispatchPeriods )
        
        nSteps = len(self.DISPATCH_PERIODS)
        nPoints = nSteps + 1

        self.DISCOUNT_FACTOR = self.create_coefficient_array( self.DISCOUNT_FACTOR,
                                                              nSteps,
                                                              "Length of 'discountFactor' must match length of 'dispatchPeriods'" )
        self.FWD_CURVE_BID = self.create_coefficient_array( self.FWD_CURVE_BID,
                                                            nSteps,
                                                            "Length of 'fwdCurveBid' must match length of 'dispatchPeriods'" )
        self.FWD_CURVE_ASK = self.create_coefficient_array( self.FWD_CURVE_ASK,
                                                            nSteps,
                                                            "Length of 'fwdCurveAsk' must match length of 'dispatchPeriods'")
        

    def create_model(self, prefix=""):
        """
        """
        super(Market, self).create_model( prefix )

        nSteps = len( self.DISPATCH_PERIODS )
        
        sprod_src_list = [src for src in self.src_list if isinstance( src, stdprod.StandardProduct )]
        sprod_snk_list = [snk for snk in self.snk_list if isinstance( snk, stdprod.StandardProduct )]
        
        other_src_list = [src for src in self.src_list if not isinstance( src, stdprod.StandardProduct )]
        other_snk_list = [snk for snk in self.snk_list if not isinstance( snk, stdprod.StandardProduct )]

        for t in xrange( nSteps ):
            if len( sprod_src_list ) > 0 and len( other_snk_list ) > 0:
                self.constraint_list.append( pulp.lpSum( [src.out_flow[t] for src in sprod_src_list] )
                                             >= pulp.lpSum( [snk.in_flow[t] for snk in other_snk_list] ) )
            if len( other_src_list ) > 0 and len( sprod_snk_list ) > 0:
                self.constraint_list.append( pulp.lpSum( [src.out_flow[t] for src in other_src_list] )
                                             >= pulp.lpSum( [snk.in_flow[t] for snk in sprod_snk_list] ) )
        
        all_srcs_storages = True
        for src in self.src_list:
            if not isinstance( src, storage.Storage ):
                all_srcs_storages = False
                break
                
        all_snks_storages = True
        for snk in self.snk_list:
            if not isinstance( snk, storage.Storage ):
                all_snks_storages = False
                break
        
        if all_srcs_storages and all_snks_storages:
            self.objective_list.append(  pulp.lpSum( [self.in_flow[t] *self.FWD_CURVE_BID[t]*self.DISCOUNT_FACTOR[t] for t in xrange( nSteps )] ) )
            self.objective_list.append( -pulp.lpSum( [self.out_flow[t]*self.FWD_CURVE_ASK[t]*self.DISCOUNT_FACTOR[t] for t in xrange( nSteps )] ) )
        else:
            # Inflow/outflow balance equation:
            for t in xrange( nSteps ):
                self.constraint_list.append( self.in_flow[t] == self.out_flow[t] )

            
if __name__ == "__main__":
    print conditional(True, "Yes", "Nope")
    print conditional(False, "Yes", "Nope")
