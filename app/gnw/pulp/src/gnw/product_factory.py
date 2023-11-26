# ==============================================================================
#
#   package         :   GasNetWorks (gnw) Python/pulp fuelled LP/MIP modeller 
#   author          :   Marc Roth (re04179)
#   version         :   $Id: product_factory.py 2138 2009-09-22 12:02:19Z re04179 $
#   heading         :   $HeadURL: http://subversion.rwe.com/svn/s_and_v_projects/GasNetworks/trunk/app/gnw/pulp/src/gnw/product_factory.py $
#
#   Description     :   COM interface sub-package
#
#   Creation Date   :   13Aug2009
#
#   Copyright       :   RWE Supply and Trading GmbH
#
# ==============================================================================
"""
gnw: provides factory for L{gnw.product.Product} objects
"""
from gnw.product import Product
from gnw.util import dbg_print

from gnw.tranche_factory import TrancheFactory


class ProductFactory( object ):
    """
    """
    def Create(prd_dict={}, entity_list=[], discount_factor=None, dispatch_period=None):
        """
        Creates a L{gnw.product.Product} instance
        from given inputs.
    
        @param prd_dict: holds information to instantiate
            and initialise a L{gnw.product.Product}
            object instance.
            Mandatory entries are:
                - 'NAME' : unique entity identifier
                - 'SB' : sell/buy factor (sell = 1, buy = -1)
                - 'MID_PRICE' : mid price
                - 'START_IDX' : index into dispatch period sequence
                - 'END_IDX' : index into dispatch period sequence
            Optional entries are:
                - 'CLIP_SIZE' : if not None and different from 0
                    triggers clip size constraints.
                - 'CURRENT_POS' : current position. Single
                    numeric value.
                    If we buy (SB = -1) the product then we are
                    long CURRENT_POS, if CURRENT_POS > 0,
                    short otherwise.
                    If we sell (SB = 1) the product then we are
                    short CURRENT_POS, if CURRENT_POS > 0,
                    long otherwise.
                - 'TRADE_SIZE_MIN' : if not None and different
                    from 0 triggers min trade size constraints
                - 'TRADE_SIZE_MAX' : if not None
                    triggers max trade size constraints
                - 'DISCOUNT_FACTOR' : discount factor(s) applicable to
                    cash flows from dispatch volumes during dispatch periods.
                    Defaults to discount_factor if not none, to 1.0 otherwise

        @param entity_list: list of instantiated and initialised
            object instances, being (direct or indirect) sub-class
            of L{gnw.entity.Entity} and L{gnw.product.Product.entity_type_list}.
        @type entity_list: instances of L{gnw.entity.Entity}
        
        @param discount_factor: discount factor(s) applicable to
            cash flows from position for each dispatch period
        @type discount_factor: None, numeric value or sequence type
            of length len( dispatch_period ) of numeric types.
            
        @param dispatch_period: sequence type of numeric values defining
            the number of dispatch periods ( = len( dispatch_period) ) and
            the duration of each dispatch period (hours). The dispatch
            periods need not be uniform.
        @type dispatch_period: sequence type of positive numeric values
        
        @return: reference to L{gnw.product.Product} instance 
        """
        # check for availability of mandatory inputs/dictionary elements
        if 'NAME' not in prd_dict:
            raise ValueError, "'NAME' not found in product dictionary"
        
        if 'SB' not in prd_dict:
            raise ValueError, "'SB' not found in product dictionary"
        
        if 'MID_PRICE' not in prd_dict:
            raise ValueError, "'MID_PRICE' not found in product dictionary"
        
        if 'START_IDX' not in prd_dict:
            raise ValueError, "'START_IDX' not found in product dictionary"
        
        if 'END_IDX' not in prd_dict:
            raise ValueError, "'END_IDX' not found in product dictionary"
        
        # check for availability of optional inputs/dictionary elements
        CLIP_SIZE = None
        if 'CLIP_SIZE' in prd_dict:
            CLIP_SIZE = prd_dict['CLIP_SIZE']
            
        CURRENT_POS = None
        if 'CURRENT_POS' in prd_dict:
            CURRENT_POS = prd_dict['CURRENT_POS']

        TRADE_SIZE_MIN = None
        if 'TRADE_SIZE_MIN' in prd_dict:
            TRADE_SIZE_MIN = prd_dict['TRADE_SIZE_MIN']
        TRADE_SIZE_MAX = None
        if 'TRADE_SIZE_MAX' in prd_dict:
            TRADE_SIZE_MAX = prd_dict['TRADE_SIZE_MAX'] 

        DISCOUNT_FACTOR = None
        if discount_factor is not None:
            DISCOUNT_FACTOR = discount_factor
        if 'DISCOUNT_FACTOR' in prd_dict and prd_dict['DISCOUNT_FACTOR'] is not None:
            DISCOUNT_FACTOR = prd_dict['DISCOUNT_FACTOR']


        # crate object
        return Product( name = prd_dict['NAME'],
                        entityList = entity_list,
                        sellbuy = prd_dict['SB'],
                        midPrice = prd_dict['MID_PRICE'],
                        clipSize = CLIP_SIZE,
                        currentPosition = CURRENT_POS,
                        deliveryPeriod = (prd_dict['START_IDX'], prd_dict['END_IDX']),
                        capacityLimit = (TRADE_SIZE_MIN, TRADE_SIZE_MAX), 
                        discountFactor = DISCOUNT_FACTOR,
                        dispatchPeriod = dispatch_period )
        
    
    Create = staticmethod(Create)


    def CreateFromDataDict( prd_dict={}, data_dict={}, verbose=False):
        """
        Creates a L{gnw.product.Product} instance and encapsulated
        entity objects from given inputs.
        
        @param prd_dict: passed as is as first argument to
            factory function L{gnw.product_factory.ProductFactory.Create}
        @type prd_dict: L{dict}
        
        @param data_dict: holds information to instantiate
            and initialise all entity objects that self
            encapsulates, as well as a default discount factor
            (sequence) and dispatch period sequence.
            Mandatory entires are:
                - 'GNRL_DICT' : holds general information on
                    optimisation problem
                - 'MRKT_DICT' : holds market information (note:
                     not properly used in this context yet, requires
                     refactoring of gnw and current data formating
                     routines (in gnw.dll)). Specifically, contains
                     sub-entries
                         - 'DISPATCH_PERIOD' : mandatory sequence of
                             numeric values defining duration of individual
                             dispatch periods and number of exercise
                             periods (note: should be moved into
                             'GNRL_DICT')
                         - 'DISCOUNT_FACTOR' : optional (sequence) of
                             numeric values defining discount factor
                             applicable to cash flows arising from
                             each dispatch period.
            Optional entries are:
                - 'TRN_DICT_LIST' : list of dictionaries
                    each holding information on a specific
                    trade TRaNche entity (note: trade tranche
                    dictionaries should be moved into the
                    respective product dictionary contained
                    in 'PRD_DICT_LIST' to mirror encapsulation
                    structure of products and tranches)
        @type data_dict: L{dict} 
                    
        @param verbose: whether to print progress messages to
             the console, or be quiet
        @type verbose: L{bool} 
            
        @return: reference to L{gnw.product.Product} instance 
        """
        # mandatory inputs/dictionary items
        if 'GNRL_DICT' not in data_dict:
            raise ValueError, "'GNRL_DICT' not found in data dictionary"
        gnrl_dict = data_dict['GNRL_DICT']
        
        if 'MRKT_DICT' not in data_dict:
            raise ValueError, "'MRKT_DICT' not found in data dictionary"
        mrkt_dict = data_dict['MRKT_DICT']
        
        if 'DISPATCH_PERIOD' not in mrkt_dict:
            raise ValueError, "'DISPATCH_PERIOD' not found in sub data dictionary with key 'MRKT_DICT'"
        DISPATCH_PERIOD = mrkt_dict['DISPATCH_PERIOD']
        
        # optional inputs/dictionary items
        DISCOUNT_FACTOR = None
        if 'DISCOUNT_FACTOR' in mrkt_dict:
            DISCOUNT_FACTOR = mrkt_dict['DISCOUNT_FACTOR']
        
    
        trn_dict_list = {}
        if 'TRN_DICT_LIST' in data_dict:
            trn_dict_list = data_dict['TRN_DICT_LIST']
            
        
        dbg_print( "... initialising product '%s'" % prd_dict['NAME'], verbose )
        prd_entity_list = []
        
        nTrdTrns = 0
        if 'nTrdTrns' in gnrl_dict and gnrl_dict['nTrdTrns'] > 0:
            nTrdTrns = gnrl_dict['nTrdTrns']
            if nTrdTrns != len( trn_dict_list ):
                raise ValueError, "value for 'nTrdTrns' does not match length of list 'TRN_DICT_LIST'"
            
            dbg_print( "initialising trade tranches ...", verbose )
            for trn_dict in trn_dict_list.itervalues():
                
                dbg_print( "... trade tranche '%s'" % trn_dict['NAME'], verbose )
                trn = TrancheFactory.Create( trn_dict, DISCOUNT_FACTOR, DISPATCH_PERIOD ) 
                prd_entity_list.append( trn )

        return ProductFactory.Create( prd_dict, prd_entity_list, DISCOUNT_FACTOR, DISPATCH_PERIOD )

    CreateFromDataDict = staticmethod( CreateFromDataDict )



if __name__ == "__main__" :
    print "gnw.product_factory.py"
    
# ==============================================================================
#
#   Revision Control:
#
#   $Revision:: 2138                    $   Revision of last commit
#   $Author:: re04179                   $   Author of last commit
#   $Date:: 2009-09-22 14:02:19 +0200 (#$   Date of last commit
#
# ==============================================================================
    