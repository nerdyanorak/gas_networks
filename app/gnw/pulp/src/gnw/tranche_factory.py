# ==============================================================================
#
#   package         :   GasNetWorks (gnw) Python/pulp fuelled LP/MIP modeller 
#   author          :   Marc Roth (re04179)
#   version         :   $Id: tranche_factory.py 2138 2009-09-22 12:02:19Z re04179 $
#   heading         :   $HeadURL: http://subversion.rwe.com/svn/s_and_v_projects/GasNetworks/trunk/app/gnw/pulp/src/gnw/tranche_factory.py $
#
#   Description     :   COM interface sub-package
#
#   Creation Date   :   13Aug2009
#
#   Copyright       :   RWE Supply and Trading GmbH
#
# ==============================================================================
"""
gwn: provides factory for L{gnw.tranche.Tranche} objects
"""
from gnw.tranche import Tranche

class TrancheFactory( object ):
    """
    """
    def Create(trn_dict={}, discount_factor=None, dispatch_period=None):
        """
        Creates a L{gnw.tranche.Tranche} instance
        from given inputs.
    
        @param trn_dict: holds information to instantiate
            and initialise a L{gnw.tranche.Tranche}
            object instance.
            Mandatory entries are:
                - 'NAME' : unique entity identifier
                - 'SB' : sell/buy factor (sell = 1, buy = -1)
                - 'BID_ASK_ADJ' : bid to mid (if 'SB' = 1) or
                    mid to ask (if 'SB' = -1) price adjustment
                - 'START_IDX' : index into dispatch period sequence
                - 'END_IDX' : index into dispatch period sequence
            Optional entries are:
                - 'TRADE_SIZE_MIN' : if not None and different
                    from 0 triggers min trade size constraints
                - 'TRADE_SIZE_MAX' : if not None
                    triggers max trade size constraints
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
        
        @return: reference to L{gnw.tranche.Tranche} instance 
        """
        # mandatory inputs/dictionary items
        if 'NAME' not in trn_dict:
            raise ValueError, "'NAME' not found in tranche dictionary"
        
        if 'SB' not in trn_dict:
            raise ValueError, "'SB' not found in tranche dictionary"

        if 'BID_ASK_ADJ' not in trn_dict:
            raise ValueError, "'BID_ASK_ADJ' not found in tranche dictionary"

        if 'START_IDX' not in trn_dict:
            raise ValueError, "'START_IDX' not found in tranche dictionary"

        if 'END_IDX' not in trn_dict:
            raise ValueError, "'END_IDX' not found in tranche dictionary"

        # optional inputs/dictionary items
        TRADE_SIZE_MIN = None
        if 'TRADE_SIZE_MIN' in trn_dict:
            TRADE_SIZE_MIN = trn_dict['TRADE_SIZE_MIN']
        TRADE_SIZE_MAX = None
        if 'TRADE_SIZE_MAX' in trn_dict:
            TRADE_SIZE_MAX = trn_dict['TRADE_SIZE_MAX'] 
        
        DISCOUNT_FACTOR = None
        if discount_factor is not None:
            DISCOUNT_FACTOR = discount_factor
        if 'DISCOUNT_FACTOR' in trn_dict and trn_dict['DISCOUNT_FACTOR'] is not None:
            DISCOUNT_FACTOR = trn_dict['DISCOUNT_FACTOR']
        
         
        return Tranche( name = trn_dict['NAME'],
                        sellbuy = trn_dict['SB'],
                        bidAskAdj = trn_dict['BID_ASK_ADJ'],
                        deliveryPeriod = (trn_dict['START_IDX'], trn_dict['END_IDX']),
                        capacityLimit = (TRADE_SIZE_MIN, TRADE_SIZE_MAX),
                        discountFactor = DISCOUNT_FACTOR,
                        dispatchPeriod = dispatch_period) 

    Create = staticmethod( Create )



if __name__ == "__main__" :
    print "gnw.tranche_factory.py"
    
# ==============================================================================
#
#   Revision Control:
#
#   $Revision:: 2138                    $   Revision of last commit
#   $Author:: re04179                   $   Author of last commit
#   $Date:: 2009-09-22 14:02:19 +0200 (#$   Date of last commit
#
# ==============================================================================
