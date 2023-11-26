# ==============================================================================
#
#   package         :   GasNetWorks (gnw) Python/pulp fuelled LP/MIP modeller 
#   author          :   Marc Roth (re04179)
#   version         :   $Id: supplier_factory.py 2394 2009-10-11 15:15:07Z re04179 $
#   heading         :   $HeadURL: http://subversion.rwe.com/svn/s_and_v_projects/GasNetworks/trunk/app/gnw/pulp/src/gnw/supplier_factory.py $
#
#   Description     :   COM interface sub-package
#
#   Creation Date   :   13Aug2009
#
#   Copyright       :   RWE Supply and Trading GmbH
#
# ==============================================================================
"""
gnw: provides factory for L{gnw.supplier.Supplier} objects
"""
from gnw.supplier import Supplier
from gnw.util import conditional

class SupplierFactory( object ):
    """
    """
    def Create(splr_dict={}, discount_factor=None, dispatch_period=None):
        """
        Creates a L{gnw.supplier.Supplier} instance
        from given inputs.
        
        @param splr_dict: holds information to instantiate
            and initialise a L{gnw.supplier.Supplier}
            object instance.
            Mandatory entries are:
                - 'NAME' : unique entity identifier
                - 'SB' : sell/buy factor (sell = 1, buy = -1)
                - 'CONSTRAINT_COEFF' : is a list (of arbitrary length)
                    of [L{int}, L{int}, L{float}, L{int}, L{int}] representing
                    start and end index into dispatch period sequence, respectively,
                    bound coefficient, boundary type and constraint type mask,
                    where
                        - boundary type is equal to
                            L{gnw.constraint.ConstraintCoeff.BoundaryType.LB} or
                            L{gnw.constraint.ConstraintCoeff.BoundaryType.UB} or
                            L{gnw.constraint.ConstraintCoeff.BoundaryType.EQ}
                        - constraint type is equal to a combination of flags
                            as set in L{gnw.supplier.Supplier.constraintTypeMask}
                - 'CONTRACT_PRICE_CURVE' : is a an sequence type of
                    length len(DISPATCH_PERIOD) holding elements of type L{float}
                    representing the contract price for volumes dispatched
                    during given dispatch periods.
            Optional entries are:
                - 'ACQ' : single numeric value representing the nominal
                    annual contract quantity. Defaults to 1.0
                - 'HAS_MAKEUP' : flag indicating whether contract
                    uses make-up features. Defaults to False
                - 'HAS_MAKEUP_EXPIRY' : flag indicating whether make-up
                    feature uses expiring make-up volume feature. Only
                    effective if 'HAS_MAKEUP' is set to True. Defaults to False 
                - 'MAKEUP_NUM_EXPIRY_PERIODS' : single integer value giving the
                    number of accounting periods after which a make-up volumes
                    expire. Only effective if 'HAS_MAKEUP' and 'HAS_MAKEUP_EXPIRY'
                    are set to True. Defaults to 1
                - 'MAKEUP_CREATE_PRICE_RATE' : the rate at which make-up gas
                    is priced if created. Only effective if 'HAS_MAKEUP' is
                    set to True. Defaults to 1.0
                - 'MAKEUP_USEUP_PRICE_RATE' : the rate at which make-up gas
                    is priced if used up. Only effecitve is 'HAS_MAKEUP' is
                    set to True. Defaults to 0.0
                - 'MAKEUP_INITIAL_BALANCE' : make-up initial balance is a single
                    numeric value if 'HAS_MAKEUP_EXPIRY' is set to False and
                    a sequence type of length 'NUM_MAKEUP_EXPIRY_PERIODS' of
                    numeric elements, otherwise. Only effective if 'HAS_MAKEUP'
                    is set to True. Defaults to (a sequence of) 0.0
                - 'HAS_CARRYFORWARD' : flag indicating whether contract
                    uses carry forward features. Defaults to False
                - 'HAS_CARRYFORWARD_EXPIRY' : flag indicating whether carry
                    forward feature uses expiring carry forward volume feature.
                    Only effective if 'HAS_CARRYFORWARD' is set to True.
                    Defaults to False 
                - 'CARRYFORWARD_NUM_EXPIRY_PERIODS' : single integer value giving the
                    number of accounting periods after which a carry forward volumes
                    expire. Only effective if 'HAS_CARRYFORWARD' and
                    'HAS_CARRYFORWARD_EXPIRY' are set to True. Defaults to 1
                - 'CARRYFORWARD_INITIAL_BALANCE' : carry forward initial balance is
                    a single numeric value if 'HAS_CARRYFORWARD_EXPIRY' is set to False
                    and a sequence type of length 'NUM_CARRYFORWARD_EXPIRY_PERIODS' of
                    numeric elements, otherwise. Only effective if 'HAS_CARRYFORWARD'
                    is set to True. Defaults to (a sequence of) 0.0
                - 'ACC_PERIOD_AVG_CONTRACT_PRICE' : None, sequence type holding
                    average contract price(s) for the accounting periods.
                - 'HAS_IAS39' : flag indicating whether IAS39 features are 
                    in effect. Defaults to False
                - 'DISCOUNT_FACTOR' : discount factor(s) applicable to
                    cash flows from dispatch volumes during dispatch periods.
                    Defaults to discount_factor if not none, to 1.0 otherwise
                
        @param discount_factor: discount factor(s) applicable to
            cash flows from position for each dispatch period
        @type discount_factor: None, numeric value or sequence type
            of length len( dispatch_period ) of numeric types.
            
        @param dispatch_period: sequence type of numeric values defining
            the number of dispatch periods ( = len( dispatch_period ) ) and
            the duration of each dispatch period (hours). The dispatch
            periods need not be uniform.
        @type dispatch_period: sequence type of positive numeric values
        
        @return: reference to L{gnw.supplier.Supplier} instance 
        """
        # mandatory inputs/dictionary items
        if 'NAME' not in splr_dict:
            raise ValueError, "'NAME' not found in supplier dictionary"
        
        if 'SB' not in splr_dict:
            raise ValueError, "'SB' not found in supplier dictionary"
        
        if 'CONSTRAINT_COEFF' not in splr_dict:
            raise ValueError, "'CONSTRAINT_COEFF' not found in supplier dictionary"
        
        if 'CONTRACT_PRICE_CURVE' not in splr_dict:
            raise ValueError, "'CONTRACT_PRICE_CURVE' not found in supplier dictionary"

        # optional inputs/dictionary items
        ACQ = None
        if 'ACQ' in splr_dict:
            ACQ =  splr_dict['ACQ']

        HAS_MAKEUP = None
        if 'HAS_MAKEUP' in splr_dict:
            HAS_MAKEUP = splr_dict['HAS_MAKEUP']

        HAS_MAKEUP_EXPIRY = None 
        if 'HAS_MAKEUP_EXPIRY' in splr_dict:
            HAS_MAKEUP_EXPIRY = splr_dict['HAS_MAKEUP_EXPIRY']
        
        MAKEUP_NUM_EXPIRY_PERIODS = conditional( HAS_MAKEUP_EXPIRY, 1, 0 )
        if 'MAKEUP_NUM_EXPIRY_PERIODS' in splr_dict:
            MAKEUP_NUM_EXPIRY_PERIODS = splr_dict['MAKEUP_NUM_EXPIRY_PERIODS']
        
        MAKEUP_CREATE_PRICE_RATE = None
        if 'MAKEUP_CREATE_PRICE_RATE' in splr_dict:
            MAKEUP_CREATE_PRICE_RATE = splr_dict['MAKEUP_CREATE_PRICE_RATE']
        
        MAKEUP_USEUP_PRICE_RATE = None
        if 'MAKEUP_USEUP_PRICE_RATE' in splr_dict:
            MAKEUP_USEUP_PRICE_RATE = splr_dict['MAKEUP_USEUP_PRICE_RATE']
        
        MAKEUP_INITIAL_BALANCE = conditional( HAS_MAKEUP_EXPIRY, [0.0]*MAKEUP_NUM_EXPIRY_PERIODS, 0.0 )
        if 'MAKEUP_INITIAL_BALANCE' in splr_dict:
            MAKEUP_INITIAL_BALANCE = splr_dict['MAKEUP_INITIAL_BALANCE']
        
        HAS_CARRYFORWARD = None
        if 'HAS_CARRYFORWARD' in splr_dict:
            HAS_CARRYFORWARD = splr_dict['HAS_CARRYFORWARD']
        
        HAS_CARRYFORWARD_EXPIRY = None
        if 'HAS_CARRYFORWARD_EXPIRY' in splr_dict:
            HAS_CARRYFORWARD_EXPIRY = splr_dict['HAS_CARRYFORWARD_EXPIRY']
        
        CARRYFORWARD_NUM_EXPIRY_PERIODS = conditional( HAS_CARRYFORWARD_EXPIRY, 1, 0 )
        if 'CARRYFORWARD_NUM_EXPIRY_PERIODS' in splr_dict:
            CARRYFORWARD_NUM_EXPIRY_PERIODS = splr_dict['CARRYFORWARD_NUM_EXPIRY_PERIODS']
        
        CARRYFORWARD_INITIAL_BALANCE = conditional( HAS_CARRYFORWARD_EXPIRY, [0.0]*CARRYFORWARD_NUM_EXPIRY_PERIODS, 0.0 )
        if 'CARRYFORWARD_INITIAL_BALANCE' in splr_dict:
            CARRYFORWARD_INITIAL_BALANCE = splr_dict['CARRYFORWARD_INITIAL_BALANCE']
            
        ACC_PERIOD_AVG_CONTRACT_PRICE = None
        if 'ACC_PERIOD_AVG_CONTRACT_PRICE' in splr_dict:
            ACC_PERIOD_AVG_CONTRACT_PRICE = splr_dict['ACC_PERIOD_AVG_CONTRACT_PRICE']
        
        HAS_IAS39 = None
        if 'HAS_IAS39' in splr_dict:
            HAS_IAS39 = splr_dict['HAS_IAS39']
        
        DISCOUNT_FACTOR = None
        if discount_factor is not None:
            DISCOUNT_FACTOR = discount_factor
        if 'DISCOUNT_FACTOR' in splr_dict and splr_dict['DISCOUNT_FACTOR'] is not None:
            DISCOUNT_FACTOR = splr_dict['DISCOUNT_FACTOR']

         
        return Supplier( name = splr_dict['NAME'],
                         sellbuy = splr_dict['SB'],
                         acq = ACQ,
                         hasMakeUp = HAS_MAKEUP,
                         hasMakeUpExpiry = HAS_MAKEUP_EXPIRY,
                         makeUpNumExpiryPeriods = MAKEUP_NUM_EXPIRY_PERIODS,
                         makeUpCreatePriceRate = MAKEUP_CREATE_PRICE_RATE,
                         makeUpUseupPriceRate = MAKEUP_USEUP_PRICE_RATE,
                         makeUpInitialBalance = MAKEUP_INITIAL_BALANCE,
                         hasCarryForward = HAS_CARRYFORWARD,
                         hasCarryForwardExpiry = HAS_CARRYFORWARD_EXPIRY,
                         carryForwardNumExpiryPeriods = CARRYFORWARD_NUM_EXPIRY_PERIODS,
                         carryForwardInitialBalance = CARRYFORWARD_INITIAL_BALANCE,
                         accPeriodAvgContractPrice = ACC_PERIOD_AVG_CONTRACT_PRICE,
                         hasIAS39 = HAS_IAS39,
                         constraintCoeff = splr_dict['CONSTRAINT_COEFF'],
                         contractPrice = splr_dict['CONTRACT_PRICE_CURVE'],
                         discountFactor = DISCOUNT_FACTOR,
                         dispatchPeriod = dispatch_period )

    Create = staticmethod( Create )



if __name__ == "__main__" :
    print "gnw.supplier_factory.py"
    
# ==============================================================================
#
#   Revision Control:
#
#   $Revision:: 2394                    $   Revision of last commit
#   $Author:: re04179                   $   Author of last commit
#   $Date:: 2009-10-11 17:15:07 +0200 (#$   Date of last commit
#
# ==============================================================================
