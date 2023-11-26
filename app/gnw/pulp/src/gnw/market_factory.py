# ==============================================================================
#
#   package         :   GasNetWorks (gnw) Python/pulp fuelled LP/MIP modeller 
#   author          :   Marc Roth (re04179)
#   version         :   $Id: market_factory.py 2138 2009-09-22 12:02:19Z re04179 $
#   heading         :   $HeadURL: http://subversion.rwe.com/svn/s_and_v_projects/GasNetworks/trunk/app/gnw/pulp/src/gnw/market_factory.py $
#
#   Description     :   COM interface sub-package
#
#   Creation Date   :   13Aug2009
#
#   Copyright       :   RWE Supply and Trading GmbH
#
# ==============================================================================
"""
gnw: provides factory for L{gnw.market.Market} objects
"""
from gnw.market import Market
from gnw.util import dbg_print

from gnw.tranche_factory import TrancheFactory
from gnw.product_factory import ProductFactory
from gnw.dispatch_product_factory import DispatchProductFactory


class MarketFactory( object ):
    """
    """
    def Create(mrkt_dict={}, entity_list=[], discount_factor=None, dispatch_period=None):
        """
        Creates a L{gnw.market.Market} instance
        from given inputs. It is assumed that market
        object related information is given in argument mrkt_dict and
        no additional entity objects have to be instantiated
        (i.e., all entities that this Market object encapsulates
        is given in argument entity_list)
        
        @param mrkt_dict: holds information to instantiate
            and initialise a L{gnw.market.Market}
            object instance.
            Mandatory entries are:
                - 'NAME' : unique entity identifier
            Optional entries are:
                - 'DISCOUNT_FACTOR' : discount factor(s) applicable to
                    cash flows from dispatch volumes during dispatch periods.
                    Defaults to discount_factor if not none, to 1.0 otherwise

        @param entity_list: list of instantiated and initialised
            object instances, being (direct or indirect) sub-class
            of L{gnw.entity.Entity} and L{gnw.market.Market.entity_type_list}.
        @type entity_list: instances of L{gnw.entity.Entity}
        
        @param discount_factor: discount factor(s) applicable to
            cash flows from position for each dispatch period
        @type discount_factor: None, numeric value or sequence type
            of length len( dispatch_period ) of numeric types.
            
        @param dispatch_period: sequence type of numeric values defining
            the number of dispatch periods ( = len( dispatch_period ) ) and
            the duration of each dispatch period (hours). The dispatch
            periods need not be uniform.
        @type dispatch_period: sequence type of positive numeric values
        
        @return: reference to L{gnw.market.Market} instance 
        """
        # mandatory inputs/dictionary items
        if 'NAME' not in mrkt_dict:
            raise ValueError, "'NAME' not found in market dictionary"

        # optional inputs/dictionary items
        DISCOUNT_FACTOR = None
        if discount_factor is not None:
            DISCOUNT_FACTOR = discount_factor
        if 'DISCOUNT_FACTOR' in mrkt_dict and mrkt_dict['DISCOUNT_FACTOR'] is not None:
            DISCOUNT_FACTOR = mrkt_dict['DISCOUNT_FACTOR']
        
        
        return Market( name = mrkt_dict['NAME'],
                       entityList = entity_list,
                       discountFactor = DISCOUNT_FACTOR,
                       dispatchPeriod = dispatch_period )
    
    Create = staticmethod( Create )


    def CreateFromDataDict( mrkt_dict={}, data_dict={}, verbose=False):
        """
        Creates a L{gnw.market.Market} instance and encapsulated
        entity objects from given inputs.
        
        @param mrkt_dict: passed as is as first argument to
            factory function L{gnw.market_factory.MarketFactory.Create}
        @type mrkt_dict: L{dict}
        
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
                - 'PRD_DICT_LIST' : list of dictionaries
                    each holding information on a specific
                    standard PRoDuct entity (note: should
                    contain as well a dictionary list of 
                    trade tranche information relating to
                    the product to mirror encapsulation
                    structure)
                - 'DSP_DICT_LIST' : list of dictionaries
                    each holding information on a specific
                    DiSPatch product entity
        @type data_dict: L{dict} 
                    
        @param verbose: whether to print progress messages to
             the console, or be quiet
        @type verbose: L{bool} 
            
        @return: reference to L{gnw.market.Market} instance 
        """
        # mandatory inputs/dictionary items
        if 'GNRL_DICT' not in data_dict:
            raise ValueError, "'GNRL_DICT' not found in data dictionary"
        gnrl_dict = data_dict['GNRL_DICT']
        
        if 'MRKT_DICT' not in data_dict:
            raise ValueError, "'MRKT_DICT' not found in data dictionary"
        mrkt_dict_local = data_dict['MRKT_DICT']
        
        if 'DISPATCH_PERIOD' not in mrkt_dict_local:
            raise ValueError, "'DISPATCH_PERIOD' not found in sub data dictionary with key 'MRKT_DICT'"
        DISPATCH_PERIOD = mrkt_dict_local['DISPATCH_PERIOD']
        
        # optional inputs/dictionary items
        DISCOUNT_FACTOR = None
        if 'DISCOUNT_FACTOR' in mrkt_dict_local:
            DISCOUNT_FACTOR = mrkt_dict_local['DISCOUNT_FACTOR']
        
    
        trn_dict_list = {}
        if 'TRN_DICT_LIST' in data_dict:
            trn_dict_list = data_dict['TRN_DICT_LIST']
        prd_dict_list = {}
        if 'PRD_DICT_LIST' in data_dict:
            prd_dict_list = data_dict['PRD_DICT_LIST']
        dsp_dict_list = {}
        if 'DSP_DICT_LIST' in data_dict:
            dsp_dict_list = data_dict['DSP_DICT_LIST']
            
        dbg_print( "... initialising market '%s'" % mrkt_dict['NAME'], verbose )
        prd_entity_list = []
        mrkt_entity_list = []
        
        # For performance reasons the trade tranche objects
        # are extracted from the data_dict/trn_dict_list
        # respectively here and added to the prd_entity_list,
        # which is passed to the ProductFactory.Create(...)
        # function rather than just calling the
        # ProductFactory.CreateFromDataDict(...) function and
        # extracting and instantiating all the trade tranches
        # over and over again for each standard product!! 
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

        
        nStdPrds = 0
        if 'nStdPrds' in gnrl_dict and gnrl_dict['nStdPrds'] > 0:
            nStdPrds = gnrl_dict['nStdPrds']
            if nStdPrds != len( prd_dict_list ):
                raise ValueError, "value for 'nStdPrds' does not match length of list 'PRD_DICT_LIST'"
            
            dbg_print( "initialising standard products ...", verbose )
            for prd_dict in prd_dict_list.itervalues():
                dbg_print( "... standard product '%s'" % prd_dict['NAME'], verbose )
                prd = ProductFactory.Create( prd_dict, prd_entity_list, DISCOUNT_FACTOR, DISPATCH_PERIOD ) 
                mrkt_entity_list.append( prd )
    
    
        nDspPrds = 0
        if 'nDspPrds' in gnrl_dict and gnrl_dict['nDspPrds'] > 0:
            nDspPrds = gnrl_dict['nDspPrds']
            if nDspPrds != len( dsp_dict_list ):
                raise ValueError, "value for 'nDspPrds' does not match length of list 'DSP_DICT_LIST'"
    
            dbg_print( "initialising dispatch products ...", verbose )
            for dsp_dict in dsp_dict_list.itervalues():
                dbg_print( "... dispatch product '%s'" % dsp_dict['NAME'], verbose )
                dsp = DispatchProductFactory.Create( dsp_dict, DISCOUNT_FACTOR, DISPATCH_PERIOD )
                mrkt_entity_list.append( dsp )
    

        return MarketFactory.Create( mrkt_dict, mrkt_entity_list, DISCOUNT_FACTOR, DISPATCH_PERIOD )

    CreateFromDataDict = staticmethod( CreateFromDataDict )



if __name__ == "__main__" :
    print "gnw.market_factory.py"

# ==============================================================================
#
#   Revision Control:
#
#   $Revision:: 2138                    $   Revision of last commit
#   $Author:: re04179                   $   Author of last commit
#   $Date:: 2009-09-22 14:02:19 +0200 (#$   Date of last commit
#
# ==============================================================================
