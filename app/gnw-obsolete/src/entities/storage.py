"""L{Storage} gas network L{Entity}"""
import pulp
import numpy

#from src.entities.entity import Entity
#from src.utils.util import conditional
import entity
from utils.util import conditional
#
class Storage(entity.Entity):
    """
    Class implements a simple storage where injection/release volumes
    are only restricted by possible (time dependent) minimal and
    maximal storage level constraints as well as (time dependent)
    maximal injection and release capacity limits.
    An (time dependent) injection and/or a release cost (potentially
    zero) is is charged for each unit of volume of gas injected and/or
    released, respectively, from the storage.
    
    For the dynamics of the storage see Class instance method
    L{create_model(self, prefix="")}.
    
    Note: In order to make the storage object independent from as many
    absolute volumes as possible all time dependent storage constraints
    limit inputs have to be provided in percentage [%] terms relative to
    L{NOMINAL_WGV},
    L{NOMINAL_INJ_CAPACITY}, and
    L{NOMINAL_REL_CAPACITY}, respectively. This means the size
    of the storage can be changed, without changing its operational
    dynamics, by only changeing the value for L{NOMINAL_WGV}.  

    @ivar name: unique entity name
    @type name: L{str}
    
    @ivar NOMINAL_WGV: working gas volume in [MWh]
    @type NOMINAL_WGV: number
    
    @ivar NOMINAL_INJ_CAPACITY: nominal injection capacity in [MW]
    @type NOMINAL_INJ_CAPACITY: number
    
    @ivar NOMINAL_REL_CAPACITY: nominal release capacity in [MW]
    @type NOMINAL_REL_CAPACITY: number
    
    @ivar START_STORAGE_LEVEL_PCT: starting volume in % of L{NOMINAL_WGV}
    @type START_STORAGE_LEVEL_PCT: number
    
    @ivar FINAL_STORAGE_LEVEL_PCT: ending volume in % of L{NOMINAL_WGV}
    @type FINAL_STORAGE_LEVEL_PCT: number
    
    @ivar src: source L{Entity} object, i.e., where the inflow is coming from
    @type src: L{Entity}
    
    @ivar snk: sink L{Entity} object, i.e., where the outflow is going to
    @type snk: L{Entity}
    
    @ivar MAX_LEV_PCT: array of size len(L{DISPATCH_PERIODS}) + 1 holding the
    maximal admissible storage level in % of L{NOMINAL_WGV} at the start
    of each dispatch period t.
    @type MAX_LEV_PCT: L{numpy.ndarray} of dtype='double'
    
    @ivar MIN_LEV_PCT: array of size len(L{DISPATCH_PERIODS}) + 1 holding the
    minimal admissible storage level in % of L{NOMINAL_WGV} at the start
    of each dispatch period t.
    @type MIN_LEV_PCT: L{numpy.ndarray} of dtype='double'
    
    @ivar MAX_INJ_CAPACITY_PCT: array of size len(L{DISPATCH_PERIODS}) holding the
    maximal available injection capacity as a % of L{NOMINAL_INJ_CAPACITY} assuming
    an injection rate of 100% for each dispatch period t.
    Depending on actual storage level the injection rate may be less than 100%.
    @type MAX_INJ_CAPACITY_PCT: L{numpy.ndarray} of dtype='double'
    
    @ivar MAX_REL_CAPACITY_PCT: array of size len(L{DISPATCH_PERIODS}) holding the
    maximal available release capacity as a % of L{NOMINAL_REL_CAPACITY} assuming
    an release rate of 100% for each dispatch period t.
    Depending on storage level the release rate may be less than 100%.
    @type MAX_REL_CAPACITY_PCT: L{numpy.ndarray} of dtype='double'
    
    @ivar lev_pct: array of constraint expression of size
    len(L{DISPATCH_PERIODS}) representing the current storage level
    as % of L{NOMINAL_WGV} at each dispatch period t.
    @type lev_pct: L{numpy.ndarray} of dtype='object'\
    where object is L{pulp.LpAffineExpression}
    
    @ivar q_dsp_pct: array of decision variables of size
    len(L{DISPATCH_PERIODS}) representing the dispatched gas volume as a % of the
    L{NOMINAL_WGV} for each dispatch period t.
    If L{q_dsp_pct}[t] > 0 we inject gas into storage.
    If L{q_dsp_pct}[t] < 0 we release gas from storage.
    @type q_dsp_pct: L{numpy.ndarray} of dtype='object'\
    where object is L{pulp.LpVariable}.
    
    @ivar INJ_COST: array of cost of size len(L{DISPATCH_PERIODS})
    for injection one [MWh] of gas into the storage.
    @type INJ_COST: L{numpy.ndarray} of dtype='double'
    
    @ivar REL_COST: array of cost of size len(L{DISPATCH_PERIODS})
    for release of one [MWh] of gas from the storage.
    @type REL_COST: L{numpy.ndarray} of dtype='double'
    
    @ivar DISCOUNT_FACTOR: array of cost of size len(L{DISPATCH_PERIODS})
    containing the discount factors to be used for cash flows from dispatch
    costs arising during each given dispatch period. This means that
    DISCOUNT_FACTOR[t] doesn't necessarily need to be the discount factor
    for cash flows payed at the end of DISPATCH_PERIOD[t] but some other
    point in time (for example settlement date of standard product its
    delivery period includes given dispatch period DISPATCH_PERIODS[t])
    @type DISCOUNT_FACTOR: L{numpy.ndarray} of dtype='double'  
    
    @ivar q_inj_pct: array of decision variables of size
    len({DISPATCH_PERIODS}) representing the injected gas volume as
    a % of L{NOMINAL_WGV} at each dispatch period t. I.e.,
        - L{q_inj_pct}[t] >= L{q_dsp_pct}[t]
    @type q_inj_pct: L{numpy.ndarray} of dtype='object'\    
    where object is L{pulp.LpVariable}
    
    @ivar q_rel_pct: array of decision variable of size
    len({DISPATCH_PERIODS}) representing the released gas volume as
    a % of L{NOMINAL_WGV} at each dispatch period t. I.e.,
        - L{q_rel_pct}[t] >= -L{q_dsp_pct}[t]
    @type q_rel_pct: L{numpy.ndarray} of dtype='object'\    
    where object is L{pulp.LpVariable}
    """
    def __init__(self,
                 name,
                 nominalWorkingGasVolume,
                 nominalInjectionCapacity,
                 nominalReleaseCapacity,
                 startStorageLevelPct,
                 endStorageLevelPct = None,
                 maxStorageLevelPct = None,
                 minStorageLevelPct = None,
                 maxInjectionCapacityPct = None,
                 maxReleaseCapacityPct = None,
                 injectionCost = None,
                 releaseCost = None,
                 discountFactor = None,
                 fwdCurveBid = None,
                 fwdCurveAsk = None,
                 src = None,
                 snk = None):
        """
        @param name:        uniqe, non-empty name string of entity
        @type name:         L{str}
        
        @param nominalWorkingGasVolume: working gas volume in [MWh]
        @type nominalWorkingGasVolume: number
        
        @param nominalInjectionCapacity: nominal injection capacity in [MW]
        @type nominalInjectionCapacity: number
        
        @param nominalReleaseCapacity: nominal release capacity in [MW]
        @type nominalReleaseCapacity: number
        
        @param startStorageLevelPct: starting volume in % of L{nominalWorkingGasVolume}
        @type startStorageLevelPct: number
        
        @param endStorageLevelPct: ending volume in % of L{nominalWorkingGasVolume}
        @type endStorageLevelPct: number
        
        @param maxStorageLevelPct: a non-negative number or an array of size
        len(L{DISPATCH_PERIODS}) + 1 holding the maximal admissible storage
        level in % of L{nominalWorkingGasVolume} at the start of each dispatch
        period t.
        @type maxStorageLevelPct: number, L{numpy.ndarray} of dtype='double'
        
        @param minStorageLevelPct: a non-negative number or an array of size
        len(L{DISPATCH_PERIODS}) + 1 holding the minimal admissible storage
        level in % of L{nominalWorkingGasVolume} at the start of each dispatch
        period t.
        @type minStorageLevelPct: number, L{numpy.ndarray} of dtype='double'
        
        @param maxInjectionCapacityPct: a non-negative number or an array of size
        len(L{DISPATCH_PERIODS}) holding the maximal available injection capacity
        as a % of L{nominalInjectionCapacity} assuming an injection rate of 100%
        for each dispatch period t.
        Depending on actual storage level the injection rate may be less than 100%.
        @type maxInjectionCapacityPct: number, L{numpy.ndarray} of dtype='double'
        
        @param maxReleaseCapacityPct: a non-negative number or an array of size
        len(L{DISPATCH_PERIODS}) holding the maximal available release capacity
        as a % of L{nominalReleaseCapacity} assuming an release rate of 100%
        for each dispatch period t.
        Depending on storage level the release rate may be less than 100%.
        @type maxReleaseCapacityPct: number, L{numpy.ndarray} of dtype='double'
        
        @param injectionCost: a number or an array of cost of size
        len(L{DISPATCH_PERIODS}) for injection of one [MWh] of gas
        into the storage.
        @type injectionCost: number, L{numpy.ndarray} of dtype='double'
        
        @param releaseCost: a number array of cost of size
        len(L{DISPATCH_PERIODS}) for release of one [MWh] of gas
        from the storage.
        @type releaseCost: number, L{numpy.ndarray} of dtype='double'
    
        @param discountFactor: a number array of discount factors of size
        len(L{DISPATCH_PERIODS}).
        @type discountFactor: number, L{numpy.ndarray} of dtype='double'

        @param src:         source entity object
        @type src:          L{Entity}
        
        @param snk:         sink entity object
        @type snk:          L{Entity}
        """
        super(Storage, self).__init__( name,
                                       conditional(src is not None, [src], []),
                                       conditional(snk is not None, [snk], []) )
        
        self.NOMINAL_WGV = nominalWorkingGasVolume
        self.NOMINAL_INJ_CAPACITY = nominalInjectionCapacity
        self.NOMINAL_REL_CAPACITY = nominalReleaseCapacity
        self.START_STORAGE_LEVEL_PCT = startStorageLevelPct
        self.FINAL_STORAGE_LEVEL_PCT = endStorageLevelPct
        
#        self.MAX_LEV_PCT = numpy.array( [], dtype='double' )
        self.set_MAX_LEV_PCT( maxStorageLevelPct ) 
#        self.MIN_LEV_PCT = numpy.array( [], dtype='double' )
        self.set_MIN_LEV_PCT( minStorageLevelPct )
#        self.MAX_INJ_CAPACITY_PCT = numpy.array( [], dtype='double' )
        self.set_MAX_INJ_CAPACITY_PCT( maxInjectionCapacityPct )
#        self.MAX_REL_CAPACITY_PCT = numpy.array( [], dtype='double' )
        self.set_MAX_REL_CAPACITY_PCT( maxReleaseCapacityPct )
#        self.INJ_COST = numpy.array( [], dtype='double' )
        self.set_INJ_COST( injectionCost )
#        self.REL_COST = numpy.array( [], dtype='double' )
        self.set_REL_COST( releaseCost )
#        self.DISCOUNT_FACTOR = numpy.array( [], dtype='double' )
        self.set_DISCOUNT_FACTOR( discountFactor )
        self.set_FWD_CURVE_BID( fwdCurveBid )
        self.set_FWD_CURVE_ASK( fwdCurveAsk )
        
        self.lev_pct = numpy.empty( 0, dtype='object' )

        self.q_inj_pct = numpy.empty( 0, dtype='object' )
        self.q_rel_pct = numpy.empty( 0, dtype='object' )


    def set_MAX_LEV_PCT(self, value):
        self.MAX_LEV_PCT = conditional( value is None, 1.0, value )


    def set_MIN_LEV_PCT(self, value):
        self.MIN_LEV_PCT = conditional( value is None, 0.0, value )


    def set_MAX_INJ_CAPACITY_PCT(self, value):
        self.MAX_INJ_CAPACITY_PCT = conditional( value is None, 1.0, value )


    def set_MAX_REL_CAPACITY_PCT(self, value):
        self.MAX_REL_CAPACITY_PCT = conditional( value is None, 1.0, value )


    def set_INJ_COST(self, value):
        self.INJ_COST = conditional( value is None, 0.0, value )


    def set_REL_COST(self, value):
        self.REL_COST = conditional( value is None, 0.0, value )


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
        length and initialise with some meaningful
        defaults, if they haven't been set appropriately 
        beforehand (using __init__(...) or setters).
        If coefficient arrays have already been set check
        for appropriate size (and values?).
        
        @param dispatchPeriods: array of dispatch periods
        defining the overall optimisation horizon as well
        as the individual duration of each dispatch period.
        @type dispatchPeriods: L{numpy.ndarray} of dtype='double'
        """
        super(Storage, self).set_DISPATCH_PERIODS( dispatchPeriods )
        
        nSteps = len(self.DISPATCH_PERIODS)
        nPoints = nSteps + 1
        
        self.MAX_LEV_PCT = \
            self.create_coefficient_array( self.MAX_LEV_PCT,
                                           nPoints,
                                           "Length of 'maxStorageLevelPct' must match length of 'dispatchPeriods' + 1" )
        self.MIN_LEV_PCT = \
            self.create_coefficient_array( self.MIN_LEV_PCT,
                                           nPoints,
                                           "Length of 'minStorageLevelPct' must match length of 'dispatchPeriods' + 1" )
        self.MAX_INJ_CAPACITY_PCT = \
            self.create_coefficient_array( self.MAX_INJ_CAPACITY_PCT,
                                           nSteps,
                                           "Length of 'maxInjectionCapacityPct' must match length of 'dispatchPeriods'" )
        self.MAX_REL_CAPACITY_PCT = \
            self.create_coefficient_array( self.MAX_REL_CAPACITY_PCT,
                                           nSteps,
                                           "Length of 'maxReleaseCapacityPct' must match length of 'dispatchPeriods'" )
        self.INJ_COST = \
            self.create_coefficient_array( self.INJ_COST,
                                           nSteps,
                                           "Length of 'injectionCost' must match length of 'dispatchPeriods'" )
        self.REL_COST = \
            self.create_coefficient_array( self.REL_COST,
                                           nSteps,
                                           "Length of 'releaseCost' must match length of 'dispatchPeriods'" )
        self.DISCOUNT_FACTOR = \
            self.create_coefficient_array( self.DISCOUNT_FACTOR,
                                           nSteps,
                                           "Length of 'discountFactor' must match length of 'dispatchPeriods'" )
        self.FWD_CURVE_BID = \
            self.create_coefficient_array( self.FWD_CURVE_BID,
                                           nSteps,
                                           "Length of 'fwdCurveBid' must match length of 'dispatchPeriods'" )
        self.FWD_CURVE_ASK =\
            self.create_coefficient_array( self.FWD_CURVE_ASK,
                                           nSteps,
                                           "Length of 'fwdCurveAsk' must match length of 'dispatchPeriods'" )


    def create_lp_vars(self, prefix=""):
        """
        """
        super(Storage, self).create_lp_vars( prefix )
        
        nSteps = len( self.DISPATCH_PERIODS )
        nPoints = nSteps + 1
      
        self.q_inj_pct = numpy.array( pulp.LpVariable.matrix( prefix + self.name + "_q_inj_pct", range( nSteps ), lowBound = 0.0 ) )
        self.q_rel_pct = numpy.array( pulp.LpVariable.matrix( prefix + self.name + "_q_rel_pct", range( nSteps ), lowBound = 0.0 ) )
        self.lev_pct = numpy.array( pulp.LpVariable.matrix( prefix + self.name + "_lev_pct", range( nPoints ), lowBound = 0.0 ) )


    def create_model(self, prefix=""):
        """
        The dynamics of the storage are as follows:
            - storage level balance constraints:
                - storage_level[t] [MWh] == storage_level[t - 1] [MWh] + dispatch_volume[t] [MWh],
                for all t = 1..nPoints-1, and
                - storage_level[0] [MWh] == START_STORAGE_LEVEL [MWh],
                - storage_level[nPoints-1] [MWh] == FINAL_STORAGE_LEVEL [MWh] (if set)
            with nPoints = nSteps + 1 and nSteps the number of dispatch periods
            in the optimisation. This is equivalent to
            storage_level(t) [MWh] == storage_level[0] [MWh] + sum(dispatch_volume[i], i = 0..t) [MWh]
            - storage level limit constraints:
                - MIN_STORAGE_LEVEL[t] [MWh] <= storage_level[t] [MWh],
                - MAX_STORAGE_LEVEL[t] [MWh] >= storage_level[t] [MWh],
            for all t = 0..nPoints-1
            - injection/release capacity constraints: As decision variable
            dispatch_volume[t], for all t = 0..nSteps-1, is a free variable
            (i.e., not bounded from below by 0) a positive value represents
            injected gas volume and a negative value represents released
            gas volume. Therefore we must have
                - dispatch_volume[t] [MWh] <= MAX_INJECTION_CAPACITY[t]*DISPATCH_PERIOD[t] [MW*h], and
                - -dispatch_volume[t] [MWh] <= MAX_RELEASE_CAPACITY[t]*DISPATCH_PERIOD[t] [MW*h],
            for all t = 0..nSteps-1
            - inflow/outflow balance constraints:
                - disptach_volume[t] [MWh] == in_flow[t] [MWh] - out_flow[t] [MWh],
                for all t = 0..nSteps-1
            - injection/release cost components to be considered for
            in objective function (that we want to maximise):
                - injectionCost [EUR] := sum(injection_volume[i]*INJ_COST[i]*DISCOUNT_FACTOR[i], i = 0..nSteps-1) [MWh*EUR/MWh]
                - releaseCost [EUR] := sum(release_volume[i]*REL_COST[i]*DISCOUNT_FACTOR[i], i = 0..nSteps-1) [MWh*EUR/MWh]
            where
                - injection_volume[t] [MWh] >= dispatch_volume[t] [MWh],
                - release_volume[t] [MWh] >= -dispatch_volume[t] [MWh],
                - injection_volume[t], release_volume[t] >= 0,
            for all t = 0..nSteps-1
        """
        super(Storage, self).create_model( prefix )

        nSteps = len( self.DISPATCH_PERIODS )
        nPoints = nSteps + 1
        
        # Storage level balance constraints:
        for t in xrange( nPoints ):
            if t == 0 and self.START_STORAGE_LEVEL_PCT is not None:
                self.constraint_list.append( self.lev_pct[t] == self.START_STORAGE_LEVEL_PCT )
            else:
                self.constraint_list.append( self.lev_pct[t] == self.lev_pct[t - 1] + self.q_inj_pct[t - 1] - self.q_rel_pct[t - 1] )
            if t == nPoints - 1 and self.FINAL_STORAGE_LEVEL_PCT is not None:
                self.constraint_list.append( self.lev_pct[t] == self.FINAL_STORAGE_LEVEL_PCT )

        # Storage level limit constraints:
        for t in xrange( nPoints ):
            self.constraint_list.append( self.lev_pct[t] >= self.MIN_LEV_PCT[t] )
            self.constraint_list.append( self.lev_pct[t] <= self.MAX_LEV_PCT[t] )

        # Injection/release capacity constraints:
        for t in xrange( nSteps ):
            #                            [%]                         *[MWh]               [%]                               *[MW]                            [h]                                
            self.constraint_list.append( self.q_inj_pct[t]*self.NOMINAL_WGV <= self.MAX_INJ_CAPACITY_PCT[t]*self.NOMINAL_INJ_CAPACITY*self.DISPATCH_PERIODS[t] )
            self.constraint_list.append( self.q_rel_pct[t]*self.NOMINAL_WGV <= self.MAX_REL_CAPACITY_PCT[t]*self.NOMINAL_REL_CAPACITY*self.DISPATCH_PERIODS[t] )

        # Inflow/outflow balance constraints:
        for t in xrange( nSteps ):
            #                            [%]              *[MWh]               [MWh]
            self.constraint_list.append( self.q_inj_pct[t]*self.NOMINAL_WGV == self.in_flow[t] )
            self.constraint_list.append( self.q_rel_pct[t]*self.NOMINAL_WGV == self.out_flow[t] )

        # Injection/Release cost
        self.objective_list.append( -pulp.lpSum( [self.q_inj_pct[t]*self.NOMINAL_WGV*self.INJ_COST[t]*self.DISCOUNT_FACTOR[t] for t in xrange( nSteps )] ) )
        self.objective_list.append( -pulp.lpSum( [self.q_rel_pct[t]*self.NOMINAL_WGV*self.REL_COST[t]*self.DISCOUNT_FACTOR[t] for t in xrange( nSteps )] ) )

        if len( self.src_list ) + len( self.snk_list ) == 0:
            # Standalone storage use given forward curve
            # to price injection/release volumes.
            self.objective_list.append( -pulp.lpSum( [self.q_inj_pct[t]*self.NOMINAL_WGV*self.FWD_CURVE_ASK[t]*self.DISCOUNT_FACTOR[t] for t in xrange( nSteps )] ) )
            self.objective_list.append(  pulp.lpSum( [self.q_rel_pct[t]*self.NOMINAL_WGV*self.FWD_CURVE_BID[t]*self.DISCOUNT_FACTOR[t] for t in xrange( nSteps )] ) )


    def get_lp_vars(self):
        """
        """
        return super(Storage, self).get_lp_vars()\
            + self.lev_pct.tolist()\
            + self.q_inj_pct.tolist()\
            + self.q_rel_pct.tolist()
    

if __name__ == "__main__":
    print conditional(True, "Yes", "Nope")
    print conditional(False, "Yes", "Nope")
    