# ==============================================================================
#
#   package         :   GasNetWorks (gnw) Python/pulp fuelled LP/MIP modeller 
#   author          :   Marc Roth (re04179)
#   version         :   $Id: network_factory.py 2138 2009-09-22 12:02:19Z re04179 $
#   heading         :   $HeadURL: http://subversion.rwe.com/svn/s_and_v_projects/GasNetworks/trunk/app/gnw/pulp/src/gnw/network_factory.py $
#
#   Description     :   COM interface sub-package
#
#   Creation Date   :   13Aug2009
#
#   Copyright       :   RWE Supply and Trading GmbH
#
# ==============================================================================
"""
gnw: provides factory for L{gnw.network.Network} objects
"""
from gnw.network import Network
from gnw.util import dbg_print

from gnw.storage_factory import StorageFactory
from gnw.supplier_factory import SupplierFactory
from gnw.firm_profile_factory import FirmProfileFactory
from gnw.market_factory import MarketFactory


class NetworkFactory( object ):
    """
    """
    def Create(ntwrk_dict={}, entity_list=[], discount_factor=None, dispatch_period=None):
        """
        Creates a L{gnw.network.Network} instance
        from given inputs. It is assumed that network
        object related information is given in argument ntwrk_dict and
        no additional entity objects have to be instantiated
        (i.e., all entities that this Market object encapsulates
        is given in argument entity_list)
        
        @param ntwrk_dict: holds information to instantiate
            and initialise a L{gnw.network.Network}
            object instance.
            Mandatory entries are:
                - 'NAME' : unique entity identifier
            Optional entries are:
                - 'DISCOUNT_FACTOR' : discount factor(s) applicable to
                    cash flows from dispatch volumes during dispatch periods.
                    Defaults to discount_factor if not none, to 1.0 otherwise

        @param entity_list: list of instantiated and initialised
            object instances, being (direct or indirect) sub-class
            of L{gnw.entity.Entity} and L{gnw.network.Network.entity_type_list}.
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
        
        @return: reference to L{gnw.network.Network} instance 
        """
        # mandatory inputs/dictionary items
        if 'NAME' not in ntwrk_dict:
            raise ValueError, "'NAME' not found in network dictionary"

        # optional inputs/dictionary items
        DISCOUNT_FACTOR = None
        if discount_factor is not None:
            DISCOUNT_FACTOR = discount_factor
        if 'DISCOUNT_FACTOR' in ntwrk_dict and ntwrk_dict['DISCOUNT_FACTOR'] is not None:
            DISCOUNT_FACTOR = ntwrk_dict['DISCOUNT_FACTOR']

        
        return Network( name = ntwrk_dict['NAME'],
                        entityList = entity_list,
                        discountFactor = DISCOUNT_FACTOR,
                        dispatchPeriod = dispatch_period )
    
    Create = staticmethod( Create )


    def CreateFromDataDict( ntwrk_dict={}, data_dict={}, verbose=False):
        """
        Creates a L{gnw.network.Network} instance and encapsulated
        entity objects from given inputs.
        
        @param ntwrk_dict: passed as is as first argument to
            factory function L{gnw.network_factory.NetworkFactory.Create}
        @type ntwrk_dict: L{dict}
        
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
                - 'STRG_DICT_LIST' : list of dictionaries
                    each holding information on a specific
                    SToRaGe entity
                - 'SPLR_DICT_LIST' : list of dictionaries
                    each holding information on a specific
                    SuPpLR entity
                - 'FRM_DICT_LIST' : list of dictionaries
                    each holding information on a specific
                    FiRM profile entity
        @type data_dict: L{dict} 
                    
        @param verbose: whether to print progress messages to
             the console, or be quiet
        @type verbose: L{bool} 
            
        @return: reference to L{gnw.network.Network} instance 
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
        
    
        strg_dict_list = {}
        if 'STRG_DICT_LIST' in data_dict:
            strg_dict_list = data_dict['STRG_DICT_LIST']
        splr_dict_list = {}
        if 'SPLR_DICT_LIST' in data_dict:
            splr_dict_list = data_dict['SPLR_DICT_LIST']
        frm_dict_list = {}
        if 'FRM_DICT_LIST' in data_dict:
            frm_dict_list = data_dict['FRM_DICT_LIST']
            
        
        dbg_print( "... initialising network '%s'" % ntwrk_dict['NAME'], verbose )
        ntwrk_entity_list = []
        
        # Require storage factory to encapsulate that logic below!!!
        nStrgs = 0
        if 'nStrgs' in gnrl_dict and gnrl_dict['nStrgs'] > 0:
            nStrgs = gnrl_dict['nStrgs']
            if nStrgs != len( strg_dict_list ):
                raise ValueError, "value for 'nStrgs' does not match length of list 'STRG_DICT_LIST'"
            
            dbg_print( "initialising storages ...", verbose )
            for strg_dict in strg_dict_list.itervalues():
                dbg_print( "... storage '%s'" % strg_dict['NAME'], verbose )
                strg = StorageFactory.Create( strg_dict, DISCOUNT_FACTOR, DISPATCH_PERIOD )
                ntwrk_entity_list.append( strg )
        
    
        nSplrs = 0
        if 'nSplrs' in gnrl_dict and gnrl_dict['nSplrs'] > 0:
            nSplrs = gnrl_dict['nSplrs']
            if nSplrs != len( splr_dict_list ):
                raise ValueError, "value for 'nSplrs' does not match length of list 'SPLR_DICT_LIST'"
            
            dbg_print( "initialising suppliers ...", verbose )
            for splr_dict in splr_dict_list.itervalues():
                dbg_print( "... supplier '%s'" % splr_dict['NAME'], verbose )
                splr = SupplierFactory.Create( splr_dict, DISCOUNT_FACTOR, DISPATCH_PERIOD )
                ntwrk_entity_list.append( splr )
        
    
        nFrmPrfls = 0
        if 'nFrmPrfls' in gnrl_dict and gnrl_dict['nFrmPrfls'] > 0:
            nFrmPrfls = gnrl_dict['nFrmPrfls']
            if nFrmPrfls != len( frm_dict_list ):
                raise ValueError, "value for 'nFrmPrfls' does not match length of list 'FRM_DICT_LIST'"
            
            dbg_print( "initialising firm profiles ...", verbose )
            for frm_dict in frm_dict_list.itervalues():
                dbg_print( "... firm profile '%s'" % frm_dict['NAME'], verbose )
                frm = FirmProfileFactory.Create( frm_dict, DISCOUNT_FACTOR, DISPATCH_PERIOD )
                ntwrk_entity_list.append( frm )
    
        dbg_print( "initialising markets ..." , verbose )
        mrkt = MarketFactory.CreateFromDataDict( { 'NAME' : 'mrkt' }, data_dict, verbose)
        ntwrk_entity_list.append( mrkt )

        return NetworkFactory.Create( ntwrk_dict, ntwrk_entity_list, DISCOUNT_FACTOR, DISPATCH_PERIOD )

    CreateFromDataDict = staticmethod( CreateFromDataDict )



if __name__ == "__main__" :
    print "gnw.network_factory.py"
    
# ==============================================================================
#
#   Revision Control:
#
#   $Revision:: 2138                    $   Revision of last commit
#   $Author:: re04179                   $   Author of last commit
#   $Date:: 2009-09-22 14:02:19 +0200 (#$   Date of last commit
#
# ==============================================================================
