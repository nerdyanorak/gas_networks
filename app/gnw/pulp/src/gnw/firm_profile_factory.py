# ==============================================================================
#
#   package         :   GasNetWorks (gnw) Python/pulp fuelled LP/MIP modeller 
#   author          :   Marc Roth (re04179)
#   version         :   $Id: firm_profile_factory.py 2397 2009-10-11 15:23:59Z re04179 $
#   heading         :   $HeadURL: http://subversion.rwe.com/svn/s_and_v_projects/GasNetworks/trunk/app/gnw/pulp/src/gnw/firm_profile_factory.py $
#
#   Description     :   COM interface sub-package
#
#   Creation Date   :   13Aug2009
#
#   Copyright       :   RWE Supply and Trading GmbH
#
# ==============================================================================
"""
gnw: provides factory for L{gnw.firm_profile.FirmProfile} objects
"""
from gnw.firm_profile import FirmProfile


class FirmProfileFactory( object ):
    """
    """
    def Create(frm_dict={}, discount_factor=None, dispatch_period=None):
        """
        Creates a L{gnw.firm_profile.FirmProfile} instance
        from given inputs.
    
        @param frm_dict: holds information to instantiate
            and initialise a L{gnw.firm_profile.FirmProfile}
            object instance.
            Mandatory entries are:
                - 'NAME' : unique entity identifier
                - 'SB' : sell/buy factor (sell = 1, buy = -1)
            Optional entries are:
                - 'CURRENT_POS_CURVE' : current position. Can be a single
                    numeric value (for a uniform position across
                    all dispatch periods) or a sequence type
                    of numeric values of length len( dispatch_period ).
                    If missing a flat position for all dispatch periods
                    is assumed.
                    If we buy (SB = -1) the firm profile then we are
                    long a basket of {CURRENT_POS[t], t in range( len( dispatch_period ) )},
                    i.e., we are long CURRENT_POS[t], if CURRENT_POS[t] > 0,
                    short otherwise.
                    If we sell (SB = 1) the firm profile then we are
                    short a basket of of {CURRENT_POS[t], t in range( len( dispatch_period ) )},
                    i.e., we are short CURRENT_POS[t], if CURRENT_POS[t] > 0,
                    long otherwise.
                - 'DISCOUNT_FACTOR' : discount factor(s) applicable to
                    cash flows from dispatch volumes during dispatch periods.
                    Defaults to discount_factor if not none, to 1.0 otherwise

        @param discount_factor: discount factor(s) applicable to
            cash flows from position for each dispatch period
        @type discount_factor: None, numeric value or sequence type
            of length len( dispatch_period ) of numeric types.
            
        @param dispatch_period: sequence type of numeric values defining
            the number of dispatch periods ( = len( dispatch_period) ) and
            the duration of each dispatch period (hours). The dispatch
            periods need not be uniform.
        @type dispatch_period: sequence type of positive numeric values
        
        @return: reference to L{gnw.firm_profile.FirmProfile} instance 
        """
        # mandatory inputs/dictionary elements
        if 'NAME' not in frm_dict:
            raise ValueError, "'NAME' not found in firm profile dictionary"
        
        if 'SB' not in frm_dict:
            raise ValueError, "'SB' not found in firm profile dictionary"
        
        # optional inputs/dictionary elements
        CURRENT_POS_CURVE = None
        if 'CURRENT_POS_CURVE' in frm_dict:
            CURRENT_POS_CURVE = frm_dict['CURRENT_POS_CURVE']
            
        DISCOUNT_FACTOR = None
        if discount_factor is not None:
            DISCOUNT_FACTOR = discount_factor
        if 'DISCOUNT_FACTOR' in frm_dict and frm_dict['DISCOUNT_FACTOR'] is not None:
            DISCOUNT_FACTOR = frm_dict['DISCOUNT_FACTOR']

        
        return FirmProfile( name = frm_dict['NAME'],
                            sellbuy = frm_dict['SB'],
                            currentPosition = CURRENT_POS_CURVE,
                            discountFactor = DISCOUNT_FACTOR,
                            dispatchPeriod = dispatch_period )
    
    Create = staticmethod( Create )
    


if __name__ == "__main__" :
    print "gnw.firm_profile_factory.py"

# ==============================================================================
#
#   Revision Control:
#
#   $Revision:: 2397                    $   Revision of last commit
#   $Author:: re04179                   $   Author of last commit
#   $Date:: 2009-10-11 17:23:59 +0200 (#$   Date of last commit
#
# ==============================================================================
