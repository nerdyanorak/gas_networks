# ==============================================================================
#
#   package         :   GasNetWorks (gnw) Python/pulp fuelled LP/MIP modeller 
#   author          :   Marc Roth (re04179)
#   version         :   $Id: storage_factory.py 2138 2009-09-22 12:02:19Z re04179 $
#   heading         :   $HeadURL: http://subversion.rwe.com/svn/s_and_v_projects/GasNetworks/trunk/app/gnw/pulp/src/gnw/storage_factory.py $
#
#   Description     :   COM interface sub-package
#
#   Creation Date   :   13Aug2009
#
#   Copyright       :   RWE Supply and Trading GmbH
#
# ==============================================================================
"""
gnw: provides factory for L{gnw.storage.Storage} objects
"""
from gnw.storage import Storage, LevDepDispatchCurve

class StorageFactory( object ):
    """
    """
    def Create(strg_dict={}, discount_factor=None, dispatch_period=None):
        """
        Creates a L{gnw.storage.Storage} instance
        from given inputs.
        
        @param strg_dict: holds information to instantiate
            and initialise a L{gnw.storage.Storage}
            object instance.
            Mandatory entries are:
                - 'NAME' : unique entity identifier
                - 'SB' : sell/buy factor (sell = 1, buy = -1)
            Optional entries are:
                - 'CURRENT_POS' : current position. Can be a single
                    numeric value (for a uniform position across
                    all dispatch periods) or a sequence type
                    of numeric values of length len( dispatch_period ).
                    If missing a flat position for all dispatch periods
                    is assumed.
                    If we buy (SB = -1) the dispatch product then we are
                    long a basket of {CURRENT_POS[t], t in range( len( dispatch_period ) )},
                    i.e., we are long CURRENT_POS[t], if CURRENT_POS[t] > 0,
                    short otherwise.
                    If we sell (SB = 1) the dispatch product then we are
                    short a basket of of {CURRENT_POS[t], t in range( len( dispatch_period ) )},
                    i.e., we are short CURRENT_POS[t], if CURRENT_POS[t] > 0,
                    long otherwise.
                - 'HAS_LEV_DEP_INJ_CAP_CURVE' : flags whether to use level
                    dependent injection rate curves (default False)
                - 'HAS_LEV_DEP_REL_CAP_CURVE' : flags whether to use level
                    dependent release rate curves (default False)
                - 'LEV_DEP_INJ_CAP_CURVE' : mandatory if 'HAS_LEV_DEP_INJ_CAP_CURVE'
                    is set to True
                - 'LEV_DEP_REL_CAP_CURVE' : mandatory if 'HAS_LEV_DEP_REL_CAP_CURVE'
                    is set to True
                - 'MIN_LEV_PCT' : minimum storage level percentage
                    (relative to working gas volume (WGV)). If given
                    it is a list (typically of length len(dispatch_period) + 1)
                    of [L{int}, L{int}, L{float}, L{int}, L{int}] representing
                    start and end index into dispatch period sequence, respectively,
                    bound coefficient, boundary type and constraint type mask,
                    where
                        - start index is equal end index,
                        - boundary type is equal to
                            L{gnw.constraint.ConstraintCoeff.BoundaryType.LB}
                        - constraint type is equal to
                            L{gnw.constraint.ConstraintCoeff.ConstraintType.LEV_PCT}
                - 'MAX_LEV_PCT' : maximum storage level percentage
                    (relative to working gas volume (WGV)). If given
                    it is a list (typically of  length len(dispatch_period) + 1)
                    of [L{int}, L{int}, L{float}, L{int}, L{int}] representing
                    start and end index into dispatch period sequence, respectively,
                    bound coefficient, boundary type and constraint type mask,
                    where
                        - start index is equal end index,
                        - boundary type is equal to
                            L{gnw.constraint.ConstraintCoeff.BoundaryType.UB}
                        - constraint type is equal to
                            L{gnw.constraint.ConstraintCoeff.ConstraintType.LEV_PCT}
                - 'MAX_INJ_CAP_PCT' : maximum injection capacity percentage
                    (relative to injection capacity (INJ_CAP)). If given
                    it is list (typically of length len(dispatch_period))
                    of [L{int}, L{int}, L{float}, L{int}, L{int}] representing
                    start and end index into dispatch period sequence, respectively,
                    bound coefficient, boundary type and constraint type mask,
                    where
                        - start index is equal end index,
                        - boundary type is equal to
                            L{gnw.constraint.ConstraintCoeff.BoundaryType.UB}
                        - constraint type is equal to
                            L{gnw.constraint.ConstraintCoeff.ConstraintType.INJ_CAP_PCT}
                - 'MAX_REL_CAP_PCT' : maximum release capacity percentage
                    (relative to release capacity (REL_CAP)). If given
                    it is a list (typically of length len(dispatch_period))
                    of [L{int}, L{int}, L{float}, L{int}, L{int}] representing
                    start and end index into dispatch period sequence, respectively,
                    bound coefficient, boundary type and constraint type mask. 
                    where
                        - start index is equal end index,
                        - boundary type is equal to
                            L{gnw.constraint.ConstraintCoeff.BoundaryType.UB}
                        - constraint type is equal to
                            L{gnw.constraint.ConstraintCoeff.ConstraintType.REL_CAP_PCT}
                - 'CONSTRAINT_COEFF' : is a list (of arbitrary length)
                    of [L{int}, L{int}, L{float}, L{int}, L{int}] representing
                    start and end index into dispatch period sequence, respectively,
                    bound coefficient, boundary type and constraint type mask,
                    where
                        - boundary type is equal to
                            L{gnw.constraint.ConstraintCoeff.BoundaryType.LB} or
                            L{gnw.constraint.ConstraintCoeff.BoundaryType.UB}
                        - constraint type is equal to
                            L{gnw.constraint.ConstraintCoeff.ConstraintType.INJ_VOL_PCT} or
                            L{gnw.constraint.ConstraintCoeff.ConstraintType.REL_VOL_PCT}
                - INJ_CAP : single numeric value, defaults to 1.0
                - REL_CAP : single numeric value, defaults to 1.0 
                - WGV : single numeric value, defaults to 1.0
                - START_LEV_PCT : single numeric value, defaults to 1.0
                - END_LEV_PCT : single numeric value, defaults to 1.0
                - STRICT_END_LEV : flag, defaults to False. If True END_LEV_PCT 
                    must be reached, any level above END_LEV_PCT otherwise.
                - INJ_COST : if not None it is a single numeric value or
                    a sequence of length len(DISPATCH_PERIOD) representing
                    the cost of storage injection in [EUR/MWh]. Defaults to 0.0
                - REL_COST : if not None it is a single numeric value or
                    a sequence of length len(DISPATCH_PERIOD) representing
                    the cost of storage release in [EUR/MWh]. Defaults to 0.0
                - 'DISCOUNT_FACTOR' : discount factor(s) applicable to
                    cash flows from dispatch volumes during dispatch periods.
                    Defaults to discount_factor if not none, to 1.0 otherwise
        @todo: merge all above list of lists (MIN_LEV_PCT, MAX_LEV_PCT, MAX_INJ_CAP_PCT,
            MAX_REL_CAP_PCT and CONSTRAINT_COEFF) into 'CONSTRAINT_COEFF' on input
            as they are in separate inputs only for historic reasons but and are
            internally anyway merged before passed to the Storage.__init__ method). 
        
        @param discount_factor: discount factor(s) applicable to
            cash flows from position for each dispatch period
        @type discount_factor: None, numeric value or sequence type
            of length len( dispatch_period ) of numeric types.
            
        @param dispatch_period: sequence type of numeric values defining
            the number of dispatch periods ( = len( dispatch_period ) ) and
            the duration of each dispatch period (hours). The dispatch
            periods need not be uniform.
        @type dispatch_period: sequence type of positive numeric values
        
        @return: reference to L{gnw.storage.Storage} instance 
        """
        # mandatory inputs/dictionary items
        if 'NAME' not in strg_dict:
            raise ValueError, "'NAME' not found in storage dictionary"
        
        if 'SB' not in strg_dict:
            raise ValueError, "'SB' not found in storage dictionary"
        
        # optional inputs/dictionary items
        has_lev_dep_inj_cap = False
        if 'HAS_LEV_DEP_INJ_CAP_CURVE' in strg_dict:
            has_lev_dep_inj_cap = strg_dict['HAS_LEV_DEP_INJ_CAP_CURVE']
             
        lev_dep_inj_cap = None
        if has_lev_dep_inj_cap:
            if 'LEV_DEP_INJ_CAP_CURVE' not in strg_dict:
                raise ValueError, "'HAS_LEV_DEP_INJ_CAP' is set to 'True' but 'LEV_DEP_INJ_CAP_CURVE' not found in storage dictionary"
            
            inj_cap_data = strg_dict['LEV_DEP_INJ_CAP_CURVE']
            lev_dep_inj_cap = LevDepDispatchCurve( [inj_cap_data[i][0] for i in xrange( len( inj_cap_data ) )],
                                                   [inj_cap_data[i][1] for i in xrange( len( inj_cap_data ) )] )
        
        has_lev_dep_rel_cap = False
        if 'HAS_LEV_DEP_REL_CAP_CURVE' in strg_dict:
            has_lev_dep_rel_cap = strg_dict['HAS_LEV_DEP_REL_CAP_CURVE']
            
        lev_dep_rel_cap = None
        if has_lev_dep_rel_cap:
            if 'LEV_DEP_REL_CAP_CURVE' not in strg_dict:
                raise ValueError, "'HAS_LEV_DEP_REL_CAP' is set to 'True' but 'LEV_DEP_REL_CAP_CURVE' not found in storage dictionary"

            rel_cap_data = strg_dict['LEV_DEP_REL_CAP_CURVE']
            lev_dep_rel_cap = LevDepDispatchCurve( [rel_cap_data[i][0] for i in xrange( len( rel_cap_data ) )],
                                                   [rel_cap_data[i][1] for i in xrange( len( rel_cap_data ) )] )
        
        constraint_coeff_list = []
        if 'MIN_LEV_PCT' in strg_dict:
            constraint_coeff_list += strg_dict['MIN_LEV_PCT']
        if 'MAX_LEV_PCT' in strg_dict:
            constraint_coeff_list + strg_dict['MAX_LEV_PCT']
        if 'MAX_INJ_CAP_PCT' in strg_dict:
            constraint_coeff_list += strg_dict['MAX_INJ_CAP_PCT']
        if 'MAX_REL_CAP_PCT' in strg_dict:
            constraint_coeff_list += strg_dict['MAX_REL_CAP_PCT']
        if 'CONSTRAINT_COEFF' in strg_dict:
            constraint_coeff_list += strg_dict['CONSTRAINT_COEFF']

            
        INJ_CAP = None
        if 'INJ_CAP' in strg_dict:
            INJ_CAP = strg_dict['INJ_CAP']
            
        REL_CAP = None
        if 'REL_CAP' in strg_dict:
            REL_CAP = strg_dict['REL_CAP']
            
        WGV = None
        if 'WGV' in strg_dict:
            WGV = strg_dict['WGV']
        
        START_LEV_PCT = None
        if 'START_LEV_PCT' in strg_dict:
            START_LEV_PCT = strg_dict['START_LEV_PCT']
        
        END_LEV_PCT = None
        if 'END_LEV_PCT' in strg_dict:
            END_LEV_PCT = strg_dict['END_LEV_PCT']
            
        STRICT_END_LEV = None
        if 'STRICT_END_LEV' in strg_dict:
            STRICT_END_LEV = strg_dict['STRICT_END_LEV']
            
        INJ_COST = None
        if 'INJ_COST' in strg_dict:
            INJ_COST = strg_dict['INJ_COST']
            
        REL_COST = None
        if 'REL_COST' in strg_dict:
            INJ_COST = strg_dict['REL_COST']
        
        DISCOUNT_FACTOR = None
        if discount_factor is not None:
            DISCOUNT_FACTOR = discount_factor
        if 'DISCOUNT_FACTOR' in strg_dict and strg_dict['DISCOUNT_FACTOR'] is not None:
            DISCOUNT_FACTOR = strg_dict['DISCOUNT_FACTOR']
        
    
        return Storage( name = strg_dict['NAME'],
                        sellbuy = strg_dict['SB'],
                        injCap = INJ_CAP,
                        relCap = REL_CAP,
                        wgv = WGV,
                        startLevPct = START_LEV_PCT,
                        finalLevPct = END_LEV_PCT,
                        strictFinalLev = STRICT_END_LEV,
                        constraintCoeff = constraint_coeff_list,
                        injCost = INJ_COST,
                        relCost = REL_COST,
                        levDepInjCap = lev_dep_inj_cap,
                        levDepRelCap = lev_dep_rel_cap,
                        discountFactor = DISCOUNT_FACTOR,
                        dispatchPeriod = dispatch_period )

    Create = staticmethod( Create )



if __name__ == "__main__" :
    print "gnw.storage_factory.py"
    
# ==============================================================================
#
#   Revision Control:
#
#   $Revision:: 2138                    $   Revision of last commit
#   $Author:: re04179                   $   Author of last commit
#   $Date:: 2009-09-22 14:02:19 +0200 (#$   Date of last commit
#
# ==============================================================================
