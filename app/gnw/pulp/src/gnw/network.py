# ==============================================================================
#
#   package         :   GasNetWorks (gnw) Python/pulp fuelled LP/MIP modeller 
#   author          :   Marc Roth (re04179)
#   version         :   $Id: network.py 4494 2009-12-07 10:16:57Z re04179 $
#   heading         :   $HeadURL: http://subversion.rwe.com/svn/s_and_v_projects/GasNetworks/trunk/app/gnw/pulp/src/gnw/network.py $
#
#   Description     :   Package file
#
#   Creation Date   :   06Mar2009
#
#   Copyright       :   RWE Supply and Trading GmbH
#
# ==============================================================================
"""
gnw: The network class allows to relate other more
'atomic' L{gnw.entity.Entity} sub-classes to each other
using appropriate constraints
"""
import numpy
import pulp

from gnw.entity import FmtDictEntry 
from gnw.container_entity import ContainerEntity
from gnw.storage import Storage
from gnw.supplier import Supplier
from gnw.firm_profile import FirmProfile
from gnw.market import Market

from gnw.util import conditional

from gnw.named_item import NamedItem, NamedItemAttr, NamedItemData
from gnw.named_item import ni_type_named_item


class Network( ContainerEntity ):
    """
    This class provides an abstraction for a
    network and encapsulates entities as given
    in entity_type_list.

    @cvar entity_type_list: sequence holding
         the classinfo self may encapsulate.
         The classinfo values must be
         (direct or indirect) sub-classes of
         L{gnw.entity.Entity}.
    @type entity_type_list: L{tuple} of classinfo
        of (direct or indirect) sub-classes of
        L{gnw.entity.Entity}

    @ivar DISCOUNT_FACTOR: dispatch period dependent discount
        factor.
    @type DISCOUNT_FACTOR: L{numpy.array} of dtype='double'
        of length len(L{DISPATCH_PERIOD})
    """
    entity_type_list = (Storage,
                        Supplier,
                        FirmProfile,
                        Market)

    
    def __init__(self, name,
                 entityList = [],
                 discountFactor = None,
                 dispatchPeriod = None):
        """
        @param name: unique network identifier
        @type name: L{str}
        
        @param entityList: list of Entity class instances
        @type entityList: L{list} of L{gnw.entity.Entity}
        
        @param discountFactor: discount factors applicable to each
            L{gnw.entity.Entity.DISPATCH_PERIOD}.
        @type discountFactor: L{None}, L{float},
            list of L{float}, or L{numpy.array} of dtype='double'
            
        @param dispatchPeriod: dispatch periods in hours [h].
        @type dispatchPeriod: L{list} of L{float} or L{numpy.array}
            of dtype='double'
            
        @raise TypeError:
        """
        super( Network, self ).__init__( name, Network.entity_type_list, entityList )
        
        self.set_DISCOUNT_FACTOR( discountFactor )
        self.set_DISPATCH_PERIOD( dispatchPeriod )
        

    def get_storage(self, name):
        """
        """
        return self.get_entity( name, Storage )


    def get_supplier(self, name):
        """
        """
        return self.get_entity( name, Supplier )


    def get_firm_profile(self, name):
        """
        """
        return self.get_entity( name, FirmProfile )


    def get_market(self, name):
        """
        """
        return self.get_entity( name, Market )


    def set_DISCOUNT_FACTOR(self, value):
        """
        Set discount factor curve. If value is None then discount
        factor curve is set to 1.0, to value otherwise.
        
        @param value: discount factor curve.
        @type value: None, L{float}, L{list} of L{float} or
            L{numpy.array} of dtype='double'
        """
        self.DISCOUNT_FACTOR = conditional( value is None, 1.0, value )


    def set_DISPATCH_PERIOD(self, value):
        """
        Sets dispatch period in super class and
        sets coefficient arrays to appropriate
        size.
        
        @param value: dispatch periods
        @type value: L{list} of L{float} or
            L{numpy.array} of dtype='double'
        """
        super( Network, self ).set_DISPATCH_PERIOD( value )
        
        nSteps = len( self.DISPATCH_PERIOD )
        
        # DISCOUNT_FACTOR
        self.DISCOUNT_FACTOR = \
            self.create_coefficient_array( self.DISCOUNT_FACTOR,
                                           nSteps,
                                           "Length of 'discountFactor' must match length of 'DISPATCH_PERIOD' (gnw.network.Network.set_DISPATCH_PERIOD)" )
        

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
        super( Network, self ).create_model( prefix )
        
        self.create_constraints()


    def create_constraints(self):
        """
        """
        nSteps = len( self.DISPATCH_PERIOD )
        # Network balance equation: For each dispatch period t the sum
        # of volumes dispatched over all storages, all supply contracts,
        # and volumes bought/sold through markets and volumes from
        # firm profiles must equate to zero.
        for t in xrange( nSteps ):
            self.constraint_list.append( 0.0 == \
                pulp.lpSum( [-mrkt.vol[t] for mrkt in self.get_entity_list( Market )] ) + \
                pulp.lpSum( [-strg.SB*strg.vol[t] for strg in self.get_entity_list( Storage )] ) + \
                pulp.lpSum( [-splr.SB*splr.vol[t] for splr in self.get_entity_list( Supplier )] ) + \
                pulp.lpSum( [-frm.SB*frm.vol[t] for frm in self.get_entity_list( FirmProfile )] ) )


    def update_fmt_dict(self, fmt_dict={}):
        """
        Overwrites base class method by updating
        dictionary L{fmt_dict} with network
        specific information and calls base class'
        method L{update_fmt_dict}.
        
        @param fmt_dict: dictionary of keys of type
            L{str} and values of type
            L{gnw.entity.Entity.FmtDictEntry}
        @type fmt_dict: L{dict} 
        """
        nSteps = len( self.DISPATCH_PERIOD )

        fmt_dict.update({'DF' : FmtDictEntry( [ self.ffmt ], 'DF[t]', 1, (nSteps,), False, self.DISCOUNT_FACTOR )})
        
        super( Network, self ).update_fmt_dict( fmt_dict )

    
    def get_lp_var_values(self, key_list=[]):
        """
        Retrieve solution values of all decision variables
        contained in list of storages, products and tranches,
        as well as this network instances itself.
        
        @return: L{gnw.named_item.NamedItem} class instance
            encapsulating all solutions values of the
            decision variables of this
            network L{gnw.entity.Entity} instance and
            all contained L{gnw.entity.Entity} sub-class
            instances (e.g., storage, product, tranche)
        @rtype: L{gnw.named_item.NamedItem}
        """
        strg_named_item_list = []
        for strg in self.get_entity_list( Storage ):
            named_item_list = strg.get_lp_var_values( key_list )
            strg_named_item_list.append( NamedItem( strg.name,
                                                    NamedItemAttr( 1, [len( named_item_list )], [ni_type_named_item] ),
                                                    NamedItemData( named_item_list ) ) )

        splr_named_item_list = []
        for splr in self.get_entity_list( Supplier ):
            named_item_list = splr.get_lp_var_values( key_list )
            splr_named_item_list.append( NamedItem( splr.name,
                                                    NamedItemAttr( 1, [len( named_item_list )], [ni_type_named_item] ),
                                                    NamedItemData( named_item_list ) ) )

        frm_named_item_list = []
        for frm in self.get_entity_list( FirmProfile ):
            named_item_list = frm.get_lp_var_values( key_list )
            frm_named_item_list.append( NamedItem( frm.name,
                                                   NamedItemAttr( 1, [len( named_item_list )], [ni_type_named_item] ),
                                                   NamedItemData( named_item_list ) ) )

        mrkt_named_item_list = []
        for mrkt in self.get_entity_list( Market ):
            named_item_list = mrkt.get_lp_var_values( key_list )
            mrkt_named_item_list.append( NamedItem( mrkt.name,
                                                    NamedItemAttr( 1, [len( named_item_list )], [ni_type_named_item] ),
                                                    NamedItemData( named_item_list ) ) )


        named_item_list = []
        named_item_list.append( super( Network, self).get_lp_var_values( key_list ) )
        
        named_item_list.append( NamedItem( 'STRG_DICT_LIST',
                                           NamedItemAttr( 1, [len( strg_named_item_list )], [ni_type_named_item] ),
                                           NamedItemData( strg_named_item_list ) ) )

        named_item_list.append( NamedItem( 'SPLR_DICT_LIST',
                                           NamedItemAttr( 1, [len( splr_named_item_list )], [ni_type_named_item] ),
                                           NamedItemData( splr_named_item_list ) ) )

        named_item_list.append( NamedItem( 'FRM_DICT_LIST',
                                           NamedItemAttr( 1, [len( frm_named_item_list )], [ni_type_named_item] ),
                                           NamedItemData( frm_named_item_list ) ) )

        named_item_list.append( NamedItem( 'MRKT_DICT_LIST',
                                           NamedItemAttr( 1, [len( mrkt_named_item_list )], [ni_type_named_item] ),
                                           NamedItemData( mrkt_named_item_list ) ) )

        return named_item_list 


    def get_storage_results(self):
        """
        """
        nSteps = len( self.DISPATCH_PERIOD )

        sum_vol = [0.0]*nSteps
        sum_cashflow = [0.0]*nSteps

        for strg in self.get_entity_list( Storage ):
            (vol, cashflow) = strg.get_results()
            for t in xrange( nSteps ):
                sum_vol[t] += vol[t]
                sum_cashflow[t] += cashflow[t]
            
        return [sum_vol, sum_cashflow]


    def get_supplier_results(self):
        """
        """
        nSteps = len( self.DISPATCH_PERIOD )
        
        sum_vol = [0.0]*nSteps
        sum_cashflow = [0.0]*nSteps
        sum_strike = [0.0]*nSteps

        for splr in self.get_entity_list( Supplier ):
            (vol, cashflow, strike) = splr.get_results()
            for t in xrange( nSteps ):
                sum_vol[t] += vol[t]
                sum_cashflow[t] += cashflow[t]
                sum_strike[t] += strike[t]

        return [sum_vol, sum_cashflow, sum_strike]


    def get_market_results(self):
        """
        """
        nSteps = len( self.DISPATCH_PERIOD )
        
        sum_vol = [0.0]*nSteps
        sum_cashflow = [0.0]*nSteps
        
        for mrkt in self.get_entity_list( Market ):
            (vol, cashflow) = mrkt.get_results()
            for t in xrange( nSteps ):
                sum_vol[t] += vol[t]
                sum_cashflow[t] += cashflow[t]
    
        return [sum_vol, sum_cashflow]
    

    def get_product_results(self):
        """
        """
        # order by 'sb' (descending), 'start_idx' (ascending), 'final_idx' (ascending)
        prd_compare = lambda x, y : conditional(x[0] != y[0],
                                                y[0] - x[0],                            # descending
                                                conditional(x[1] != y[1],
                                                            x[1] - y[1],                # ascending    
                                                            conditional(x[2] != y[2],
                                                                        x[2] - y[2],    # ascending
                                                                        0)))

        prd_rslts = []
        for mrkt in self.get_entity_list( Market ):
            prd_rslts += mrkt.get_product_results()

        prd_rslts.sort( cmp = prd_compare )

        return prd_rslts


    def get_tranche_results(self):
        """
        """
        # order by 'sb' (descending), 'start_idx' (ascending), 'final_idx' (ascending)
        trn_compare = lambda x, y : conditional(x[0] != y[0],
                                                y[0] - x[0],                            # descending
                                                conditional(x[1] != y[1],
                                                            x[1] - y[1],                # ascending    
                                                            conditional(x[2] != y[2],
                                                                        x[2] - y[2],    # ascending
                                                                        0)))

        trn_rslts = []
        for mrkt in self.get_entity_list( Market ):
            trn_rslts += mrkt.get_tranche_results()

        trn_rslts.sort( cmp = trn_compare )

        return trn_rslts


    def get_dispatch_product_results(self):
        """
        """
        dsp_rslts = []
        for mrkt in self.get_entity_list( Market ):
            dsp_rslts += mrkt.get_dispatch_product_results()

        return dsp_rslts


    def get_firm_profile_results(self):
        """
        """
        nSteps = len( self.DISPATCH_PERIOD )
        
        sum_vol = [0.0]*nSteps
        sum_cashflow = [0.0]*nSteps
        
        for frm in self.get_entity_list( FirmProfile ):
            (vol, cashflow) = frm.get_results()
            for t in xrange( nSteps ):
                sum_vol[t] += vol[t]
                sum_cashflow[t] += cashflow[t]

        return [sum_vol, sum_cashflow]



if __name__ == "__main__":
    print "gnw.network.py" 

# ==============================================================================
#
#   Revision Control:
#
#   $Revision:: 4494                    $   Revision of last commit
#   $Author:: re04179                   $   Author of last commit
#   $Date:: 2009-12-07 11:16:57 +0100 (#$   Date of last commit
#
# ==============================================================================

