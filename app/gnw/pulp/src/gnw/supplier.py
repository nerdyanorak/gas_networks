# ==============================================================================
#
#   package         :   GasNetWorks (gnw) Python/pulp fuelled LP/MIP modeller 
#   author          :   Marc Roth (re04179)
#   version         :   $Id: supplier.py 4301 2009-11-23 13:04:46Z re04179 $
#   heading         :   $HeadURL: http://subversion.rwe.com/svn/s_and_v_projects/GasNetworks/trunk/app/gnw/pulp/src/gnw/supplier.py $
#
#   Description     :   Package file
#
#   Creation Date   :   18May2009
#
#   Copyright       :   RWE Supply and Trading GmbH
#
# ==============================================================================
"""
gnw: provides gas supply contract abstraction
"""
import numpy
import pulp

from gnw.entity import Entity, FmtDictEntry
from gnw.constraint import ConstraintCoeff

from gnw.util import conditional
from gnw.util import isnumeric
from gnw.util import isint
from gnw.util import issequence

from __init__ import __eSell__
from __init__ import __eBuy___


class Supplier( Entity ):
    """
    Gas supplier entity.
    
    @ivar SB: sell or buy indicator
    @type SB: L{int} in {L{__eSell__}, L{__eBuy___}}
    
    @ivar ACQ: (nominal) annual contract quantity in [MWh]
    @type ACQ: L{float} 
           
    @ivar HAS_SFP: flags whether Short-Fall Penalty feature is enabled
    @type HAS_SFP: L{bool}
     
    @ivar HAS_MUP: flags whether Make-UP feature is enabled
    @type HAS_MUP: L{bool}
    
    @ivar HAS_MUP_EXPIRY: flags whether Make-UP volume expiry feature is enabled
        (only active if L{HAS_MUP} is set to True)
    @type HAS_MUP_EXPIRY: L{bool}
     
    @ivar MUP_NUM_EXPIRY_PERIODS: provides the number of accounting periods
        after which Make-UP volumes expire (only active if L{HAS_MUP} and
        L{HAS_MUP_EXPIRY} are set to True)
    @type MUP_NUM_EXPIRY_PERIODS: L{int}
      
    @ivar MUP_CREATE_PRICE_RATE: is a rate multiplied with the average
        contract price at which Make-UP gas created is priced at.
    @type MUP_CREATE_PRICE_RATE: L{float}
    
    @ivar MUP_USEUP_PRICE_RATE: is a rate multiplied with the average
        contract price at which Make-UP gas used-up is priced at.
    @type MUP_USEUP_PRICE_RATE: L{float} 

    @ivar HAS_CFW: flags whether Carry ForWard feature is enabled
    @type HAS_CFW: L{bool}
     
    @ivar HAS_CFW_EXPIRY: flags whether Carry-ForWard volume expiry feature is enabled
        (only active if L{HAS_CFW} is set to True)
    @type HAS_CFW_EXPIRY: L{bool}
     
    @ivar CFW_NUM_EXPIRY_PERIODS: provides the number of accounting periods
        after which Carry ForWard volumes expire (only active if L{HAS_CFW} and
        L{HAS_CFW_EXPIRY} are set to True)
    @type CFW_NUM_EXPIRY_PERIODS: L{int} 
    
    @ivar HAS_IAS39: flags whether IAS39 related features are enabled
    @type HAS_IAS39: L{bool}
     
    @ivar MUP_INITIAL_BALANCE: Make-UP initial volume balance(s)
    @type MUP_INITIAL_BALANCE: is
        - L{float}, if L{HAS_MUP} and not L{HAS_MUP_EXPIRY}
        - L{list} of L{float} of length L{MUP_NUM_EXPIRY_PERIODS},
            if L{HAS_MUP} and L{HAS_MUP_EXPIRY}
        - ignored otherwise
        
    @ivar CFW_INITIAL_BALANCE: Carry ForWard initial volume balance(s)
    @type CFW_INITIAL_BALANCE: is
        - L{float}, if L{HAS_CFW} and not L{HAS_CFW_EXPIRY}
        - L{list} of L{float} of length L{CFW_NUM_EXPIRY_PERIODS},
            if L{HAS_CFW} and L{HAS_CFW_EXPIRY}
        - ignored otherwise
    
    @ivar ACC_AVG_CONTRACT_PRICE: average contract price(s) over given accounting
        periods (the number of accounting periods is given by list
        len( L{gnw.supplier.Supplier.acc_period_tuple_list} )
        that is only initialised later during model set-up, see
        L{gnw.supplier.Supplier.collect_constraint_coeff_information})
    @type ACC_AVG_CONTRACT_PRICE: can have the the following structure:
        - None type: all average prices are calculated from
            the given contract price curve on the fly.
        - sequence type:
            the average contract price for the first
            len( ACC_AVG_CONTRACT_PRICE ) accounting periods
            are taken from this sequence, if elements numeric,
            calculated on the fly from contract price curve,
            otherwise. 
    
    @ivar CONTRACT_PRICE: dispatch period dependent contract price.
    @type CONTRACT_PRICE: L{numpy.array} of dtype='double'   
    
    @ivar CONSTRAINT_COEFF: constraint coefficients applicable
        to one or more dispatch periods.
    @type CONSTRAINT_COEFF: L{list} of L{gnw.ConstraintCoeff}
    
    @ivar DISCOUNT_FACTOR: dispatch period dependent discount
        factor.
    @type DISCOUNT_FACTOR: L{numpy.array} of dtype='double'

    @ivar pos_pct: array of decision variables holding the
        dispatched position in [MW] for each dispatch period
        as a percentage of ACQ.
    @type pos_pct: L{numpy.array} of L{pulp.LpVariable}
    
    @ivar vol: arreay of decision variables holding the
        dispatched volume in [MWh] for each dsipatch period
    @type vol: L{numpy.array} of L{pulp.LpVariable}
    
    @ivar top_period_trig: array of binary variables being 1 if
        ToP level is not reached during make-up and/or
        carry forward accounting period, and make-up gas is created
        and/or carry forward gas is used up, 0 otherwise
    @type top_period_trig: L{numpy.array} of L{pulp.LpVariable} 
    
    @ivar mup_period_vol_bal: array of make-up gas balances
        available at the start of each make-up accounting period
    @type mup_period_vol_bal: L{numpy.array} of L{pulp.LpVariable}
    
    @ivar mup_period_vol_chg: array of volume changes of make-up gas
        during each make-up accounting period
    @type mup_period_vol_chg: L{numpy.array} of L{pulp.LpVariable}
     
    @ivar mup_period_vol_inc: array of volume increases of make-up gas
        during each make-up accounting period
    @type mup_period_vol_inc: L{numpy.array} of L{pulp.LpVariable}
     
    @ivar mup_period_vol_dec: array of volume decreases of make-up gas
        during each make-up accounting period
    @type mup_period_vol_dec: L{numpy.array} of L{pulp.LpVariable} 
                                           
    @ivar mup_trig: array of binary variables being 1 if ToP level
        has been reached at the end of dispatch period t
        during make-up accounting period k, 0 otherwise
    @type mup_trig: L{numpy.array} of L{pulp.LpVariable}
     
    @ivar mup_vol: array of gas volumes taken as make-up gas
        during dispatch period t in make-up accounting period k
    @type mup_vol: L{numpy.array} of L{pulp.LpVariable} 

    @ivar cfw_period_vol_bal: array of carry forward gas balances
        available at the start of each carry forward accounting period
    @type cfw_period_vol_bal: L{numpy.array} of L{pulp.LpVariable}
    
    @ivar cfw_period_vol_chg: array of volume changes of carry forward gas
        during each carry forward accounting period
    @type cfw_period_vol_chg: L{numpy.array} of L{pulp.LpVariable}
    
    @ivar cfw_period_vol_inc: array of volume increases of carry forward gas
        during each carry forward accounting period
    @type cfw_period_vol_inc: L{numpy.array} of L{pulp.LpVariable}
    
    @ivar cfw_period_vol_dec: array of volume decreases of carry forward gas
        during each carray forward accounting period
    @type cfw_period_vol_dec: L{numpy.array} of L{pulp.LpVariable}

    @ivar acc_period_tuple_list: list of (START,FINAL)
        L{DISPATCH_PERIOD} index tuples collected from
        constraints having CTYPE bit ACC_PERIOD set
        (required for make-up, carry forward and/or
        ias39 variables and constraints)
    @type acc_period_tuple_list: L{list} of
        (L{int},L{int}) tuples

    @ivar daily_constraint_coeff_min_index_dict: dictionary
        holding indices into the L{CONSTRAINT_COEFF} list
        for daily minimum volume constraints (i.e.,
        constraints with BTYPE = 0 and CTYPE bit POS_PCT set).
        The dictionarie's keys are tuples (START,FINAL) with
        START==FINAL, representing L{DISPATCH_PERIOD} indices
    @type daily_constraint_coeff_min_index_dict: L{dict} with
        keys of type (L{int},L{int}) and values of type L{int} 
    
    @ivar daily_constraint_coeff_max_index_dict: dictionary
        holding indices into the L{CONSTRAINT_COEFF} list
        for daily maximum volume constraints (i.e.,
        constraints with BTYPE = 1 and CTYPE bit POS_PCT set).
        The dictionarie's keys are tuples (START,FINAL) with
        START==FINAL, representing L{DISPATCH_PERIOD} indices
    @type daily_constraint_coeff_max_index_dict: L{dict} with
        keys of type (L{int},L{int}) and values of type L{int}     

    @ivar acc_period_constraint_coeff_min_index_dict: dictionary
        holding indices into the L{CONSTRAINT_COEFF} list
        for accounting period minimum volume constraints (i.e.,
        constraints with BTYPE = 0 and CTYPE bit ACC_PERIODS set).
        The dictionarie's keys are tuples (START,FINAL)
        representing L{DISPATCH_PERIOD} indices
    @type acc_period_constraint_coeff_min_index_dict: L{dict} with
        keys of type (L{int},L{int}) and values of type L{int}
      
    @ivar acc_period_constraint_coeff_max_index_dict: dictionary
        holding indices into the L{CONSTRAINT_COEFF} list
        for accounting period maximum volume constraints (i.e.,
        constraints with BTYPE = 1 and CTYPE bit ACC_PERIODS set).
        The dictionarie's keys are tuples (START,FINAL)
        representing L{DISPATCH_PERIOD} indices
    @type acc_period_constraint_coeff_max_index_dict: L{dict} with
        keys of type (L{int},L{int}) and values of type L{int}
    """
    def __init__(self, name,
                 sellbuy = __eSell__,
                 acq = None,
                 # shortfall related inputs
                 hasShortfallPenalty = None,
                 # makeup related inputs
                 hasMakeUp = None,
                 hasMakeUpExpiry = None,
                 makeUpNumExpiryPeriods = None,
                 makeUpCreatePriceRate = None,
                 makeUpUseupPriceRate = None,
                 # carry forward related inputs
                 hasCarryForward = None,
                 hasCarryForwardExpiry = None,
                 carryForwardNumExpiryPeriods = None,
                 # IAS39 related inputs
                 hasIAS39 = None,
                 # curve/list inputs
                 constraintCoeff = None,
                 contractPrice = None,
                 makeUpInitialBalance = None,
                 carryForwardInitialBalance = None,
                 accPeriodAvgContractPrice = None,
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
        
        @param acq: (Nominal) annual contract quantity.
        @type acq: L{float}
        
        @param hasShortfallPenalty: flag indicating whether
            short-fall penalty feature applies or not.
        @type hasShortfallPenalty: L{bool}
        
        @param hasMakeUp: flag indicating whether
            make-up feature applies or not.
        @type hasMakeUp: L{bool}
        
        @param hasMakeUpExpiry: flag indicating whether
            make-up gas is expiring after a number of
            make-up periods or not
        @type hasMakeUpExpiry: L{bool}
        
        @param makeUpNumExpiryPeriods: non-negative integer giving the
            the number of make-up periods after which make-up gas is
            expiring. Input is ignored if L{hasMakeUpExpiry} is False.
        @type makeUpNumExpiryPeriods: L{int}

        @param makeUpCreatePriceRate: rate at which make-up gas is
            priced while created.
        @type makeUpCreatePriceRate: L{float}
        
        @param makeUpUseupPriceRate: rate at which make-up gas is
            priced while used up.
        @type makeUpUseupPriceRate: L{float}
        
        @param hasCarryForward: flag indicating whether carry
            forward feature applies or not.
        @type hasCarryForward: L{bool}
        
        @param makeUpInitialBalance: provides the balance
            of make-up gas available at the beginning of the
            dispatch period of the supply contract. Depending
            on the values of flags L{hasMakeUp} and L{hasMakeUpExpiry}
            makeUpInitialiseBalance may be None (L{hasMakeUp} = False),
            a numeric value ((L{hasMakeUp} = True, L{hasMakeUpExpiry} = False)
            or a list of size L{makeUpNumExpiryPeriods} of numeric values
            ((L{hasMakeUp} = True, L{hasMakeUpExpiry} = True).
        @type makeUpInitialBalance: None, L{float} or L{list} of
            L{float} size L{makeUpNumExpiryPeriods}
        
        @param contractPrice: dispatch period dependent
            contract price.
        @type contractPrice: None, L{float}, L{list} of L{float}
            or L{numpy.array} of dtype='double', [default=0.0]

        @param constraintCoeff: list of constraint coefficient
            specifications applicable to one or more dispatch periods.
        @type constraintCoeff: None or potentially empty
            list of lists of types [L{int},L{int},L{float},L{int},L{str}],
            representing dispatch period start index,
            dispatch period end index, bound value, bound type and
            constraint type, respectively.
            
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
        super( Supplier, self ).__init__( name )
        
        self.set_SB( sellbuy )

        self.ACQ = conditional( acq is None, 1.0, acq )
        
        self.HAS_SFP = conditional( hasShortfallPenalty is None, False, hasShortfallPenalty ) 
         
        self.HAS_MUP = conditional( hasMakeUp is None, False, hasMakeUp )
        self.HAS_MUP_EXPIRY = conditional( hasMakeUpExpiry is None, False, hasMakeUpExpiry )
        self.MUP_NUM_EXPIRY_PERIODS = conditional( makeUpNumExpiryPeriods is None, 0, makeUpNumExpiryPeriods )
        self.MUP_CREATE_PRICE_RATE = conditional( makeUpCreatePriceRate is None, 1.0, makeUpCreatePriceRate )
        self.MUP_USEUP_PRICE_RATE = conditional(  makeUpUseupPriceRate is None, 0.0, makeUpUseupPriceRate )

        self.HAS_CFW = conditional( hasCarryForward is None, False, hasCarryForward )
        self.HAS_CFW_EXPIRY = conditional( hasCarryForwardExpiry is None, False, hasCarryForwardExpiry )
        self.CFW_NUM_EXPIRY_PERIODS = conditional( carryForwardNumExpiryPeriods is None, 0, carryForwardNumExpiryPeriods )
        
        self.HAS_IAS39 = conditional( hasIAS39 is None, False, hasIAS39 )
        
        self.set_CONSTRAINT_COEFF( constraintCoeff )
        self.set_CONTRACT_PRICE( contractPrice )
        
        self.set_MUP_INITIAL_BALANCE( makeUpInitialBalance )
        self.set_ACC_AVG_CONTRACT_PRICE( accPeriodAvgContractPrice )
        self.set_CFW_INITIAL_BALANCE( carryForwardInitialBalance )
        
        self.set_DISCOUNT_FACTOR( discountFactor )
        self.set_DISPATCH_PERIOD( dispatchPeriod )
                
        self.pos_pct = numpy.empty( 0, dtype='object' )
        self.vol = numpy.empty( 0, dtype='object' )
        
        
        if self.HAS_MUP or self.HAS_CFW:
            # top_period_trig: binary variable being 1 if
            # ToP level is not reached during period and
            # make-up gas is created, 0 otherwise.
            self.top_period_trig = numpy.empty( 0, dtype='object' )         # b[k]
            
        if self.HAS_MUP:
            # mup_period_vol_bal: represents make-up gas balance
            # available at the start of make-up period k
            self.mup_period_vol_bal = numpy.empty( 0, dtype='object' )      # M[k] >= 0     : make-up balance
            # mup_period_vol_inc: represents the increase of make-up gas
            # in make-up period k
            self.mup_period_vol_inc = numpy.empty( 0, dtype='object' )      # dM+[k] >= 0   : increase of make-up gas
            # mup_period_vol_dec: represents the decrease of make-up gas
            # in make-up period k
            self.mup_period_vol_dec = numpy.empty( 0, dtype='object' )      # dM-[k] >= 0   : decrease of make-up gas
            # mup_period_vol_chg: represents the change of make-up gas
            # in make-up period k
            self.mup_period_vol_chg = numpy.empty( 0, dtype='object' )      # dM[k] in R    : change of make-up gas
                                                   
            # mup_trig: binary variable being 1 if ToP level
            # has been reached at the end of dispatch period t
            # during make-up period k, t in {START[k],..,FINAL[k]},
            # 0 otherwise.
            self.mup_trig = numpy.empty( 0, dtype='object' )                # u[t]
            # mup_vol: represents the gas taken as make-up gas
            # during dispatch period t in make-up period k,
            # t in {START[k],..,FINAL[k]}, given as absolute
            # gas volume [MWh].
            self.mup_vol = numpy.empty( 0, dtype='object' )                 # qM[t]

            if self.HAS_MUP_EXPIRY:
                # mup_period_vol_exp_bal: represents make-up gas balance
                # available at the start of make-up period k
                self.mup_period_vol_exp_bal = numpy.empty( (0,0), dtype='object' )      # M[k,i] >= 0     : make-up balance
                # mup_period_vol_exp_dec: represents the decrease of make-up gas
                # in make-up period k expiring in i accounting periods
                self.mup_period_vol_exp_dec = numpy.empty( (0,0), dtype='object' )      # dM-[k,i] >= 0   : decrease of make-up gas
                # mup_period_vol_exp: represents the volume of make-up gas
                # expired at the end of make-up period k
                self.mup_period_vol_exp = numpy.empty( 0, dtype='object' )              # expired_M[k] >= 0    : expired make-up gas
                

        if self.HAS_CFW:
            # cfw_period_vol_bal: represents carry forward gas balance
            # available at the start of carry forward period k
            self.cfw_period_vol_bal = numpy.empty( 0, dtype='object' )      # C[k] >= 0     : carry forward balance
            # cfw_period_vol_inc: represents the increase of carry forward gas
            # in carry forward period k
            self.cfw_period_vol_inc = numpy.empty( 0, dtype='object' )      # dC+[k] >= 0   : increase of carry forward gas
            # cfw_period_vol_dec: represents the decrease of carry forward gas
            # in carry forward period k
            self.cfw_period_vol_dec = numpy.empty( 0, dtype='object' )      # dC-[k] >= 0   : decrease of carry forward gas
            # cfw_period_vol_chg: represents the change of carry forward gas
            # in carry forward period k
            self.cfw_period_vol_chg = numpy.empty( 0, dtype='object' )      # dC[k] in R    : change of carry forward gas

            if self.HAS_CFW_EXPIRY:
                # cfw_period_vol_exp_bal: represents carry forward gas balance
                # available at the start of carry forward period k
                self.cfw_period_vol_exp_bal = numpy.empty( (0,0), dtype='object' )      # C[k,i] >= 0     : carry forward balance
                # cfw_period_vol_exp_dec: represents the decrease of carry forward gas
                # in carry forward period k expiring in i accounting periods
                self.cfw_period_vol_exp_dec = numpy.empty( (0,0), dtype='object' )      # dC-[k,i] >= 0   : decrease of carry forward gas
                # mup_period_vol_exp: represents the volume of make-up gas
                # expired at the end of make-up period k
                self.cfw_period_vol_exp = numpy.empty( 0, dtype='object' )              # expired_C[k] >= 0    : expired carry forward gas

            
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
        self.constraintTypeMask =\
            ConstraintCoeff.ConstraintType.POS_PCT|\
            ConstraintCoeff.ConstraintType.ACC_PERIOD|\
            ConstraintCoeff.ConstraintType.MUP_BND_PCT|\
            ConstraintCoeff.ConstraintType.CFW_BND_PCT
        
        super( Supplier, self ).set_CONSTRAINT_COEFF( value )
       
        
    def set_CONTRACT_PRICE(self, value):
        """
        @param value: dispatch period dependent
            contract price.
        @type value: None, L{float}, L{list} of L{float}
            or L{numpy.array} of dtype='double', [default=0.0]
        """
        self.CONTRACT_PRICE = conditional( value is None, 0.0, value )
    
    
    def set_MUP_INITIAL_BALANCE(self, value):
        """
        """
        self.MUP_INITIAL_BALANCE = self.get_initial_balance(value, self.HAS_MUP, self.HAS_MUP_EXPIRY, self.MUP_NUM_EXPIRY_PERIODS)


    def set_CFW_INITIAL_BALANCE(self, value):
        """
        """
        self.CFW_INITIAL_BALANCE = self.get_initial_balance(value, self.HAS_CFW, self.HAS_CFW_EXPIRY, self.CFW_NUM_EXPIRY_PERIODS)


    def get_initial_balance(value, has_flag = False, has_expiry_flag = False, num_expiry_periods = 0):
        """
        @param value: initial balance of gas available at the
            beginning of the supply contract's dispatch period.
        @type value: None (L{has_flag} = False), L{float}
            (L{has_flag} = True, L{has_expiry_flag} = False),
            or a list of length num_expiry_periods
            of L{float} (L{has_flag} = True,
            L{has_expiry_flag} = True)
        
        @param has_flag: indicates whether some sort
            of initial balance is required and given in
            parameter L{value}
        @type has_flag: L{bool}
        
        @param has_expiry_flag: indicates whether
            multiple initial balance values are
            given in parameter L{value}, i.e.,
            a list of length L{num_expiry_periods}.
            Ignored if parameter L{has_flag} = False
        @type has_expiry_flag: L{bool}
        
        @param num_expiry_periods: provides number of
            expiry periods. Ignored if parameter
            L{has_expiry_flag} = False.
        @type num_expiry_periods: L{int}
        
        @return: appropriately initialised initial balance variable
        @rtype: L{None}, L{float}, L{list} of L{float} of length
            L{num_expiry_periods}
        @raise TypeError: mismatch among parameters detected 
        """
        initial_balance = None
        if value is None:
            if has_flag:
                if has_expiry_flag:
                    initial_balance = [0.0 for i in len( num_expiry_periods )]
                else:
                    initial_balance = 0.0
                
        elif isnumeric( value ):
            if has_flag:
                if has_expiry_flag:
                    raise TypeError, "get_initial_balance: list expected for parameter 'value'"
                else:
                    initial_balance = value
                    
        elif issequence( value ):
            if has_flag:
                if has_expiry_flag:
                    if len( value ) != num_expiry_periods:
                        raise TypeError, "get_initial_balance: list of length %d expected. Got %d" % (num_expiry_periods, len( value ))
                    initial_balance = value
                else:
                    raise TypeError, "get_initial_balance: numeric value expected. Got list of length %d" % len( value )
        
        else:
            if has_flag:
                raise TypeError, "get_initial_balance: wrong type for parameter 'value'" 

        return initial_balance
    

    get_initial_balance = staticmethod( get_initial_balance )
    
    
    def set_ACC_AVG_CONTRACT_PRICE(self, value):
        """
        Sets L{ACC_AVG_CONTRACT_PRICE}. L{ACC_AVG_CONTRACT_PRICE}
        is used to price make-up gas volumes created or used-up
        (see L{gnw.supplier.Supplier.get_mup_mark_to_market_value}) during
        a given accounting peiod ([gas] year) and typically is equivalent
        to the average contract price over the entire corresponding
        accounting period.
        L{ACC_AVG_CONTRACT_PRICE} has various admissible forms as
        explained below.
        
        @param value: average contract price(s) over given accounting
            periods (the number of accounting periods is given by list
            len( L{gnw.supplier.Supplier.acc_period_tuple_list} )
            that is only initialised later during model set-up, see
            L{gnw.supplier.Supplier.collect_constraint_coeff_information}).
        @type value: can have the the following structures:
            - None type: all average prices are calculated from
                the given contract price curve on the fly.
            - sequence type:
                the average contract price for the first
                len( ACC_AVG_CONTRACT_PRICE ) accounting periods
                are taken from this sequence, if elements numeric,
                calculated on the fly from contract price curve,
                otherwise. 
        """
        self.ACC_AVG_CONTRACT_PRICE = value
        
        
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
        super( Supplier, self ).set_DISPATCH_PERIOD( value )
        nSteps = len( self.DISPATCH_PERIOD )

        self.CONTRACT_PRICE = \
            self.create_coefficient_array( self.CONTRACT_PRICE,
                                           nSteps,
                                           "Length of 'contractPrice' must match length of 'DISPATCH_PERIOD' (gnw.supplier.Supplier.set_DISPATCH_PERIOD)")
            
        self.DISCOUNT_FACTOR = \
            self.create_coefficient_array( self.DISCOUNT_FACTOR,
                                           nSteps,
                                           "Length of 'discountFactor' must match length of 'DISPATCH_PERIOD' (gnw.supplier.Supplier.set_DISPATCH_PERIOD)")


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
        super( Supplier, self ).create_lp_vars( prefix )

        self.collect_constraint_coeff_information()
        
        self.create_std_lp_vars( prefix )
        self.create_mup_and_cfw_lp_vars( prefix )


    def collect_constraint_coeff_information(self):
        """
        collect some constraint information required
        for LP variable creation (and later for model
        creation)
        """
        # acc_period_tuple_list is a list holding the
        # period tuples (START,FINAL) collected from
        # constraints having CTYPE bit ACC_PERIOD set
        # (required for make-up, carry forward and/or
        # ias39 variables and constraints).
        # Tuples will be sorted in ascending order.
        self.acc_period_tuple_list = []

        # daily_constraint_coeff_{min,max}_index_dict
        # is a dictionary holding the indices into the
        # CONSTRAINT_COEFF list for daily {minimum,maximum}
        # volume constraints (BTYPE = {0,1}, CTYPE = POS_PCT),
        # i.e., for period tuples (START,FINAL)
        # where START==FINAL.  
        self.daily_constraint_coeff_min_index_dict = {}
        self.daily_constraint_coeff_max_index_dict = {}     

        # acc_period_constraint_coeff_{min,max}_index_dict
        # is a dictionary holding the indices into the
        # CONSTRAINT_COEFF list having CTYPE bit ACC_PERIOD
        # set (required for make-up, carry forward and/or
        # ias39 variables and constraints).
        self.acc_period_constraint_coeff_min_index_dict = {}
        self.acc_period_constraint_coeff_max_index_dict = {}

        for i in xrange( len( self.CONSTRAINT_COEFF ) ):
            period_tuple = (self.CONSTRAINT_COEFF[i].START,self.CONSTRAINT_COEFF[i].FINAL)
            
            # filter out the ACC_PERIOD constraints
            if self.CONSTRAINT_COEFF[i].CTYPE & ConstraintCoeff.ConstraintType.ACC_PERIOD:
        
                if period_tuple not in self.acc_period_tuple_list:
                    self.acc_period_tuple_list.append( period_tuple )
                
                if self.CONSTRAINT_COEFF[i].BTYPE == ConstraintCoeff.BoundaryType.LB:
                    self.acc_period_constraint_coeff_min_index_dict[period_tuple] = i
                    if self.HAS_MUP or self.HAS_CFW:
                        # Switch off standard constraint lower bounds for constraint
                        # periods of make-up or carry forward. The constraint
                        # boundary is still going to be used for make-up and 
                        # carry forward features but accessed through the
                        # acc_period_constraint_coeff_{min,max}_index_dict
                        # dictionaries
                        self.CONSTRAINT_COEFF[i].CTYPE &= ~ConstraintCoeff.ConstraintType.POS_PCT
                elif self.CONSTRAINT_COEFF[i].BTYPE == ConstraintCoeff.BoundaryType.UB:
                    self.acc_period_constraint_coeff_max_index_dict[period_tuple] = i
                else: # i.e., self.CONSTRAINT_COEFF[i].BTYPE == ConstraintCoeff.BoundaryType.EQ
                    self.acc_period_constraint_coeff_min_index_dict[period_tuple] = i
                    self.acc_period_constraint_coeff_max_index_dict[period_tuple] = i

            # filter out daily gas limit constraints
            if self.CONSTRAINT_COEFF[i].CTYPE & ConstraintCoeff.ConstraintType.POS_PCT\
            and period_tuple[0] == period_tuple[1]:
                if self.CONSTRAINT_COEFF[i].BTYPE == ConstraintCoeff.BoundaryType.LB:
                    self.daily_constraint_coeff_min_index_dict[period_tuple] = i
                elif self.CONSTRAINT_COEFF[i].BTYPE == ConstraintCoeff.BoundaryType.UB:
                    self.daily_constraint_coeff_max_index_dict[period_tuple] = i
                else: # i.e., self.CONSTRAINT_COEFF[i].BTYPE == ConstraintCoeff.BoundaryType.EQ
                    self.daily_constraint_coeff_min_index_dict[period_tuple] = i
                    self.daily_constraint_coeff_max_index_dict[period_tuple] = i
                    
        # order by 'START' (ascending) and 'FINAL' (ascending)
        period_compare = lambda a, b : conditional( a[0] != b[0],
                                                    a[0] - b[0],
                                                    conditional( a[1] != b[1],
                                                                 a[1] - b[1],
                                                                 0 ) )
        self.acc_period_tuple_list.sort( cmp = period_compare )
        

    def create_std_lp_vars(self, prefix=""):
        """
        """
        nSteps = len( self.DISPATCH_PERIOD )
        self.pos_pct = numpy.array( pulp.LpVariable.matrix( prefix + self.name + "_pos_pct", range( nSteps ), lowBound = 0.0 ) )
        self.vol = numpy.array( pulp.LpVariable.matrix( prefix + self.name + "_vol", range( nSteps ), lowBound = 0.0 ) )
        

    def create_mup_and_cfw_lp_vars(self, prefix=""):
        """
        """
        if self.HAS_MUP or self.HAS_CFW:
            nPeriods = len( self.acc_period_tuple_list )
            self.top_period_trig = numpy.array( pulp.LpVariable.matrix( prefix + self.name + "_top_period_trig",
                                                                        range( nPeriods ),
                                                                        lowBound = 0, upBound = 1,
                                                                        cat = pulp.LpInteger ) )
        self.create_mup_lp_vars( prefix )
        self.create_cfw_lp_vars( prefix )



    def create_mup_lp_vars(self, prefix=""):
        """
        """
        self.collect_mup_constraint_coeff_information()
        
        if self.HAS_MUP:
            nPeriods = len( self.acc_period_tuple_list )
            self.mup_period_vol_bal = numpy.array( pulp.LpVariable.matrix( prefix + self.name + "_mup_period_vol_bal",
                                                                           range( nPeriods ),
                                                                           lowBound = 0.0 ) )
            self.mup_period_vol_inc = numpy.array( pulp.LpVariable.matrix( prefix + self.name + "_mup_period_vol_inc",
                                                                           range( nPeriods ),
                                                                           lowBound = 0.0 ) )
            self.mup_period_vol_dec = numpy.array( pulp.LpVariable.matrix( prefix + self.name + "_mup_period_vol_dec",
                                                                           range( nPeriods ),
                                                                           lowBound = 0.0 ) )
            self.mup_period_vol_chg = numpy.array( pulp.LpVariable.matrix( prefix + self.name + "_mup_period_vol_chg",
                                                                           range( nPeriods ) ) ) # is free variable, may be replaced by affine expression
            
            nSteps = len( self.DISPATCH_PERIOD )
            self.mup_trig = numpy.array( pulp.LpVariable.matrix( prefix + self.name + "_mup_trig",
                                                                 range( nSteps ),
                                                                 lowBound = 0, upBound = 1,
                                                                 cat = pulp.LpInteger ) )
            self.mup_vol = numpy.array( pulp.LpVariable.matrix( prefix + self.name + "_mup_vol",
                                                                range( nSteps ),
                                                                lowBound = 0.0 ) )

            if self.HAS_MUP_EXPIRY:
                self.mup_period_vol_exp_bal = numpy.array( [[pulp.LpVariable( prefix + self.name + "_mup_period_vol_exp_bal_%d_%d" % (k,i), lowBound = 0.0 )
                                                             for i in range( self.MUP_NUM_EXPIRY_PERIODS )] for k in range( nPeriods )] )
                self.mup_period_vol_exp_dec = numpy.array( [[pulp.LpVariable( prefix + self.name + "_mup_period_vol_exp_dec_%d_%d" % (k,i), lowBound = 0.0 )
                                                             for i in range( self.MUP_NUM_EXPIRY_PERIODS )] for k in range( nPeriods )] )
                self.mup_period_vol_exp = numpy.array( pulp.LpVariable.matrix( prefix + self.name + "_mup_period_vol_exp",
                                                                               range( nPeriods ),
                                                                               lowBound = 0.0 ) )


    def create_cfw_lp_vars(self, prefix=""):
        """
        """
        self.collect_cfw_constraint_coeff_information()
        
        if self.HAS_CFW:
            nPeriods = len( self.acc_period_tuple_list )
            self.cfw_period_vol_bal = numpy.array( pulp.LpVariable.matrix( prefix + self.name + "_cfw_period_vol_bal",
                                                                           range( nPeriods ),
                                                                           lowBound = 0.0 ) )
            self.cfw_period_vol_inc = numpy.array( pulp.LpVariable.matrix( prefix + self.name + "_cfw_period_vol_inc",
                                                                           range( nPeriods ),
                                                                           lowBound = 0.0 ) )
            self.cfw_period_vol_dec = numpy.array( pulp.LpVariable.matrix( prefix + self.name + "_cfw_period_vol_dec",
                                                                           range( nPeriods ),
                                                                           lowBound = 0.0 ) )
            self.cfw_period_vol_chg = numpy.array( pulp.LpVariable.matrix( prefix + self.name + "_cfw_period_vol_chg",
                                                                           range( nPeriods ) ) ) # is free variable, may be replaced by affine expression

            if self.HAS_CFW_EXPIRY:
                self.cfw_period_vol_exp_bal = numpy.array( [[pulp.LpVariable( prefix + self.name + "_cfw_period_vol_exp_bal_%d_%d" % (k,i), lowBound = 0.0 )
                                                             for i in range( self.CFW_NUM_EXPIRY_PERIODS )] for k in range( nPeriods )] )
                self.cfw_period_vol_exp_dec = numpy.array( [[pulp.LpVariable( prefix + self.name + "_cfw_period_vol_exp_dec_%d_%d" % (k,i), lowBound = 0.0 )
                                                             for i in range( self.CFW_NUM_EXPIRY_PERIODS )] for k in range( nPeriods )] )
                self.cfw_period_vol_exp = numpy.array( pulp.LpVariable.matrix( prefix + self.name + "_cfw_period_vol_exp",
                                                                               range( nPeriods ),
                                                                               lowBound = 0.0 ) )

            
    def collect_mup_constraint_coeff_information(self):
        """
        """
        self.mup_bnd_ccoeff_min_period_index_dict = None
        self.mup_bnd_ccoeff_max_period_index_dict = None
        
        if self.HAS_MUP:
            # mup_bnd_ccoeff_{min,max}_period_index_dict is a dictionary holding
            # the indices into the CONSTRAINT_COEFF list for make-up period
            # {minimum,maximum} use-up/create boundary constraints
            # (BTYPE = {0,1}, CTYPE = MUP_BND_PCT).
            self.mup_bnd_ccoeff_min_period_index_dict = {}
            self.mup_bnd_ccoeff_max_period_index_dict = {}
  
            for i in xrange( len( self.CONSTRAINT_COEFF ) ):
                period_tuple = (self.CONSTRAINT_COEFF[i].START,self.CONSTRAINT_COEFF[i].FINAL)
                
                # filter out the make-up gas period make-up use-up/creation limit constraints
                if self.CONSTRAINT_COEFF[i].CTYPE & ConstraintCoeff.ConstraintType.MUP_BND_PCT:
                    if self.CONSTRAINT_COEFF[i].BTYPE == ConstraintCoeff.BoundaryType.LB:
                        self.mup_bnd_ccoeff_min_period_index_dict[period_tuple] = i
                    elif self.CONSTRAINT_COEFF[i].BTYPE == ConstraintCoeff.BoundaryType.UB:
                        self.mup_bnd_ccoeff_max_period_index_dict[period_tuple] = i
                    else:
                        raise ValueError, "create_mup_lp_vars: constraint with CTYPE MUP_BND_PCT and BTYPE 2 (=EQ) in CONSTRAINT_COEFF[%d]" % i
        
                    
    def collect_cfw_constraint_coeff_information(self):
        """
        """
        self.cfw_bnd_ccoeff_min_period_index_dict = None
        self.cfw_bnd_ccoeff_max_period_index_dict = None
        
        if self.HAS_CFW:
            # cfw_bnd_ccoeff_{min,max}_period_index_dict is a dictionary holding
            # the indices into the CONSTRAINT_COEFF list for carry forward period
            # {minimum,maximum} use-up/create boundary constraints
            # (BTYPE = {0,1}, CTYPE = CFW_BND_PCT).
            self.cfw_bnd_ccoeff_min_period_index_dict = {}
            self.cfw_bnd_ccoeff_max_period_index_dict = {}
  
            for i in xrange( len( self.CONSTRAINT_COEFF ) ):
                period_tuple = (self.CONSTRAINT_COEFF[i].START,self.CONSTRAINT_COEFF[i].FINAL)
                
                # filter out the make-up gas period make-up use-up/creation limit constraints
                if self.CONSTRAINT_COEFF[i].CTYPE & ConstraintCoeff.ConstraintType.CFW_BND_PCT:
                    if self.CONSTRAINT_COEFF[i].BTYPE == ConstraintCoeff.BoundaryType.LB:
                        self.cfw_bnd_ccoeff_min_period_index_dict[period_tuple] = i
                    elif self.CONSTRAINT_COEFF[i].BTYPE == ConstraintCoeff.BoundaryType.UB:
                        self.cfw_bnd_ccoeff_max_period_index_dict[period_tuple] = i
                    else:
                        raise ValueError, "create_cfw_lp_vars: constraint with CTYPE CFW_BND_PCT and BTYPE 2 (=EQ) in CONSTRAINT_COEFF[%d]" % i
                    

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
        super( Supplier, self ).create_model( prefix )
        
        self.create_constraints()
        self.create_objective()


    def create_constraints(self):
        """
        """
        self.create_std_constraints()
#        self.create_sfp_constraints()
        self.create_mup_and_cfw_constraints()
        self.create_ias39_constraints()


    def create_objective(self):
        """
        """
        self.create_std_objective()
#        self.create_sfp_objecitve()
        self.create_mup_objective()
#        self.create_cfw_objective()
        
        
    def create_std_constraints(self):
        """
        """
        nSteps = len( self.DISPATCH_PERIOD )
        for t in xrange( nSteps ):
            self.constraint_list.append( self.vol[t] == self.pos_pct[t]*self.ACQ*self.DISPATCH_PERIOD[t] )
        
        # multi-dispatch-period min/max volume constraints
        for i in xrange( len( self.CONSTRAINT_COEFF ) ):
            
            dispatchPeriodIdx = xrange( self.CONSTRAINT_COEFF[i].START, self.CONSTRAINT_COEFF[i].FINAL + 1 )
            
            if self.CONSTRAINT_COEFF[i].CTYPE & ConstraintCoeff.ConstraintType.POS_PCT:
                if self.CONSTRAINT_COEFF[i].BTYPE == ConstraintCoeff.BoundaryType.LB:
                    self.constraint_list.append( pulp.lpSum( [self.pos_pct[t]*self.DISPATCH_PERIOD[t] for t in dispatchPeriodIdx] )
                                                 >= self.CONSTRAINT_COEFF[i].BOUND )
                    
                elif self.CONSTRAINT_COEFF[i].BTYPE == ConstraintCoeff.BoundaryType.UB:
                    self.constraint_list.append( pulp.lpSum( [self.pos_pct[t]*self.DISPATCH_PERIOD[t] for t in dispatchPeriodIdx] )
                                                 <= self.CONSTRAINT_COEFF[i].BOUND )
                    
                elif self.CONSTRAINT_COEFF[i].BTYPE == ConstraintCoeff.BoundaryType.EQ:
                    self.constraint_list.append( pulp.lpSum( [self.pos_pct[t]*self.DISPATCH_PERIOD[t] for t in dispatchPeriodIdx] )
                                                 == self.CONSTRAINT_COEFF[i].BOUND )
                    
                else:
                    raise ValueError, "create_model: Unknown boundary type %d encountered for constraint number %d" % (self.CONSTRAINT_COEFF[i].BTYPE,i)
        

    def create_mup_and_cfw_constraints(self):
        """
        """
        if self.HAS_MUP or self.HAS_CFW:
            nPeriods = len( self.acc_period_tuple_list )
            for k in xrange( nPeriods ):
                period_tuple = self.acc_period_tuple_list[k]
                START = period_tuple[0]
                FINAL = period_tuple[1]
                dispatchPeriodIdx = xrange( START, FINAL + 1 )
                
                PERIOD_VOL_LB = self.CONSTRAINT_COEFF[self.acc_period_constraint_coeff_min_index_dict[period_tuple]].BOUND*self.ACQ
                PERIOD_VOL_UB = self.CONSTRAINT_COEFF[self.acc_period_constraint_coeff_max_index_dict[period_tuple]].BOUND*self.ACQ

                period_vol = pulp.lpSum( [self.vol[t] for t in dispatchPeriodIdx] )

                if True:
                    if PERIOD_VOL_UB:
                        self.constraint_list.append( (PERIOD_VOL_LB - period_vol)/PERIOD_VOL_UB <= self.top_period_trig[k] )
                        self.constraint_list.append( self.top_period_trig[k] <= (PERIOD_VOL_LB - period_vol)/PERIOD_VOL_UB + 1.0 )
                    else:
                        self.constraint_list.append( self.top_period_trig[k] == 0 )
                else:
                    # avoid potential division by 0 (=PERIOD_VOL_UB)
                    # but produces somehow infeasibilities of the problem
                    self.constraint_list.append( PERIOD_VOL_LB - period_vol <= PERIOD_VOL_UB*self.top_period_trig[k] )
                    self.constraint_list.append( PERIOD_VOL_UB*self.top_period_trig[k] <= PERIOD_VOL_LB - period_vol + PERIOD_VOL_UB )

                if self.HAS_MUP and self.HAS_CFW:
                    self.constraint_list.append( period_vol - PERIOD_VOL_LB == self.cfw_period_vol_chg[k] - self.mup_period_vol_chg[k] )

                if self.HAS_MUP and not self.HAS_CFW:
                    self.constraint_list.append( self.mup_period_vol_chg[k] >= PERIOD_VOL_LB - period_vol )
                    self.constraint_list.append( self.mup_period_vol_chg[k] <= PERIOD_VOL_LB - period_vol + (1.0 - self.top_period_trig[k])*(PERIOD_VOL_UB - PERIOD_VOL_LB) )

                if self.HAS_CFW and not self.HAS_MUP:
                    self.constraint_list.append( self.cfw_period_vol_chg[k] == period_vol - PERIOD_VOL_LB )
                        
            self.create_mup_constraints()
            self.create_cfw_constraints()
        
        
    def create_mup_constraints(self):
        """
        """
        if self.HAS_MUP:
            nPeriods = len( self.acc_period_tuple_list )
            for k in xrange( nPeriods ):
                period_tuple = self.acc_period_tuple_list[k]
                START = period_tuple[0]
                FINAL = period_tuple[1]
                dispatchPeriodIdx = xrange( START, FINAL + 1 )
                
                PERIOD_VOL_LB = self.CONSTRAINT_COEFF[self.acc_period_constraint_coeff_min_index_dict[period_tuple]].BOUND*self.ACQ
                PERIOD_VOL_UB = self.CONSTRAINT_COEFF[self.acc_period_constraint_coeff_max_index_dict[period_tuple]].BOUND*self.ACQ
            
                if period_tuple in self.mup_bnd_ccoeff_min_period_index_dict:
                    MUP_PERIOD_VOL_LB = max( self.CONSTRAINT_COEFF[self.mup_bnd_ccoeff_min_period_index_dict[period_tuple]].BOUND*self.ACQ, PERIOD_VOL_LB - PERIOD_VOL_UB )
                else:
                    MUP_PERIOD_VOL_LB = PERIOD_VOL_LB - PERIOD_VOL_UB
                    
                if period_tuple in self.mup_bnd_ccoeff_max_period_index_dict:
                    MUP_PERIOD_VOL_UB = min( self.CONSTRAINT_COEFF[self.mup_bnd_ccoeff_max_period_index_dict[period_tuple]].BOUND*self.ACQ, PERIOD_VOL_LB )
                else:
                    MUP_PERIOD_VOL_UB = PERIOD_VOL_LB
                
                # change of make-up gas equations 
                self.constraint_list.append( self.mup_period_vol_chg[k] == self.mup_period_vol_inc[k] - self.mup_period_vol_dec[k] )

                if not self.HAS_MUP_EXPIRY:
                    # cannot use-up more make-up gas in any period than is actually available
                    self.constraint_list.append( self.mup_period_vol_bal[k] - self.mup_period_vol_dec[k] >= 0.0 )
                    # make-up gas balance equations
                    if k == 0:
                        self.constraint_list.append( self.mup_period_vol_bal[k] == self.MUP_INITIAL_BALANCE*self.ACQ )
                    else:
                        self.constraint_list.append( self.mup_period_vol_bal[k] == self.mup_period_vol_bal[k-1] + self.mup_period_vol_chg[k-1] )
    
                else:
                    self.constraint_list.append( self.mup_period_vol_bal[k] == pulp.lpSum( [self.mup_period_vol_exp_bal[k,i] for i in xrange( self.MUP_NUM_EXPIRY_PERIODS )] ) )
                    self.constraint_list.append( self.mup_period_vol_dec[k] == pulp.lpSum( [self.mup_period_vol_exp_dec[k,i] for i in xrange( self.MUP_NUM_EXPIRY_PERIODS )] ) )
                    # record the amount of expired make-up gas for accounting period k
                    self.constraint_list.append( self.mup_period_vol_exp[k] == self.mup_period_vol_exp_bal[k,0] - self.mup_period_vol_exp_dec[k,0] ) # forall k, i == 0
                    
                    if k == 0:
                        self.constraint_list += [self.mup_period_vol_exp_bal[k,i] == self.MUP_INITIAL_BALANCE[i]*self.ACQ
                                                 for i in xrange( self.MUP_NUM_EXPIRY_PERIODS )]
                    else:
                        self.constraint_list.append( self.mup_period_vol_exp_bal[k, self.MUP_NUM_EXPIRY_PERIODS-1] == self.mup_period_vol_inc[k-1] ) 
                        self.constraint_list += [self.mup_period_vol_exp_bal[k,i-1] == self.mup_period_vol_exp_bal[k-1,i] - self.mup_period_vol_exp_dec[k-1,i]
                                                 for i in xrange( self.MUP_NUM_EXPIRY_PERIODS ) if i > 0]
                    self.constraint_list += [self.mup_period_vol_exp_bal[k,i] - self.mup_period_vol_exp_dec[k,i] >= 0.0
                                             for i in xrange( self.MUP_NUM_EXPIRY_PERIODS )]
                    
#                self.constraint_list.append( self.mup_period_vol_inc[k] <= self.top_period_trig[k]*MUP_PERIOD_VOL_UB )
#                self.constraint_list.append( self.mup_period_vol_dec[k] <= -(1.0 - self.top_period_trig[k])*MUP_PERIOD_VOL_LB )
                self.constraint_list.append( self.mup_period_vol_inc[k] <= self.top_period_trig[k]*PERIOD_VOL_LB )
                self.constraint_list.append( self.mup_period_vol_dec[k] <= (1.0 - self.top_period_trig[k])*(PERIOD_VOL_UB - PERIOD_VOL_LB) )

                self.constraint_list.append( MUP_PERIOD_VOL_LB <= self.mup_period_vol_chg[k] )
                self.constraint_list.append( self.mup_period_vol_chg[k] <= MUP_PERIOD_VOL_UB )
                
                self.constraint_list.append( self.mup_period_vol_dec[k] == pulp.lpSum( [self.mup_vol[d] for d in dispatchPeriodIdx] ) )
                for t in dispatchPeriodIdx:
                    self.constraint_list.append( self.mup_vol[t] <= self.vol[t] )
                    self.constraint_list.append( self.mup_vol[t] <= self.mup_trig[t]*self.CONSTRAINT_COEFF[self.daily_constraint_coeff_max_index_dict[(t,t)]].BOUND*self.ACQ )
                    self.constraint_list.append( self.mup_trig[t] <= self.mup_vol[t] )
                    self.constraint_list.append( self.mup_trig[t] <= self.mup_period_vol_dec[k] )
                    if t < FINAL:
                        self.constraint_list.append( self.mup_trig[t] <= self.mup_trig[t + 1] )
                        
                        period_vol = pulp.lpSum( [self.vol[d] for d in xrange( t + 1, FINAL + 1)] )
                        
                        if True:
                            if PERIOD_VOL_UB:
                                self.constraint_list.append( (self.mup_period_vol_dec[k] - self.mup_vol[t] - period_vol )/PERIOD_VOL_UB <= self.mup_trig[t] )
                                self.constraint_list.append( self.mup_trig[t] <= (self.mup_period_vol_dec[k] - self.mup_vol[t] - period_vol )/PERIOD_VOL_UB + 1.0 )
                            else:
                                self.constraint_list.append( self.mup_trig[t] == 0 )
                        else:
                            # avoid potential division by 0 (=PERIOD_VOL_UB)
                            # but produces somehow infeasibilities of the problem
                            self.constraint_list.append( self.mup_period_vol_dec[k] - self.mup_vol[t] - period_vol <= PERIOD_VOL_UB*self.mup_trig[t] )
                            self.constraint_list.append( PERIOD_VOL_UB*self.mup_trig[t] <= self.mup_period_vol_dec[k] - self.mup_vol[t] - period_vol + PERIOD_VOL_UB )


    def create_cfw_constraints(self):
        """
        """
        if self.HAS_CFW:
            nPeriods = len( self.acc_period_tuple_list )
            for k in xrange( nPeriods ):
                period_tuple = self.acc_period_tuple_list[k]
                START = period_tuple[0]
                FINAL = period_tuple[1]
                dispatchPeriodIdx = xrange( START, FINAL + 1 )
                
                PERIOD_VOL_LB = self.CONSTRAINT_COEFF[self.acc_period_constraint_coeff_min_index_dict[period_tuple]].BOUND*self.ACQ
                PERIOD_VOL_UB = self.CONSTRAINT_COEFF[self.acc_period_constraint_coeff_max_index_dict[period_tuple]].BOUND*self.ACQ

                if period_tuple in self.cfw_bnd_ccoeff_min_period_index_dict:
                    CFW_PERIOD_VOL_LB = max( self.CONSTRAINT_COEFF[self.cfw_bnd_ccoeff_min_period_index_dict[period_tuple]].BOUND*self.ACQ, -PERIOD_VOL_LB )
                else:
                    CFW_PERIOD_VOL_LB = -PERIOD_VOL_LB
                    
                if period_tuple in self.cfw_bnd_ccoeff_max_period_index_dict:
                    CFW_PERIOD_VOL_UB = min( self.CONSTRAINT_COEFF[self.cfw_bnd_ccoeff_max_period_index_dict[period_tuple]].BOUND*self.ACQ, PERIOD_VOL_UB - PERIOD_VOL_LB )
                else:
                    CFW_PERIOD_VOL_UB = PERIOD_VOL_UB - PERIOD_VOL_LB
                            
                # change of make-up gas equations 
                self.constraint_list.append( self.cfw_period_vol_chg[k] == self.cfw_period_vol_inc[k] - self.cfw_period_vol_dec[k] )

                if not self.HAS_CFW_EXPIRY:
                    # cannot use-up more make-up gas in any period than is actually available
                    self.constraint_list.append( self.cfw_period_vol_bal[k] - self.cfw_period_vol_dec[k] >= 0.0 )
                    # make-up gas balance equations
                    if k == 0:
                        self.constraint_list.append( self.cfw_period_vol_bal[k] == self.CFW_INITIAL_BALANCE*self.ACQ )
                    else:
                        self.constraint_list.append( self.cfw_period_vol_bal[k] == self.cfw_period_vol_bal[k-1] + self.cfw_period_vol_chg[k-1] )
    
                else:
                    self.constraint_list.append( self.cfw_period_vol_bal[k] == pulp.lpSum( [self.cfw_period_vol_exp_bal[k,i] for i in xrange( self.CFW_NUM_EXPIRY_PERIODS )] ) )
                    self.constraint_list.append( self.cfw_period_vol_dec[k] == pulp.lpSum( [self.cfw_period_vol_exp_dec[k,i] for i in xrange( self.CFW_NUM_EXPIRY_PERIODS )] ) )
                    # record the amount of expired carry-forward gas for accounting period k
                    self.constraint_list.append( self.cfw_period_vol_exp[k] == self.cfw_period_vol_exp_bal[k,0] - self.cfw_period_vol_exp_dec[k,0] )
                    
                    if k == 0:
                        self.constraint_list += [self.cfw_period_vol_exp_bal[k,i] == self.CFW_INITIAL_BALANCE[i]*self.ACQ
                                                 for i in xrange( self.CFW_NUM_EXPIRY_PERIODS )]
                    else:
                        self.constraint_list.append( self.cfw_period_vol_exp_bal[k,self.CFW_NUM_EXPIRY_PERIODS-1] == self.cfw_period_vol_inc[k-1] )
                        self.constraint_list += [self.cfw_period_vol_exp_bal[k,i-1] == self.cfw_period_vol_exp_bal[k-1,i] - self.cfw_period_vol_exp_dec[k-1,i]
                                                 for i in xrange( self.CFW_NUM_EXPIRY_PERIODS ) if i > 0]
                            
                    self.constraint_list += [self.cfw_period_vol_exp_bal[k,i] - self.cfw_period_vol_exp_dec[k,i] >= 0.0
                                             for i in xrange( self.CFW_NUM_EXPIRY_PERIODS )]

                self.constraint_list.append( self.cfw_period_vol_inc[k] <= (1.0 - self.top_period_trig[k])*CFW_PERIOD_VOL_UB )
                self.constraint_list.append( self.cfw_period_vol_dec[k] <= -self.top_period_trig[k]*CFW_PERIOD_VOL_LB )

                self.constraint_list.append( CFW_PERIOD_VOL_LB <= self.cfw_period_vol_chg[k] )
                self.constraint_list.append( self.cfw_period_vol_chg[k] <= CFW_PERIOD_VOL_UB )

                
    def create_ias39_constraints(self):
        """
        """
        if self.HAS_IAS39:
            
            MUP_INIT = conditional( self.HAS_MUP,
                                    conditional( not self.HAS_MUP_EXPIRY,
                                                 self.MUP_INITIAL_BALANCE,
                                                 sum( [self.MUP_INITIAL_BALANCE[i] for i in xrange( self.MUP_NUM_EXPIRY_PERIODS )] )),
                                    0.0 )
            CFW_INIT = conditional( self.HAS_CFW,
                                    conditional( not self.HAS_CFW_EXPIRY,
                                                 self.CFW_INITIAL_BALANCE,
                                                 sum( [self.CFW_INITIAL_BALANCE[i] for i in xrange( self.CFW_NUM_EXPIRY_PERIODS )] )),
                                    0.0 )
            
            nPeriods = len( self.acc_period_tuple_list )
            
            PERIOD_VOL_LB = [0.0]*nPeriods
            period_vol = [pulp.LpAffineExpression( 0.0 )]*nPeriods
            
            for k in xrange( nPeriods ):
                period_tuple = self.acc_period_tuple_list[k]
                START = period_tuple[0]
                FINAL = period_tuple[1]
                dispatchPeriodIdx = xrange( START, FINAL + 1 )
                
                PERIOD_VOL_LB[k] = self.CONSTRAINT_COEFF[self.acc_period_constraint_coeff_min_index_dict[period_tuple]].BOUND*self.ACQ
                period_vol[k] = pulp.lpSum( [self.vol[t] for t in dispatchPeriodIdx] )
                
            # On average take ACQmin + initial make-up - initial carry forward
            self.constraint_list.append( pulp.lpSum( [period_vol[k] for k in xrange( nPeriods )] ) == (MUP_INIT - CFW_INIT)*self.ACQ + pulp.lpSum( [PERIOD_VOL_LB[k] for k in xrange( nPeriods )] ) )
          
            if self.HAS_MUP:
                # ZERO make-up balance at the end of the optimisation
                self.constraint_list.append( MUP_INIT*self.ACQ + pulp.lpSum( [self.mup_period_vol_chg[k] for k in xrange( nPeriods )] ) == 0 )
            if self.HAS_CFW:
                # ZERO carry forward balance at the end of the optimisation
                self.constraint_list.append( CFW_INIT*self.ACQ + pulp.lpSum( [self.cfw_period_vol_chg[k] for k in xrange( nPeriods )] ) == 0 ) 
        
        
    def create_std_objective(self):
        """
        """
        self.objective_list.append( self.get_std_mark_to_market_value() )

        
    def create_mup_objective(self):
        """
        """
        self.objective_list.append( self.get_mup_mark_to_market_value() )
        

    def get_lp_vars(self):
        """
        This method returns a list containing all
        lp variables contained in self and any
        of its super classes.
        
        @return: list of lp variables
        @rtype: L{list} of L{pulp.LpVariable}
        """
        lp_vars_list = self.pos_pct.tolist()
        lp_vars_list += self.vol.tolist()
        if self.HAS_MUP or self.HAS_CFW:
            lp_vars_list += self.top_period_trig.tolist()
        if self.HAS_MUP:
            lp_vars_list += self.mup_period_vol_bal.tolist()
            lp_vars_list += self.mup_period_vol_dec.tolist()
            if self.HAS_MUP_EXPIRY:
                lp_vars_list += self.mup_period_vol_exp.tolist()
                lp_vars_list += self.mup_period_vol_exp_bal.tolist()
                lp_vars_list += self.mup_period_vol_exp_dec.tolist()
            lp_vars_list += self.mup_period_vol_inc.tolist()
            lp_vars_list += self.mup_period_vol_chg.tolist()
            lp_vars_list += self.mup_trig.tolist()
            lp_vars_list += self.mup_vol.tolist()
        if self.HAS_CFW:
            lp_vars_list += self.cfw_period_vol_bal.tolist()
            lp_vars_list += self.cfw_period_vol_dec.tolist()
            if self.HAS_CFW_EXPIRY:
                lp_vars_list += self.cfw_period_vol_exp.tolist()
                lp_vars_list += self.cfw_period_vol_exp_bal.tolist()
                lp_vars_list += self.cfw_period_vol_exp_dec.tolist()
            lp_vars_list += self.cfw_period_vol_inc.tolist()
            lp_vars_list += self.cfw_period_vol_chg.tolist()
            
        return super( Supplier, self ).get_lp_vars() + lp_vars_list

            
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
        
        fmt_dict.update({'SB' :                 FmtDictEntry( [ self.ifmt ], 'sell/buy [1/-1]',             0, None,            False,  self.SB ),
                         'ACQ' :                FmtDictEntry( [ self.ffmt ], 'ACQ [MWh]',                   0, None,            False,  self.ACQ ),
                         'HAS_SFP' :            FmtDictEntry( [ self.ifmt ], 'HAS_SFP',                     0, None,            False,  self.HAS_SFP ),
                         'HAS_MUP' :            FmtDictEntry( [ self.ifmt ], 'HAS_MUP',                     0, None,            False,  self.HAS_MUP ),
                         'HAS_CFW' :            FmtDictEntry( [ self.ifmt ], 'HAS_CFW',                     0, None,            False,  self.HAS_CFW ),
                         'HAS_IAS39' :          FmtDictEntry( [ self.ifmt ], 'HAS_IAS39',                   0, None,            False,  self.HAS_IAS39 ),
                         'CONTRACT_PRICE' :     FmtDictEntry( [ self.ffmt ], 'CONTRACT_PRICE[t] [EUR/MWh]', 1, (nSteps,),       False,  self.CONTRACT_PRICE ),
                         'DF' :                 FmtDictEntry( [ self.ffmt ], 'DF[t]',                       1, (nSteps,),       False,  self.DISCOUNT_FACTOR ),
                         'pos_pct' :            FmtDictEntry( [ self.ffmt ], 'pos_pct[t] [MW%]',            1, (nSteps,),       True,   self.pos_pct ),
                         'vol' :                FmtDictEntry( [ self.ffmt ], 'vol[t] [MWh]',                1, (nSteps,),       True,   self.vol )})
        
        if self.HAS_MUP or self.HAS_CFW:
            nPeriods = len( self.acc_period_tuple_list )
            fmt_dict.update({'top_period_trig' :            FmtDictEntry( [ self.ifmt ], 'top_period_trig[k]',          1,  (nPeriods,),     True,   self.top_period_trig )})
        
        if self.HAS_MUP:
            fmt_dict.update({'HAS_MUP_EXPIRY' :             FmtDictEntry( [ self.ifmt ], 'HAS_MUP_EXPIRY',              0,  None,               False,  self.HAS_MUP_EXPIRY ),
                             'MUP_NUM_EXPIRY_PERIODS' :     FmtDictEntry( [ self.ifmt ], 'MUP_NUM_EXPIRY_PERIODS',      0,  None,               False,  self.MUP_NUM_EXPIRY_PERIODS ),
                             'MUP_CREATE_PRICE_RATE' :      FmtDictEntry( [ self.ffmt ], 'MUP_CREATE_PRICE_RATE',       0,  None,               False,  self.MUP_CREATE_PRICE_RATE ),
                             'MUP_USEUP_PRICE_RATE' :       FmtDictEntry( [ self.ffmt ], 'MUP_USEUP_PRICE_RATE',        0,  None,               False,  self.MUP_USEUP_PRICE_RATE ),
                             'MUP_INITIAL_BALANCE' :        conditional(self.HAS_MUP_EXPIRY,
                                                                        FmtDictEntry( [ self.ffmt ], 'MUP_INITIAL_BALANCE[i] [MW%]',  1,  (self.MUP_NUM_EXPIRY_PERIODS,), False,  self.MUP_INITIAL_BALANCE ),
                                                                        FmtDictEntry( [ self.ffmt ], 'MUP_INITIAL_BALANCE [MW%]',     0,  None,                           False,  self.MUP_INITIAL_BALANCE )),
                             'mup_period_vol_bal' :         FmtDictEntry( [ self.ffmt ], 'mup_period_vol_bal[k] [MWh]', 1,  (nPeriods,),        True,   self.mup_period_vol_bal ),
                             'mup_period_vol_dec' :         FmtDictEntry( [ self.ffmt ], 'mup_period_vol_dec[k] [MWh]', 1,  (nPeriods,),        True,   self.mup_period_vol_dec ),
                             'mup_period_vol_inc' :         FmtDictEntry( [ self.ffmt ], 'mup_period_vol_inc[k] [MWh]', 1,  (nPeriods,),        True,   self.mup_period_vol_inc ),
                             'mup_period_vol_chg' :         FmtDictEntry( [ self.ffmt ], 'mup_period_vol_chg[k] [MWh]', 1,  (nPeriods,),        True,   self.mup_period_vol_chg ),
                             'mup_trig' :                   FmtDictEntry( [ self.ifmt ], 'mup_trig[t]',                 1,  (nSteps,),          True,   self.mup_trig ),
                             'mup_vol' :                    FmtDictEntry( [ self.ffmt ], 'mup_vol[t] [MWh]',            1,  (nSteps,),          True,   self.mup_vol )})

            if self.HAS_MUP_EXPIRY:
                fmt_dict.update({'mup_period_vol_exp' :
                                    FmtDictEntry( [ self.ffmt ],
                                                  'mup_period_vol_exp[k] [MWh]',
                                                  1, (nPeriods,), True,
                                                  self.mup_period_vol_exp ),
                                 'mup_period_vol_exp_bal' :
                                    FmtDictEntry( [ self.ffmt ]*self.MUP_NUM_EXPIRY_PERIODS,
                                                  'mup_period_vol_exp_bal[k,%d] [MWh]',
                                                  2, (nPeriods,self.MUP_NUM_EXPIRY_PERIODS), True,
                                                  self.mup_period_vol_exp_bal ),
                                 'mup_period_vol_exp_dec' :
                                    FmtDictEntry( [ self.ffmt ]*self.MUP_NUM_EXPIRY_PERIODS,
                                                  'mup_period_vol_exp_dec[k,%d] [MWh]',
                                                  2, (nPeriods,self.MUP_NUM_EXPIRY_PERIODS), True,
                                                  self.mup_period_vol_exp_dec )})

        if self.HAS_CFW:
            fmt_dict.update({'HAS_CFW_EXPIRY' :             FmtDictEntry( [ self.ifmt ], 'HAS_CFW_EXPIRY',              0,  None,               False,  self.HAS_CFW_EXPIRY ),
                             'CFW_NUM_EXPIRY_PERIODS' :     FmtDictEntry( [ self.ifmt ], 'CFW_NUM_EXPIRY_PERIODS',      0,  None,               False,  self.CFW_NUM_EXPIRY_PERIODS ),
                             'CFW_INITIAL_BALANCE' :        conditional(self.HAS_CFW_EXPIRY,
                                                                        FmtDictEntry( [ self.ffmt ], 'CFW_INITIAL_BALANCE[i] [MW%]',  1,  (self.CFW_NUM_EXPIRY_PERIODS,), False,  self.CFW_INITIAL_BALANCE ),
                                                                        FmtDictEntry( [ self.ffmt ], 'CFW_INITIAL_BALANCE [MW%]',     0,  None,                           False,  self.CFW_INITIAL_BALANCE )),
                             'cfw_period_vol_bal' :         FmtDictEntry( [ self.ffmt ], 'cfw_period_vol_bal[k] [MWh]', 1,  (nPeriods,),        True,   self.cfw_period_vol_bal ),
                             'cfw_period_vol_dec' :         FmtDictEntry( [ self.ffmt ], 'cfw_period_vol_dec[k] [MWh]', 1,  (nPeriods,),        True,   self.cfw_period_vol_dec ),
                             'cfw_period_vol_inc' :         FmtDictEntry( [ self.ffmt ], 'cfw_period_vol_inc[k] [MWh]', 1,  (nPeriods,),        True,   self.cfw_period_vol_inc ),
                             'cfw_period_vol_chg' :         FmtDictEntry( [ self.ffmt ], 'cfw_period_vol_chg[k] [MWh]', 1,  (nPeriods,),        True,   self.cfw_period_vol_chg )})

            if self.HAS_CFW_EXPIRY:
                fmt_dict.update({'cfw_period_vol_exp' :
                                    FmtDictEntry( [ self.ffmt ],
                                                  'cfw_period_vol_exp[k] [MWh]',
                                                  1, (nPeriods,), True,
                                                  self.cfw_period_vol_exp ),
                                 'cfw_period_vol_exp_bal' :
                                    FmtDictEntry( [ self.ffmt ]*self.CFW_NUM_EXPIRY_PERIODS,
                                                  'cfw_period_vol_exp_bal[k,%d] [MWh]',
                                                  2, (nPeriods,self.CFW_NUM_EXPIRY_PERIODS), True,
                                                  self.cfw_period_vol_exp_bal ),
                                 'cfw_period_vol_exp_dec' :
                                    FmtDictEntry( [ self.ffmt ]*self.CFW_NUM_EXPIRY_PERIODS,
                                                  'cfw_period_vol_exp_dec[k,%d] [MWh]',
                                                  2, (nPeriods, self.CFW_NUM_EXPIRY_PERIODS), True,
                                                  self.cfw_period_vol_exp_dec )})
            
        super( Supplier, self ).update_fmt_dict( fmt_dict )


    def get_results(self):
        """
        """
        nSteps = len( self.DISPATCH_PERIOD )
        
        if self.HAS_MUP:
            volume = [-self.SB*(self.vol[t].varValue - self.mup_vol[t].varValue) for t in xrange( nSteps )]
        else:
            volume = [-self.SB*self.vol[t].varValue for t in xrange( nSteps )]

        cashflow = [-self.CONTRACT_PRICE[t]*volume[t] for t in xrange( nSteps )]


        return [volume, cashflow, self.CONTRACT_PRICE.tolist()] 


    def get_mup_results(self, accountingPeriod=True):
        """
        @param accountingPeriod: flag indicating whether
            accounting period make-up results (accountingPeriod == True), or
            dispatch period make-up results (accountingPeriod == False)
            shall be returned
        @type accountingPeriod: L{bool}
         
        @return: LP decision variable values and
            coefficient data relating to make-up
        @rtype: L{list} [of L{list}s [of ...]]
        """
        result = None
        if accountingPeriod:
            nPeriods = len( self.acc_period_tuple_list )
            mup_accounting_period_vol_bal = [0.0]*nPeriods
            mup_accounting_period_vol_chg = [0.0]*nPeriods
            mup_accounting_period_avg_prc = [0.0]*nPeriods
            if self.HAS_MUP:
    
                mup_accounting_period_vol_bal = [self.mup_period_vol_bal[k].varValue for k in xrange( nPeriods )]
                mup_accounting_period_vol_chg = [self.mup_period_vol_chg[k].varValue for k in xrange( nPeriods )]
                mup_accounting_period_avg_prc = self.get_average_contract_price_list( accountingPeriod )
            
            result = [mup_accounting_period_vol_bal,
                      mup_accounting_period_vol_chg,
                      mup_accounting_period_avg_prc]
            
        else:
            nSteps = len( self.DISPATCH_PERIOD )
            mup_dispatch_period_vol_dec = [0.0]*nSteps
            mup_dispatch_period_avg_prc = [0.0]*nSteps
            mup_dispatch_period_vol_cfl = [0.0]*nSteps
            if self.HAS_MUP:
                mup_dispatch_period_vol_dec = [-self.SB*self.mup_vol[t].varValue for t in xrange( nSteps )]
                mup_dispatch_period_avg_prc = self.get_average_contract_price_list( accountingPeriod ) 
                mup_dispatch_period_vol_cfl = [-mup_dispatch_period_vol_dec[t]*mup_dispatch_period_avg_prc[t] for t in xrange( nSteps )]
                
            result = [mup_dispatch_period_vol_dec,
                      mup_dispatch_period_vol_cfl,
                      mup_dispatch_period_avg_prc]
        
        return result


    def get_cfw_results(self):
        """
        @return: LP decision variable values and
            coefficient data relating to carry forward
        @rtype: L{list} [of L{list}s [of ...]]
        """
        nPeriods = len( self.acc_period_tuple_list )
        cfw_accounting_period_vol_bal = [0.0]*nPeriods
        cfw_accounting_period_vol_chg = [0.0]*nPeriods
        if self.HAS_CFW:

            cfw_accounting_period_vol_bal = [self.cfw_period_vol_bal[k].varValue for k in xrange( nPeriods )]
            cfw_accounting_period_vol_chg = [self.cfw_period_vol_chg[k].varValue for k in xrange( nPeriods )]
            
        return [cfw_accounting_period_vol_bal,
                cfw_accounting_period_vol_chg]


    def get_mark_to_market_value(self):
        """
        Returns affine expression function representing
        the mark to market value corresponding to the
        objective value but using mid prices.
        
        @return: mark to market value function.
        @rtype: L{pulp.LpAffineExpression}
        """
        mtm = super( Supplier, self ).get_mark_to_market_value()

        mtm += self.get_std_mark_to_market_value()
        mtm += self.get_mup_mark_to_market_value()
        
        return mtm


    def get_std_mark_to_market_value(self):
        """
        standard contract price components to objective function
        """
        nSteps = len( self.DISPATCH_PERIOD )
        return pulp.LpAffineExpression( self.SB*pulp.lpSum( [self.vol[t]*self.CONTRACT_PRICE[t]*self.DISCOUNT_FACTOR[t] for t in xrange( nSteps )] ) )
        

    def get_mup_mark_to_market_value(self):
        mtm = pulp.LpAffineExpression( 0 )
        
        if self.HAS_MUP:
            nPeriods = len( self.acc_period_tuple_list )
            for k in xrange( nPeriods ):
                period_tuple = self.acc_period_tuple_list[k]
                START = period_tuple[0]
                FINAL = period_tuple[1]
                
                dispatchPeriodIdx = xrange( START, FINAL + 1 )
                
                AVG_CONTRACT_PRICE = self.get_average_contract_price( k )
                
                mtm += pulp.LpAffineExpression( self.SB*self.mup_period_vol_inc[k]*self.MUP_CREATE_PRICE_RATE*AVG_CONTRACT_PRICE*self.DISCOUNT_FACTOR[FINAL] )
                mtm += pulp.LpAffineExpression( self.SB*self.mup_period_vol_dec[k]*self.MUP_USEUP_PRICE_RATE *AVG_CONTRACT_PRICE*self.DISCOUNT_FACTOR[FINAL] )
                mtm += pulp.LpAffineExpression( -self.SB*pulp.lpSum( [self.mup_vol[t]*self.CONTRACT_PRICE[t]*self.DISCOUNT_FACTOR[t] for t in dispatchPeriodIdx] ) )
                
        return mtm


    def get_average_contract_price(self, k):
        """
        @param k: index into
            L{gnw.supplier.Supplier.acc_period_tuple_list} list.
        @type k: L{int}
         
        @return: average contract price for k-th accounting period
            either calculated on the fly from current contract price
            curve L{gnw.supplier.Supplier.CONTRACT_PRICE} or determined
            from L{gnw.supplier.Supplier.ACC_AVG_CONTRACT_PRICE} member.
        @rtype: L{float}
        """
        AVG_CONTRACT_PRICE = 0.0

        if self.ACC_AVG_CONTRACT_PRICE is not None \
        and len( self.ACC_AVG_CONTRACT_PRICE ) > k \
        and isnumeric( self.ACC_AVG_CONTRACT_PRICE[k] ):
            # use input value
            AVG_CONTRACT_PRICE = self.ACC_AVG_CONTRACT_PRICE[k]
        else:
            AVG_CONTRACT_PRICE = self.calc_average_contract_price( k )

        return AVG_CONTRACT_PRICE


    def calc_average_contract_price(self, k):
        """
        @param k: index into
            L{gnw.supplier.Supplier.acc_period_tuple_list} list.
        @type k: L{int}
         
        @return: average contract price for k-th accounting period
            calculated on the fly from current contract price
            curve L{gnw.supplier.Supplier.CONTRACT_PRICE}
        @rtype: L{float}
        """
        AVG_CONTRACT_PRICE = 0.0

        # calc from contract price curve
        period_tuple = self.acc_period_tuple_list[k]
        START = period_tuple[0]
        FINAL = period_tuple[1]

        dispatchPeriodIdx = xrange( START, FINAL + 1 )

        # dispatch period weighted average contract price
        # if DISPATCH_PERIOD represents a uniform list of periods
        # then this is just the arithmetic average.
        # Possible would as well be (additionally) a discount factor
        # weighted average.
        if dispatchPeriodIdx: 
            AVG_CONTRACT_PRICE = sum( [self.CONTRACT_PRICE[t]*self.DISPATCH_PERIOD[t] for t in dispatchPeriodIdx] )
            AVG_CONTRACT_PRICE /= sum( [self.DISPATCH_PERIOD[t] for t in dispatchPeriodIdx] )

        return AVG_CONTRACT_PRICE


    def get_average_contract_price_list(self, accountingPeriod=True):
        """ Returns a list of size len( self.acc_period_tuple_list )
        of prices corresponding to the average contract prices over
        given accounting periods (if accountingPeriod=True) or 
        a list of size len( self.DISPATCH_PERIOD )
        of prices corresponding to the average contract price
        over accounting periods, such that value for dispatch
        period t is equal to average contract price over
        accounting period k if t falls into accounting period k.
        
        @param accountingPeriod: whether returned list corresponds to
            number of accounting periods or to number of dispatch
            periods
        @type accountingPeriod: L{bool}
        
        @return: list of average contract prices corresponding
            to accounting periods
        @rtype: L{list} of L{float} of size len( self.acc_period_tuple_list )
            or len( self.DISPATCH_PERIOD )
        """ 
        if accountingPeriod:
            nPeriods = len( self.acc_period_tuple_list )
            AVG_CONTRACT_PRICE_LIST = [self.get_average_contract_price( k ) for k in xrange( nPeriods )]
        else:
            nSteps = len( self.DISPATCH_PERIOD )
            AVG_CONTRACT_PRICE_LIST = [0.0]*nSteps
            for t in xrange( nSteps ):
                for k in xrange( len( self.acc_period_tuple_list ) ):
                    if self.acc_period_tuple_list[k][0] <= t and t <= self.acc_period_tuple_list[k][1]: 
                        AVG_CONTRACT_PRICE_LIST[t] = self.get_average_contract_price( k )
                        break 
        return AVG_CONTRACT_PRICE_LIST



if __name__ == "__main__":
    print "gnw.supplier.py"

# ==============================================================================
#
#   Revision Control:
#
#   $Revision:: 4301                    $   Revision of last commit
#   $Author:: re04179                   $   Author of last commit
#   $Date:: 2009-11-23 14:04:46 +0100 (#$   Date of last commit
#
# ==============================================================================
