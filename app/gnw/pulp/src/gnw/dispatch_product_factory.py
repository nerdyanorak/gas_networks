# ==============================================================================
#
#   package         :   GasNetWorks (gnw) Python/pulp fuelled LP/MIP modeller 
#   author          :   Marc Roth (re04179)
#   version         :   $Id: dispatch_product_factory.py 2397 2009-10-11 15:23:59Z re04179 $
#   heading         :   $HeadURL: http://subversion.rwe.com/svn/s_and_v_projects/GasNetworks/trunk/app/gnw/pulp/src/gnw/dispatch_product_factory.py $
#
#   Description     :   COM interface sub-package
#
#   Creation Date   :   13Aug2009
#
#   Copyright       :   RWE Supply and Trading GmbH
#
# ==============================================================================
"""
gnw: provides factory for L{gnw.dispatch_product.DispatchProduct} objects
"""
from gnw.dispatch_product import DispatchProduct


class DispatchProductFactory( object ):
    """
    """
    def Create(dsp_dict={}, discount_factor=None, dispatch_period=None):
        """
        Creates a L{gnw.dispatch_product.DispatchProduct} instance
        from given inputs.
        
        @param dsp_dict: holds information to instantiate
            and initialise a L{gnw.dispatch_product.DispatchProduct}
            object instance.
            Mandatory entries are:
                - 'NAME' : unique entity identifier
                - 'SB' : sell/buy factor (sell = 1, buy = -1)
                - 'PRICE_CURVE' : bid (sell) or asking (buy) price
                    depending on value of 'SB'
                - 'MID_PRICE_CURVE': corresponding mid price
            Optional entries are:
                - 'CURRENT_POS_CURVE' : current position. Can be a single
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
        
        @return: reference to L{gnw.dispatch_product.DispatchProduct} instance 
        """
        # mandatory inputs/dictionary elements
        if 'NAME' not in dsp_dict:
            raise ValueError, "'NAME' not found in dispatch product dictionary"

        if 'SB' not in dsp_dict:
            raise ValueError, "'SB' not found in dispatch product dictionary"

        if 'PRICE_CURVE' not in dsp_dict:
            raise ValueError, "'PRICE_CURVE' not found in dispatch product dictionary"

        if 'MID_PRICE_CURVE' not in dsp_dict:
            raise ValueError, "'MID_PRICE_CURVE' not found in dispatch product dictionary"

        # optional inputs/dictionary elements
        CURRENT_POS_CURVE = None
        if 'CURRENT_POS_CURVE' in dsp_dict:
            CURRENT_POS_CURVE = dsp_dict['CURRENT_POS_CURVE']

        DISCOUNT_FACTOR = None
        if discount_factor is not None:
            DISCOUNT_FACTOR = discount_factor
        if 'DISCOUNT_FACTOR' in dsp_dict and dsp_dict['DISCOUNT_FACTOR'] is not None:
            DISCOUNT_FACTOR = dsp_dict['DISCOUNT_FACTOR']
            
         
        return DispatchProduct( name = dsp_dict['NAME'],
                                sellbuy = dsp_dict['SB'],
                                price = dsp_dict['PRICE_CURVE'],
                                midPrice = dsp_dict['MID_PRICE_CURVE'],
                                currentPosition = CURRENT_POS_CURVE,
                                discountFactor = DISCOUNT_FACTOR,
                                dispatchPeriod = dispatch_period )

    Create = staticmethod( Create )



if __name__ == "__main__" :
    print "gnw.dispatch_product_factory.py"

# ==============================================================================
#
#   Revision Control:
#
#   $Revision:: 2397                    $   Revision of last commit
#   $Author:: re04179                   $   Author of last commit
#   $Date:: 2009-10-11 17:23:59 +0200 (#$   Date of last commit
#
# ==============================================================================
