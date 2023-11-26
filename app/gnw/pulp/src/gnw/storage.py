# ==============================================================================
#
#   package         :   GasNetWorks (gnw) Python/pulp fuelled LP/MIP modeller 
#   author          :   Marc Roth (re04179)
#   version         :   $Id: storage.py 4064 2009-11-03 19:25:24Z re04179 $
#   heading         :   $HeadURL: http://subversion.rwe.com/svn/s_and_v_projects/GasNetworks/trunk/app/gnw/pulp/src/gnw/storage.py $
#
#   Description     :   Package file
#
#   Creation Date   :   06Mar2009
#
#   Copyright       :   RWE Supply and Trading GmbH
#
# ==============================================================================
"""
gnw: Provides gas storage abstraction
"""
import numpy
import pulp

from gnw.entity import Entity, FmtDictEntry
from gnw.constraint import ConstraintCoeff

from gnw.util import isint
from gnw.util import conditional

from __init__ import __eSell__
from __init__ import __eBuy___


class Storage( Entity ):
    """
    Gas storage entity.
    
    @ivar SB: sell or buy indicator
    @type SB: L{int} in {L{__eSell__}, L{__eBuy___}}
    
    @ivar INJ_CAP: nominal injection capacity in [MW]
    @type INJ_CAP: L{float}

    @ivar REL_CAP: nominal release capacity in [MW]
    @type REL_CAP: L{float}
    
    @ivar WGV: nominal working gas volume in [MWh]
    @type WGV: L{float}
    
    @ivar START_LEV_PCT: storage start level as a percentage [%] of
        L{gnw.storage.Storage.WGV}
    @type START_LEV_PCT: L{float}
    
    @ivar FINAL_LEV_PCT: storage final level as a percentage [%] of
        L{gnw.storage.Storage.WGV}, or None. If equal to None no
        storage final level constraints are set.
    @type FINAL_LEV_PCT: L{float} or None
     
    @ivar STRICT_FINAL_LEV: Flag indicating whether
        L{gnw.storage.Storage.FINAL_LEV_PCT} has to be reached
        exactly or cannot be under cut.
    @type STRICT_FINAL_LEV: L{bool}
    
    @ivar CONSTRAINT_COEFF: constraint coefficients applicable
        to one or more dispatch periods.
    @type CONSTRAINT_COEFF: L{list} of L{gnw.ConstraintCoeff}
    
    @ivar INJ_COST: dispatch period dependent injection cost in [EUR/MWh].
    @type INJ_COST: L{list} of L{float} or L{numpy.array} of
        dtype='double'
        
    @ivar REL_COST: dispatch period dependent release cost in [EUR/MWh].
    @type REL_COST: L{list} of L{float} or L{numpy.array} of
        dtype='double'
        
    @ivar LEV_DEP_INJ_CAP: storage level dependent injection capacity
        rate curve.
    @type LEV_DEP_INJ_CAP: L{gnw.storage.Storage.LevDepDispatchCurve}
        or None
    
    @ivar LEV_DEP_REL_CAP: storage level dependent release capacity
        rate curve.
    @type LEV_DEP_REL_CAP: L{gnw.storage.Storage.LevDepDispatchCurve}
        or None
    
    @ivar DISCOUNT_FACTOR: dispatch period dependent discount
        factor.
    @type DISCOUNT_FACTOR: L{numpy.array} of dtype='double'
    
    @ivar DISPATCH_PERIOD: dispatch periods in hours [h] that
        do not need to be uniform. This array defines the
        optimisation period in total and the individual
        storage exercise periods individually.
    @type DISPATCH_PERIOD: L{numpy.array} of dtype='double'
    
    @ivar vol: lp decision variables representing the
        actual dispatched volume , i.e.,
        L{gnw.storage.Storage.vol}[t] == L{gnw.storage.Storage.dsp_pct}[t]*L{gnw.storage.Storage.WGV},
        for all t in xrange( nSteps )
    @type vol: L{numpy.array} of L{pulp.LpVariable}
    
    @ivar lev_pct: lp decision variables representing the
        optimal storage level at the start of each
        dispatch period as a percentage [%] of 
        L{gnw.storage.Storage.WGV}.
    @type lev_pct: L{numpy.array} of L{pulp.LpVariable}
    
    @ivar dsp_pct: lp decision variables representing the
        dispatch volume for each dispatch period as a
        percentage [%] of L{gnw.storage.Storage.WGV}.
        These are 'free' decision variables with
        positive solution values representing injection, 
        and negative solution values release.
    @type dsp_pct: L{numpy.array} of L{pulp.LpVariable}
    
    @ivar inj_pct: lp decision variables representing the
        injection volume for each dispatch period as a
        percentage [%] of L{gnw.storage.Storage.WGV}.
    @type inj_pct: L{numpy.array} of L{pulp.LpVariable}
    
    @ivar rel_pct: lp decision variables representing the
        release volume for each dispatch period as a 
        percentage [%] of L{gnw.storage.Storage.WGV}.
    @type rel_pct: L{numpy.array} of L{pulp.LpVariable}

    @ivar inj_rate: lp decision variables representing
        the storage level dependent injection capacity
        rate for each dispatch period.
    @type inj_rate: L{numpy.array} of L{pulp.LpVariable}
    
    @ivar inj_rate_a_trig: binary lp decision variables
        modelling level dependent injection capacity rate
        curves for each dispatch period and each capacity
        rate level.   
    @type inj_rate_a_trig: L{numpy.array} of L{pulp.LpVariable}

    @ivar inj_rate_b_trig: binary lp decision variables
        modelling level dependent injection capacity rate
        curves for each dispatch period and each capacity
        rate level.
    @type inj_rate_b_trig: L{numpy.array} of L{pulp.LpVariable}
    
    @ivar rel_rate: lp decision variables representing
        the storage level dependent release capacity
        rate for each dispatch period.
    @type rel_rate: L{numpy.array} of L{pulp.LpVariable}
    
    @ivar rel_rate_a_trig: binary lp decision variables
        modelling level dependent release capacity rate
        curves for each dispatch period and each capacity
        rate level.
    @type rel_rate_a_trig: L{numpy.array} of L{pulp.LpVariable}
    
    @ivar rel_rate_b_trig: binary lp decision variables
        modelling level dependent release capacity rate
        curves for each dispatch period and each capacity
        rate level.
    @type rel_rate_b_trig: L{numpy.array} of L{pulp.LpVariable}
    """
    def __init__(self, name,
                 sellbuy = __eSell__,
                 injCap = None,
                 relCap = None,
                 wgv = None,
                 startLevPct = None,
                 finalLevPct = None,
                 strictFinalLev = None,
                 constraintCoeff = None,
                 injCost = None,
                 relCost = None,
                 levDepInjCap = None,
                 levDepRelCap = None,
                 discountFactor = None,
                 dispatchPeriod = None):
        """
        As the number of arguments to the constructor
        of the class may further increase it is advised
        to use named rather than positional parameters
        when instantiating class objects.

        @param name: unique storage identifier
        @type name: L{str}
        
        @param sellbuy: sell or buy indicator
        @type sellbuy: L{int} in {L{__eSell__}, L{__eBuy___}}

        @param injCap: nominal injection capacity in [MW]
        @type injCap: L{float}
         
        @param relCap: nominal release capacity in [MW]
        @type relCap: L{float}
        
        @param wgv: nominal working gas volume in [MWh]
        @type wgv: L{float}
        
        @param startLevPct: storage start level as
            a percentage [%] of wgv.
        @type startLevPct: L{float}
        
        @param finalLevPct: storage final or ending level
            as a percentage [%] of wgv.
        @type finalLevPct: L{float} or None
        
        @param strictFinalLev: Flag indicating whether
            finalLevPct has to be reached exactly or cannot
            be under cut.
        @type strictFinalLev: L{bool}
        
        @param constraintCoeff: list of constraint coefficient
            specifications applicable to one or more dispatch periods.
        @type constraintCoeff: None or potentially empty
            list of lists of types [L{int},L{int},L{float},L{int},L{str}],
            representing dispatch period start index,
            dispatch period end index, bound value, bound type and
            constraint type, respectively.

        @param injCost: dispatch period dependent injection cost
            in [EUR/MWh].
        @type injCost: None, L{float}, L{list} of L{float}
            or L{numpy.array} of dtype='double', [default=0.0]
            
        @param relCost: dispatch period dependent release cost
            in [EUR/MWh].
        @type relCost: None, L{float}, L{list} of L{float}
            or L{numpy.array} of dtype='double', [default=0.0]
            
        @param levDepInjCap: storage level dependent injection
            capacity rate curve.
        @type levDepInjCap: None or
            L{gnw.storage.Storage.LevDepDispatchCurve},
            [default=LevelDepDispatchCurve()]
        
        @param levDepRelCap: storage level dependent release
            capacity rate curve.
        @type levDepRelCap: None or
            L{gnw.storage.Storage.LevDepDispatchCurve}
            [default=LevelDepDispatchCurve()]
        
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
        super( Storage, self ).__init__( name )
        
        self.set_SB( sellbuy )

        self.INJ_CAP = conditional( injCap is None, 1.0, injCap )
        self.REL_CAP = conditional( relCap is None, 1.0, relCap )
        self.WGV = conditional( wgv is None, 1.0, wgv )
        self.START_LEV_PCT = conditional( startLevPct is None, 0.0, startLevPct )
        self.FINAL_LEV_PCT = conditional( finalLevPct is None, 0.0, finalLevPct )
        self.STRICT_FINAL_LEV = conditional( strictFinalLev is None, False, strictFinalLev )
        
        self.set_CONSTRAINT_COEFF( constraintCoeff )
        
        self.set_INJ_COST( injCost )
        self.set_REL_COST( relCost )
        
        self.set_LEV_DEP_INJ_CAP( levDepInjCap )
        self.set_LEV_DEP_REL_CAP( levDepRelCap )
        
        self.set_DISCOUNT_FACTOR( discountFactor )
        self.set_DISPATCH_PERIOD( dispatchPeriod )
        
        self.vol = numpy.empty( 0, dtype='object' )
        
        self.lev_pct = numpy.empty( 0, dtype='object' )
        self.dsp_pct = numpy.empty( 0, dtype='object' )
        
        self.rel_pct = numpy.empty( 0, dtype='object' )
        self.inj_pct = numpy.empty( 0, dtype='object' )

        self.inj_rate = numpy.empty( 0, dtype='object' )
        self.inj_rate_b_trig = numpy.empty( 0, dtype='object' )
        self.inj_rate_a_trig = numpy.empty( 0, dtype='object' )
        
        self.rel_rate = numpy.empty( 0, dtype='object' )
        self.rel_rate_b_trig = numpy.empty( 0, dtype='object' )
        self.rel_rate_a_trig = numpy.empty( 0, dtype='object' )
        

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

        
    def set_CONSTRAINT_COEFF(self, value):
        """
        @param value: list of constraints.
        @type value: None or potentially empty
            list of lists of types [L{int},L{int},L{float},L{int},L{str}],
            representing dispatch period start index,
            dispatch period end index, bound, bound type
            and constraint type, respectively.
        
        @raise TypeError:
        @raise IndexError:  
        @raise ValueError: 
        """
        self.constraintTypeMask = \
            ConstraintCoeff.ConstraintType.LEV_PCT|\
            ConstraintCoeff.ConstraintType.INJ_CAP_PCT|\
            ConstraintCoeff.ConstraintType.REL_CAP_PCT|\
            ConstraintCoeff.ConstraintType.INJ_VOL_PCT|\
            ConstraintCoeff.ConstraintType.REL_VOL_PCT
        
        super( Storage, self ).set_CONSTRAINT_COEFF( value )
    
    
    def set_INJ_COST(self, value):
        """
        @param value: dispatch period dependent injection
            cost in [EUR/MWh]. If input is list or
            array type then its length must equal
            len( L{gnw.entity.Entity.DISPATCH_PERIOD} ). 
        @type value: None, L{float}, L{list} of L{float} or
            L{numpy.array} of dtype='double', [default=0.0].
        """
        self.INJ_COST = conditional( value is None, 0.0, value )
    
    
    def set_REL_COST(self, value):
        """
        @param value: dispatch period dependent release
            cost in [EUR/MWh]. If input is list or
            array type then its length must equal
            len( L{gnw.entity.Entity.DISPATCH_PERIOD} ). 
        @type value: None, L{float}, L{list} of L{float} or
            L{numpy.array} of dtype='double', [default=0.0].
        """
        self.REL_COST = conditional( value is None, 0.0, value )


    def set_LEV_DEP_INJ_CAP(self, value):
        """
        @param value: storage level dependent injection
            capacity rate curve.  
        @type value: None or L{gnw.storage.LevDepDispatchCurve}
            [default=LevDepDispatchCurve()].
            
        @raise TypeError:
        """
        self.LEV_DEP_INJ_CAP = conditional( value is None, LevDepDispatchCurve(), value )
        if not isinstance( self.LEV_DEP_INJ_CAP, LevDepDispatchCurve ):
            raise TypeError, "set_LEV_DEP_INJ_CAP: Object instance of type 'LevDepDispatchCurve' expected"
    
    
    def set_LEV_DEP_REL_CAP(self, value):
        """
        @param value: storage level dependent release
            capacity rate curve.  
        @type value: None or L{gnw.storage.LevDepDispatchCurve}
            [default=LevDepDispatchCurve()].
        
        @raise TypeError: 
        """
        self.LEV_DEP_REL_CAP = conditional( value is None, LevDepDispatchCurve(), value )
        if not isinstance( self.LEV_DEP_REL_CAP, LevDepDispatchCurve ):
            raise TypeError, "set_LEV_DEP_REL_CAP: Object instance of type 'LevDepDispatchCurve' expected"
        

    def set_DISCOUNT_FACTOR(self, value):
        """
        @param value: dispatch period dependent
            discount factor.
        @type value: None, L{float}, L{list} of L{float}
            or L{numpy.array} of dtype='double', [default=1.0]
        """
        self.DISCOUNT_FACTOR = conditional( value is None, 1.0, value )
        

    def set_DISPATCH_PERIOD(self, value ):
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
        super( Storage, self ).set_DISPATCH_PERIOD( value )
        
        nSteps = len( self.DISPATCH_PERIOD )
        nPoints = nSteps + 1
        
        self.INJ_COST = \
            self.create_coefficient_array( self.INJ_COST,
                                           nSteps,
                                           "Length of 'injCost' must match length of 'DISPATCH_PERIOD' (gnw.storage.Storage.set_DISPATCH_PERIOD)")

        self.REL_COST = \
            self.create_coefficient_array( self.REL_COST,
                                           nSteps,
                                           "Length of 'relCost' must match length of 'DISPATCH_PERIOD' (gnw.storage.Storage.set_DISPATCH_PERIOD)")
            
        self.DISCOUNT_FACTOR = \
            self.create_coefficient_array( self.DISCOUNT_FACTOR,
                                           nSteps,
                                           "Length of 'discountFactor' must match length of 'DISPATCH_PERIOD' (gnw.storage.Storage.set_DISPATCH_PERIOD)")


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
        super( Storage, self ).create_lp_vars( prefix )
        
        nSteps = len( self.DISPATCH_PERIOD )
        nPoints = nSteps + 1
        
        self.vol = numpy.array( pulp.LpVariable.matrix( prefix + self.name + "_vol", range( nSteps ) ) )
        
        self.lev_pct = numpy.array( pulp.LpVariable.matrix( prefix + self.name + "_lev_pct", range( nPoints ), lowBound = 0.0 ) )
        self.dsp_pct = numpy.array( pulp.LpVariable.matrix( prefix + self.name + "_dsp_pct", range( nSteps ) ) )
        self.inj_pct = numpy.array( pulp.LpVariable.matrix( prefix + self.name + "_inj_pct", range( nSteps ), lowBound = 0.0 ) )
        self.rel_pct = numpy.array( pulp.LpVariable.matrix( prefix + self.name + "_rel_pct", range( nSteps ), lowBound = 0.0 ) )
        
        nInjLevels = len( self.LEV_DEP_INJ_CAP.LEVEL )
        self.inj_rate = numpy.array( pulp.LpVariable.matrix( prefix + self.name + "_inj_rate", range( nSteps ), lowBound = 0.0 ) )
        if nInjLevels > 0:
            self.inj_rate_b_trig = numpy.array( [[pulp.LpVariable( prefix + self.name + "_inj_rate_b_trig_%d_%d" % (t,l), lowBound = 0, upBound = 1, cat = pulp.LpInteger ) for l in xrange( nInjLevels )] for t in xrange( nSteps )] )
            self.inj_rate_a_trig = numpy.array( [[pulp.LpVariable( prefix + self.name + "_inj_rate_a_trig_%d_%d" % (t,l), lowBound = 0, upBound = 1, cat = pulp.LpInteger ) for l in xrange( nInjLevels )] for t in xrange( nSteps )] )

        nRelLevels = len( self.LEV_DEP_REL_CAP.LEVEL )
        self.rel_rate = numpy.array( pulp.LpVariable.matrix( prefix + self.name + "_rel_rate", range( nSteps ), lowBound = 0.0 ) )
        if nRelLevels > 0:
            self.rel_rate_b_trig = numpy.array( [[pulp.LpVariable( prefix + self.name + "_rel_rate_b_trig_%d_%d" % (t,l), lowBound = 0, upBound = 1, cat = pulp.LpInteger ) for l in xrange( nRelLevels )] for t in xrange( nSteps )] )
            self.rel_rate_a_trig = numpy.array( [[pulp.LpVariable( prefix + self.name + "_rel_rate_a_trig_%d_%d" % (t,l), lowBound = 0, upBound = 1, cat = pulp.LpInteger ) for l in xrange( nRelLevels )] for t in xrange( nSteps )] )

            
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
        super( Storage, self ).create_model( prefix )
        
        nSteps = len( self.DISPATCH_PERIOD )
        nPoints = nSteps + 1

        # storage start level constraint
        self.constraint_list.append( self.lev_pct[0] == self.START_LEV_PCT )
        
        # storage level balance constraints
        for t in xrange( 1, nPoints ):
            self.constraint_list.append( self.lev_pct[t] == self.lev_pct[t - 1] + self.dsp_pct[t - 1] )
            
        # storage end level constraint
        if self.FINAL_LEV_PCT is not None:
            if self.STRICT_FINAL_LEV:
                self.constraint_list.append( self.lev_pct[-1] == self.FINAL_LEV_PCT )
            else:
                self.constraint_list.append( self.lev_pct[-1] >= self.FINAL_LEV_PCT )

        # storage constraints defined by CONSTRAINT_COEFF array
        self.create_constraint_coeff_constraints()
        
        # storage level dependent injection/release capacity rate constraints
        self.create_lev_dep_inj_cap_constraints()
        self.create_lev_dep_rel_cap_constraints()

        for t in xrange( nSteps ):
            # release is ve-, injection is ve+, but
            # released volume flow into the network and should be positive (bought volumes)
            # and injected volume flow out of the network and should be negative (sold volumes).
            # Hence, minus sign in front of self.dsp_pct[t]
            self.constraint_list.append( self.vol[t] == -self.dsp_pct[t]*self.WGV )

        # storage injection/release transformation constraints
        for t in xrange( nSteps ):
            self.constraint_list.append( self.inj_pct[t] >=  self.dsp_pct[t] )
            self.constraint_list.append( self.rel_pct[t] >= -self.dsp_pct[t] )
        
        self.objective_list.append( self.get_objective_value() )


    def create_constraint_coeff_constraints(self):
        for i in xrange( len( self.CONSTRAINT_COEFF ) ):
            if self.CONSTRAINT_COEFF[i].CTYPE & ConstraintCoeff.ConstraintType.LEV_PCT:
                self.create_lev_constraint( self.CONSTRAINT_COEFF[i] )

            if self.CONSTRAINT_COEFF[i].CTYPE & ConstraintCoeff.ConstraintType.INJ_CAP_PCT:
                self.create_inj_cap_constraint( self.CONSTRAINT_COEFF[i] )

            if self.CONSTRAINT_COEFF[i].CTYPE & ConstraintCoeff.ConstraintType.REL_CAP_PCT:
                self.create_rel_cap_constraint( self.CONSTRAINT_COEFF[i] )

            if self.CONSTRAINT_COEFF[i].CTYPE & ConstraintCoeff.ConstraintType.INJ_VOL_PCT:
                self.create_inj_vol_constraint( self.CONSTRAINT_COEFF[i] )

            if self.CONSTRAINT_COEFF[i].CTYPE & ConstraintCoeff.ConstraintType.REL_VOL_PCT:
                self.create_rel_vol_constraint( self.CONSTRAINT_COEFF[i] )
        

    def create_lev_constraint(self, constraint_coeff = ConstraintCoeff()):
        dispatchPeriodIdx = xrange( constraint_coeff.START, constraint_coeff.FINAL + 1 )
        if constraint_coeff.BTYPE == ConstraintCoeff.BoundaryType.LB:
            self.constraint_list.append( pulp.lpSum( [self.lev_pct[t] for t in dispatchPeriodIdx] )
                                         >= constraint_coeff.BOUND )
            
        elif constraint_coeff.BTYPE == ConstraintCoeff.BoundaryType.UB:
            self.constraint_list.append( pulp.lpSum( [self.lev_pct[t] for t in dispatchPeriodIdx] )
                                         <= constraint_coeff.BOUND )
        
        elif constraint_coeff.BTYPE == ConstraintCoeff.BoundaryType.EQ:
            self.constraint_list.append( pulp.lpSum( [self.lev_pct[t] for t in dispatchPeriodIdx] )
                                         == constraint_coeff.BOUND )
        
        else:
            raise ValueError, "create_lev_constraint: Unknown boundary type %d encountered for constraint" % constraint_coeff.BTYPE


    def create_inj_cap_constraint(self, constraint_coeff = ConstraintCoeff()):
        dispatchPeriodIdx = xrange( constraint_coeff.START, constraint_coeff.FINAL + 1 )
        if constraint_coeff.BTYPE == ConstraintCoeff.BoundaryType.LB:
            self.constraint_list.append( self.WGV*pulp.lpSum( [self.dsp_pct[t] for t in dispatchPeriodIdx] )
                                         >= constraint_coeff.BOUND*self.INJ_CAP*pulp.lpSum( [self.DISPATCH_PERIOD[t]*self.inj_rate[t] for t in dispatchPeriodIdx] ) )
            
        elif constraint_coeff.BTYPE == ConstraintCoeff.BoundaryType.UB:
            self.constraint_list.append( self.WGV*pulp.lpSum( [self.dsp_pct[t] for t in dispatchPeriodIdx] )
                                         <= constraint_coeff.BOUND*self.INJ_CAP*pulp.lpSum( [self.DISPATCH_PERIOD[t]*self.inj_rate[t] for t in dispatchPeriodIdx] ) )
        
        elif constraint_coeff.BTYPE == ConstraintCoeff.BoundaryType.EQ:
            self.constraint_list.append( self.WGV*pulp.lpSum( [self.dsp_pct[t] for t in dispatchPeriodIdx] )
                                         == constraint_coeff.BOUND*self.INJ_CAP*pulp.lpSum( [self.DISPATCH_PERIOD[t]*self.inj_rate[t] for t in dispatchPeriodIdx] ) )
        
        else:
            raise ValueError, "create_inj_cap_constraint: Unknown boundary type %d encountered for constraint" % constraint_coeff.BTYPE


    def create_rel_cap_constraint(self, constraint_coeff = ConstraintCoeff()):
        dispatchPeriodIdx = xrange( constraint_coeff.START, constraint_coeff.FINAL + 1 )
        # Note the change of relational operator in LB and UB boudnary types
        # compared to function create_inj_cap_constraint for example.
        if constraint_coeff.BTYPE == ConstraintCoeff.BoundaryType.LB:
            self.constraint_list.append( self.WGV*pulp.lpSum( [self.dsp_pct[t] for t in dispatchPeriodIdx] )
                                         <= -constraint_coeff.BOUND*self.REL_CAP*pulp.lpSum( [self.DISPATCH_PERIOD[t]*self.rel_rate[t] for t in dispatchPeriodIdx] ) )
            
        elif constraint_coeff.BTYPE == ConstraintCoeff.BoundaryType.UB:
            self.constraint_list.append( self.WGV*pulp.lpSum( [self.dsp_pct[t] for t in dispatchPeriodIdx] )
                                         >= -constraint_coeff.BOUND*self.REL_CAP*pulp.lpSum( [self.DISPATCH_PERIOD[t]*self.rel_rate[t] for t in dispatchPeriodIdx] ) )
        
        elif constraint_coeff.BTYPE == ConstraintCoeff.BoundaryType.EQ:
            self.constraint_list.append( self.WGV*pulp.lpSum( [self.dsp_pct[t] for t in dispatchPeriodIdx] )
                                         == -constraint_coeff.BOUND*self.REL_CAP*pulp.lpSum( [self.DISPATCH_PERIOD[t]*self.rel_rate[t] for t in dispatchPeriodIdx] ) )
        
        else:
            raise ValueError, "create_rel_cap_constraint: Unknown boundary type %d encountered for constraint" % constraint_coeff.BTYPE


    def create_inj_vol_constraint(self, constraint_coeff = ConstraintCoeff()):
        dispatchPeriodIdx = xrange( constraint_coeff.START, constraint_coeff.FINAL + 1 )
        if constraint_coeff.BTYPE == ConstraintCoeff.BoundaryType.LB:
            self.constraint_list.append( pulp.lpSum( [self.inj_pct[t] for t in dispatchPeriodIdx] )
                                         >= constraint_coeff.BOUND )
        
        elif constraint_coeff.BTYPE == ConstraintCoeff.BoundaryType.UB:
            self.constraint_list.append( pulp.lpSum( [self.inj_pct[t] for t in dispatchPeriodIdx] )
                                         <= constraint_coeff.BOUND )
    
        elif constraint_coeff.BTYPE == ConstraintCoeff.BoundaryType.EQ:
            self.constraint_list.append( pulp.lpSum( [self.inj_pct[t] for t in dispatchPeriodIdx] )
                                         == constraint_coeff.BOUND )
    
        else:
            raise ValueError, "create_inj_vol_constraint: Unknown boundary type %d encountered for constraint" % constraint_coeff.BTYPE


    def create_rel_vol_constraint(self, constraint_coeff = ConstraintCoeff()):
        dispatchPeriodIdx = xrange( constraint_coeff.START, constraint_coeff.FINAL + 1 )
        if constraint_coeff.BTYPE == ConstraintCoeff.BoundaryType.LB:
            self.constraint_list.append( pulp.lpSum( [self.rel_pct[t] for t in dispatchPeriodIdx] )
                                         >= constraint_coeff.BOUND )
        
        elif constraint_coeff.BTYPE == ConstraintCoeff.BoundaryType.UB:
            self.constraint_list.append( pulp.lpSum( [self.rel_pct[t] for t in dispatchPeriodIdx] )
                                         <= constraint_coeff.BOUND )
    
        elif constraint_coeff.BTYPE == ConstraintCoeff.BoundaryType.EQ:
            self.constraint_list.append( pulp.lpSum( [self.rel_pct[t] for t in dispatchPeriodIdx] )
                                         == constraint_coeff.BOUND )
    
        else:
            raise ValueError, "create_rel_vol_constraint: Unknown boundary type %d encountered for constraint" % constraint_coeff.BTYPE


    def create_lev_dep_inj_cap_constraints(self):
        """
        Helper function to set up 
        level dependent injection capacity rate constraints.
        """
        # Backstep interpolation
        nSteps = len( self.DISPATCH_PERIOD )
        nLevels = len( self.LEV_DEP_INJ_CAP.LEVEL )
        
        if nLevels > 0:
            LEVEL = self.LEV_DEP_INJ_CAP.LEVEL
            RATE = self.LEV_DEP_INJ_CAP.RATE
            
            for t in xrange( nSteps ):
                for i in xrange( nLevels ):
                    self.constraint_list.append( self.inj_rate_b_trig[t, i] >= LEVEL[i] - self.lev_pct[t] )
                    self.constraint_list.append( self.inj_rate_b_trig[t, i] <= LEVEL[i] - self.lev_pct[t] + 1 )
                
                for i in xrange( nLevels ):
                    if i == 0:    
                        self.constraint_list.append( self.inj_rate_a_trig[t, i] == self.inj_rate_b_trig[t, i] )
                    else:
                        self.constraint_list.append( self.inj_rate_a_trig[t, i] == self.inj_rate_b_trig[t, i] - self.inj_rate_b_trig[t, i - 1] )
    
                self.constraint_list.append( pulp.lpSum( [self.inj_rate_a_trig[t, i] for i in xrange( nLevels )] ) == 1 )
                self.constraint_list.append( pulp.lpSum( [self.inj_rate_a_trig[t, i]*RATE[i] for i in xrange( nLevels )] ) == self.inj_rate[t] )
        else:
            for t in xrange( nSteps ):
                self.constraint_list.append( 1.0 == self.inj_rate[t] )


    def create_lev_dep_rel_cap_constraints(self):
        """
        Helper function to set up
        level dependent release capacity rate constraints.
        """
        # Backstep interpolation
        nSteps = len( self.DISPATCH_PERIOD )
        nLevels = len( self.LEV_DEP_REL_CAP.LEVEL )
        if nLevels > 0:
            LEVEL = self.LEV_DEP_REL_CAP.LEVEL
            RATE = self.LEV_DEP_REL_CAP.RATE
            
            for t in xrange( nSteps ):
                for i in xrange( nLevels ):
                    self.constraint_list.append( self.rel_rate_b_trig[t, i] >= LEVEL[i] - self.lev_pct[t] )
                    self.constraint_list.append( self.rel_rate_b_trig[t, i] <= LEVEL[i] - self.lev_pct[t] + 1 )
                
                for i in xrange( nLevels ):
                    if i == 0:
                        self.constraint_list.append( self.rel_rate_a_trig[t, i] == self.rel_rate_b_trig[t, i] )
                    else:
                        self.constraint_list.append( self.rel_rate_a_trig[t, i] == self.rel_rate_b_trig[t, i] - self.rel_rate_b_trig[t, i - 1] )
    
                self.constraint_list.append( pulp.lpSum( [self.rel_rate_a_trig[t, i] for i in xrange( nLevels )] ) == 1 )
                self.constraint_list.append( pulp.lpSum( [self.rel_rate_a_trig[t, i]*RATE[i] for i in xrange( nLevels )] ) == self.rel_rate[t] )
        else:
            for t in xrange( nSteps ):
                self.constraint_list.append( 1.0 == self.rel_rate[t] )


    def get_lp_vars(self):
        """
        This method returns a list containing all
        lp variables contained in self and any
        of its super classes.
        
        @return: list of lp variables
        @rtype: L{list} of L{pulp.LpVariable}
        """
        return super( Storage, self ).get_lp_vars()\
            + self.vol.tolist()\
            + self.lev_pct.tolist()\
            + self.dsp_pct.tolist()\
            + self.inj_pct.tolist()\
            + self.rel_pct.tolist()\
            + self.inj_rate.tolist()\
            + self.inj_rate_b_trig.tolist()\
            + self.inj_rate_a_trig.tolist()\
            + self.rel_rate.tolist()\
            + self.rel_rate_b_trig.tolist()\
            + self.rel_rate_a_trig.tolist()

            
    def update_fmt_dict(self, fmt_dict={}):
        """
        Overwrites base class method by updating
        dictionary L{fmt_dict} with storage
        specific information and calls base class'
        method L{update_fmt_dict}.
        
        @param fmt_dict: dictionary of keys of type
            L{str} and values of type
            L{gnw.entity.Entity.FmtDictEntry}
        @type fmt_dict: L{dict} 
        """
        nSteps = len( self.DISPATCH_PERIOD )
        nPoints = nSteps + 1

        fmt_dict.update({'SB' :                FmtDictEntry( [ self.ifmt ], 'sell/buy [1/-1]',          0, None,            False,  self.SB ),
                         'INJ_CAP' :           FmtDictEntry( [ self.ffmt ], 'INJ_CAP [MW]',             0, None,            False,  self.INJ_CAP ),
                         'REL_CAP' :           FmtDictEntry( [ self.ffmt ], 'REL_CAP [MW]',             0, None,            False,  self.REL_CAP ),
                         'WGV' :               FmtDictEntry( [ self.ffmt ], 'WGV [MWh]',                0, None,            False,  self.WGV ),
                         'START_LEV_PCT' :     FmtDictEntry( [ self.ffmt ], 'START_LEV_PCT [%]',        0, None,            False,  self.START_LEV_PCT ),
                         'FINAL_LEV_PCT' :     FmtDictEntry( [ self.ffmt ], 'FINAL_LEV_PCT [%]',        0, None,            False,  self.FINAL_LEV_PCT ),
                         'STRICT_FINAL_LEV' :  FmtDictEntry( [ self.sfmt ], 'STRICT_FINAL_LEV',         0, None,            False,  self.STRICT_FINAL_LEV ),
                         'vol':                FmtDictEntry( [ self.ffmt ], 'vol[t] [MWh]',             1, (nSteps,),       True,   self.vol),
                         'lev_pct' :           FmtDictEntry( [ self.ffmt ], 'lev_pct[t] [%]',           1, (nPoints,),      True,   self.lev_pct ),
                         'dsp_pct' :           FmtDictEntry( [ self.ffmt ], 'dsp_pct[t] [%]',           1, (nSteps,),       True,   self.dsp_pct ),
                         'rel_pct' :           FmtDictEntry( [ self.ffmt ], 'rel_pct[t] [%]',           1, (nSteps,),       True,   self.rel_pct ),
                         'inj_pct' :           FmtDictEntry( [ self.ffmt ], 'inj_pct[t] [%]',           1, (nSteps,),       True,   self.inj_pct ),
                         'INJ_COST' :          FmtDictEntry( [ self.ffmt ], 'INJ_COST[t] [EUR/MWh]',    1, (nSteps,),       False,  self.INJ_COST ),
                         'REL_COST' :          FmtDictEntry( [ self.ffmt ], 'REL_COST[t] [EUR/MWh]',    1, (nSteps,),       False,  self.REL_COST ),
                         'DF' :                FmtDictEntry( [ self.ffmt ], 'DF[t]',                    1, (nSteps,),       False,  self.DISCOUNT_FACTOR ),
                         'inj_rate' :          FmtDictEntry( [ self.ffmt ], 'inj_rate[t] [%]',          1, (nSteps,),       True,   self.inj_rate ),
                         'rel_rate' :          FmtDictEntry( [ self.ffmt ], 'rel_rate[t] [%]',          1, (nSteps,),       True,   self.rel_rate )})
        
        nInjLevs = len( self.LEV_DEP_INJ_CAP.LEVEL ) 
        if  nInjLevs > 0:
            fmt_dict.update({'LEV_DEP_INJ_CAP_LEVEL' : FmtDictEntry( [ self.ffmt ]*nInjLevs, 'LEV_DEP_INJ_CAP.LEVEL[i] [%]', 1, (nInjLevs,), False, self.LEV_DEP_INJ_CAP.LEVEL ),
                             'LEV_DEP_INJ_CAP_RATE' :  FmtDictEntry( [ self.ffmt ]*nInjLevs, 'LEV_DEP_INJ_CAP.RATE[i] [%]',  1, (nInjLevs,), False, self.LEV_DEP_INJ_CAP.RATE ),
                             'inj_rate_b_trig' :       FmtDictEntry( [ self.ifmt ]*nInjLevs, 'inj_rate_b_trig[t,%d]', 2, (nSteps,nInjLevs), True, self.inj_rate_b_trig ),
                             'inj_rate_a_trig' :       FmtDictEntry( [ self.ifmt ]*nInjLevs, 'inj_rate_a_trig[t,%d]', 2, (nSteps,nInjLevs), True, self.inj_rate_a_trig )})
            
        nRelLevs = len( self.LEV_DEP_REL_CAP.LEVEL )
        if nRelLevs > 0:
            fmt_dict.update({'LEV_DEP_REL_CAP_LEVEL' : FmtDictEntry( [ self.ffmt ]*nRelLevs, 'LEV_DEP_REL_CAP.LEVEL[i] [%]', 1, (nRelLevs,), False, self.LEV_DEP_REL_CAP.LEVEL ),
                             'LEV_DEP_REL_CAP_RATE' :  FmtDictEntry( [ self.ffmt ]*nRelLevs, 'LEV_DEP_REL_CAP.RATE[i] [%]',  1, (nRelLevs,), False, self.LEV_DEP_REL_CAP.RATE ),
                             'rel_rate_b_trig' :       FmtDictEntry( [ self.ifmt ]*nRelLevs, 'rel_rate_b_trig[t,%d]', 2, (nSteps,nRelLevs), True, self.rel_rate_b_trig ),
                             'rel_rate_a_trig' :       FmtDictEntry( [ self.ifmt ]*nRelLevs, 'rel_rate_a_trig[t,%d]', 2, (nSteps,nRelLevs), True, self.rel_rate_a_trig )})

        super( Storage, self ).update_fmt_dict( fmt_dict )


    def get_results(self):
        """
        """
        nSteps = len( self.DISPATCH_PERIOD )
        
        vol = [-self.SB*self.vol[t].varValue for t in xrange( nSteps )]
        cashflow = [self.SB*(self.INJ_COST[t]*self.inj_pct[t].varValue +
                             self.REL_COST[t]*self.rel_pct[t].varValue)*self.WGV for t in xrange( nSteps )]
        
        return (vol, cashflow) 


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
        mtm = super( Storage, self ).get_mark_to_market_value()

        nSteps = len( self.DISPATCH_PERIOD )
        # storage injection/release cost components to objective function
        mtm += pulp.LpAffineExpression( self.SB*self.WGV*pulp.lpSum( [self.inj_pct[t]*self.INJ_COST[t]*self.DISCOUNT_FACTOR[t] for t in xrange( nSteps )] ) ) 
        mtm += pulp.LpAffineExpression( self.SB*self.WGV*pulp.lpSum( [self.rel_pct[t]*self.REL_COST[t]*self.DISCOUNT_FACTOR[t] for t in xrange( nSteps )] ) ) 
        
        return mtm


class LevDepDispatchCurve( object ):
    """
    Encapsulates information on level dependent capacity
    rate curve. Currently only supports 'backstep' interpolation.

    @ivar LEVEL: array of storage levels as a percentage of
        the working gas volume of given storage, i.e., 0.0 <= l <= 1.0,
        forall l in LEVEL. Needless to say that
        len( LEVEL ) = len( L{gnw.storage.LevDepDispatchCurve.RATE} ),
        must hold.
    @type LEVEL: L{numpy.array} of dtype='double'
    
    @ivar RATE: array of capacity rates corresponding to
        levels in L{gnw.storage.LevDepDispatchCurve.LEVEL}.
        In general, 0.0 <= r <= 1.0, forall r in RATE,
        must hold. Needless to say that
        len( RATE ) = len( L{gnw.storage.LevDepDispatchCurve.LEVEL} ),
        must hold.
    @type RATE: L{numpy.array} of dtype='double'
    
    @ivar INTERP_TYPE: interpolation type.
    @type INTERP_TYPE: L{str} in {'backstep'}
    """
    def __init__(self, level = [], rate = [], interpType = 'backstep' ):
        """
        @param level: list or array of storage levels as a percentage of
            the working gas volume of given storage, i.e., 0.0 <= lev <= 1.0,
            forall lev in level. Needless to say that
            len( level ) = len( rate ),
            must hold.
        @type level: L{list} of L{float} or L{numpy.array} of dtype='double'
        
        @param rate: list or array of capacity rates corresponding to
            levels in level.
            In general, 0.0 <= r <= 1.0, forall r in rate,
            must hold. Needless to say that
            len( rate ) = len( level ),
            must hold.
        @type rate: L{list} of L{float} or L{numpy.array} of dtype='double'
        
        @param interpType: interpolation type.
        @type interpType: L{str} in {'backstep'}, [default='backstep']
        """
        self.LEVEL = numpy.array( level, dtype='double' )
        self.RATE = numpy.array( rate, dtype='double' )
        self.INTERP_TYPE = interpType



if __name__ == "__main__":
    print "gnw.storage.py"

# ==============================================================================
#
#   Revision Control:
#
#   $Revision:: 4064                    $   Revision of last commit
#   $Author:: re04179                   $   Author of last commit
#   $Date:: 2009-11-03 20:25:24 +0100 (#$   Date of last commit
#
# ==============================================================================
