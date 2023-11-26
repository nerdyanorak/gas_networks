# ==============================================================================
#
#   package         :   GasNetWorks (gnw) Python/pulp fuelled LP/MIP modeller 
#   author          :   Marc Roth (re04179)
#   version         :   $Id: market.py 2519 2009-10-15 19:07:21Z re04179 $
#   heading         :   $HeadURL: http://subversion.rwe.com/svn/s_and_v_projects/GasNetworks/trunk/app/gnw/pulp/src/gnw/market.py $
#
#   Description     :   COM interface sub-package
#
#   Creation Date   :   13Aug2009
#
#   Copyright       :   RWE Supply and Trading GmbH
#
# ==============================================================================
"""
gnw: provides market abstraction
"""
import numpy
import pulp

from gnw.entity import FmtDictEntry
from gnw.container_entity import ContainerEntity

from gnw.product import Product
from gnw.dispatch_product import DispatchProduct

from gnw.util import conditional

from gnw.named_item import NamedItem, NamedItemAttr, NamedItemData
from gnw.named_item import ni_type_named_item


class Market( ContainerEntity ):
    """
    This class provides an abstraction for a
    market and encapsulates entities as given
    in entity_type_list (currently entities
    L{gnw.product.Product} and
    L{gnw.dispatch_product.DispatchProduct} are
    provisioned).
    
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
    
    @ivar vol: lp affine expression variables
        representing the volume
        in [MWh] of the market during each
        L{DISPATCH_PERIOD}. 
    @type vol: L{numpy.array} of dtype='object' of
        length len(L{DISPATCH_PERIOD}) of L{pulp.LpVariable}
    """
    entity_type_list = (Product,
                        DispatchProduct)
        
    def __init__(self, name,
                 entityList=[],
                 discountFactor=None,
                 dispatchPeriod=None):
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
        super( Market, self ).__init__( name, Market.entity_type_list, entityList )

        self.set_DISCOUNT_FACTOR( discountFactor )
        self.set_DISPATCH_PERIOD( dispatchPeriod )
        
        self.vol = numpy.empty( 0, dtype='object' )
        
    
    def get_product(self, name):
        """
        """
        return self.get_entity( name, Product )
    
    
    def get_dispatch_product(self, name):
        """
        """
        return self.get_entity( name, DispatchProduct )
    
        
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
        creates/checks other coefficient arrays
        for appropriate size/values.
        
        @param value: dispatch periods
        @type value: L{list} of L{float} or
            L{numpy.array} of dtype='double'
        """
        super( Market, self ).set_DISPATCH_PERIOD( value )
        
        nSteps = len( self.DISPATCH_PERIOD )
        
        # DISCOUNT_FACTOR
        self.DISCOUNT_FACTOR = \
            self.create_coefficient_array( self.DISCOUNT_FACTOR,
                                           nSteps,
                                           "Length of 'discountFactor' must match length of 'DISPATCH_PERIOD' (gnw.market.Market.set_DISPATCH_PERIOD)" )


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
        super( Market, self ).create_lp_vars( prefix )
        
        nSteps = len( self.DISPATCH_PERIOD )
        
        self.vol = numpy.array( pulp.LpVariable.matrix( prefix + self.name + "_vol", range( nSteps ) ) )
        
        
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
        super( Market, self ).create_model( prefix )
        
        nSteps = len( self.DISPATCH_PERIOD )
        
        for t in xrange( nSteps ):
            self.constraint_list.append( self.vol[t] == pulp.lpSum( [item.SB*item.vol[t] for item in self.get_entity_list()] ) )

    
    def get_lp_vars(self):
        """
        This method returns a list containing all
        lp variables including the lp variables from
        L{gnw.entity.Entity} sub-class instances
        contained in entity_list_dict.
        
        @return: list of lp variables
        @rtype: L{list} of L{pulp.LpVariable}
        """
        return super( Market, self ).get_lp_vars() \
            + self.vol.tolist()

    
    def update_fmt_dict(self, fmt_dict={}):
        """
        Overwrites base class method by updating
        dictionary L{fmt_dict} with market
        specific information and calls base class'
        method L{update_fmt_dict}.
        
        @param fmt_dict: dictionary of keys of type
            L{str} and values of type
            L{gnw.entity.Entity.FmtDictEntry}
        @type fmt_dict: L{dict} 
        """
        nSteps = len( self.DISPATCH_PERIOD )

        fmt_dict.update({'vol': FmtDictEntry( [ self.ffmt ], 'vol[t] [MWh]', 1, (nSteps,), True,  self.vol ),
                         'DF' : FmtDictEntry( [ self.ffmt ], 'DF[t]',        1, (nSteps,), False, self.DISCOUNT_FACTOR )})
        
        super( Market, self ).update_fmt_dict( fmt_dict )

    
    def get_results(self):
        """
        @todo: add code to extract cashflow information from
            encapsulated entities and aggregate in 'cashflow'
        """
        nSteps = len( self.DISPATCH_PERIOD )
        
        vol = [self.vol[t].varValue for t in xrange( nSteps )]
        cashflow = [0.0]*nSteps
            
        return (vol, cashflow)

    
    def get_lp_var_values(self, key_list=[]):
        """
        Retrieve solution values of all decision variables
        contained in internal entity list 
        as well as this instances itself.
        
        @return: L{gnw.named_item.NamedItem} class instance
            encapsulating all solutions values of the
            decision variables of this
            network L{gnw.entity.Entity} instance and
            all contained L{gnw.entity.Entity} sub-class
            instances.
        @rtype: L{gnw.named_item.NamedItem}
        """
        prd_named_item_list = []
        for prd in self.get_entity_list( Product ):
            named_item_list = prd.get_lp_var_values( key_list ) 
            prd_named_item_list.append( NamedItem( prd.name,
                                                   NamedItemAttr( 1, [len( named_item_list )], [ni_type_named_item] ),
                                                   NamedItemData( named_item_list ) ) )

        dsp_named_item_list = []
        for dsp in self.get_entity_list( DispatchProduct ):
            named_item_list = dsp.get_lp_var_values( key_list )
            dsp_named_item_list.append( NamedItem( dsp.name,
                                                   NamedItemAttr( 1, [len( named_item_list )], [ni_type_named_item] ),
                                                   NamedItemData( named_item_list ) ) )

        named_item_list = []
        named_item_list.append( super( Market, self).get_lp_var_values( key_list ) )

        named_item_list.append( NamedItem( 'PRD_DICT_LIST',
                                           NamedItemAttr( 1, [len( prd_named_item_list )], [ni_type_named_item] ),
                                           NamedItemData( prd_named_item_list ) ) )

        named_item_list.append( NamedItem( 'DSP_DICT_LIST',
                                           NamedItemAttr( 1, [len( dsp_named_item_list )], [ni_type_named_item] ),
                                           NamedItemData( dsp_named_item_list ) ) )
            
        return named_item_list 


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
        for prd in self.get_entity_list( Product ):
            (sb, start_idx, final_idx, cap_min, cap_max, price, clip_size, current_pos, pos) = prd.get_results()
            prd_rslts.append( [sb, start_idx, final_idx, cap_min, cap_max, price, clip_size, current_pos, pos] )

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
        for prd in self.get_entity_list( Product ):
            trn_rslts += prd.get_tranche_results()

        trn_rslts.sort( cmp = trn_compare )

        return trn_rslts


    def get_dispatch_product_results(self):
        """
        """
        nSteps = len( self.DISPATCH_PERIOD )
        
        sum_vol = [0.0]*nSteps
        sum_cashflow = [0.0]*nSteps
        
        for dsp in self.get_entity_list( DispatchProduct ):
            (vol, cashflow) = dsp.get_results()
            for t in xrange( nSteps ):
                sum_vol[t] += vol[t]
                sum_cashflow[t] += cashflow[t]

        return [sum_vol, sum_cashflow]


    
if __name__ == "__main__" :
    print "gnw.market.py"
    
# ==============================================================================
#
#   Revision Control:
#
#   $Revision:: 2519                    $   Revision of last commit
#   $Author:: re04179                   $   Author of last commit
#   $Date:: 2009-10-15 21:07:21 +0200 (#$   Date of last commit
#
# ==============================================================================
