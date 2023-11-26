# ==============================================================================
#
#   package         :   GasNetWorks (gnw) Python/pulp fuelled LP/MIP modeller 
#   author          :   Marc Roth (re04179)
#   version         :   $Id: product.py 1860 2009-09-07 12:09:18Z re04179 $
#   heading         :   $HeadURL: http://subversion.rwe.com/svn/s_and_v_projects/GasNetworks/trunk/app/gnw/pulp/src/gnw/com/product.py $
#
#   Description     :   COM interface sub-package
#
#   Creation Date   :   24Mar2009
#
#   Copyright       :   RWE Supply and Trading GmbH
#
# ==============================================================================
"""
gnw.com: provides COM class callable from VB[A] 
encapsulating L{gnw.product.Product} object instance.
"""
import winerror

from win32com.server.exception import COMException

from gnw.com.entity import COM_Entity
from gnw.product_factory import ProductFactory
from gnw.com.util import err_value


class COM_Product( COM_Entity ):
    """
    In order to (re-)generate a GUID do the following
    in a python shell:
        >>> import pythoncom
        >>> print pythoncom.CreateGuid()
    """
    _public_methods_ = ['set_data', 'get_keys', 'get_lp_var_values']
    _reg_progid_ = "RWEST.gnw.Product"
    _reg_clsid_ = '{D55ED103-754C-4DF1-8008-FF3EC3611BEF}'


    def set_all_data(self, niTuples):
        """
        Sets up entire product object from data
        given in parameter niTuples. This means
        that niTuples must contain all necessary
        information! See L{gnw.com.nidatatuples.niDataTuples}
        and L{gnw.com.btsf_supplier_tuples.btsfSplrTuples} as
        examples for well formed niTuples
        
        @todo: Refactor class hierarchy by introducing
            a super class COM_ContainerEntity that
            inherits from COM_Entity and handles all
            object instantiations/initialisations of
            gnw entities encapsulated in
            self.gnw,  which is itself a a sub-class
            of {gnw.container_entity.ContainerEntity} 
        
        @param niTuples: well formed named item (NI) tuples
            providing all information to set up entire
            product object (including all
            L{gnw.tranche.Tranche}s, etc.)
        @type niTuples: L{tuple} [of L{tuple}s [...]]
        
        @raise win32com.server.exception.COMException:
        """
        try:
            super( COM_Product, self ).set_data( niTuples )

            prd_dict = {'NAME' : "prd"}
            if 'NAME' in self.data_dict:
                prd_dict['NAME'] = self.data_dict['NAME']
                
            self.gnw = ProductFactory.CreateFromDataDict( prd_dict, self.data_dict )
            
        except ( TypeError, ValueError ):
            raise COMException( err_value(), winerror.DISP_E_TYPEMISMATCH )
        except ( IndexError, KeyError ):
            raise COMException( err_value(), winerror.DISP_E_BADINDEX )
        except:
            raise COMException( err_value(), winerror.DISP_E_EXCEPTION )
        

    def set_data(self, niTuples):
        """
        Sets up only encapsulated L{gnw.product.Product}
        entity. Other entities making up the product object
        have to be set using method
        L{gnw.com.product.COM_Product.set_entities}.
        If a client instantiates and initialises this class
        as COM object he can add it to the network object by
        passing it as argument to call of
        L{gnw.com.market.COM_Market.add_entity}
        
        @param niTuples: well formed named item (NI) tuples
            providing information to set up only
            encapsulated L{gnw.product.Product} entity.
        @type niTuples: L{tuple} [of L{tuple}s [...]]
        
        @raise win32com.server.exception.COMException:
        """
        try:
            super( COM_Product, self ).set_data( niTuples )

            if 'MRKT_DICT' not in self.data_dict:
                raise ValueError, "missing 'MRKT_DICT' key in parameter 'niTuples'"
            mrkt_dict = self.data_dict['MRKT_DICT']

            if 'DISPATCH_PERIOD' not in mrkt_dict:
                raise ValueError, "missing 'DISPATCH_PERIOD' key under 'MRKT_DICT' key"
            DISPATCH_PERIOD = mrkt_dict['DISPATCH_PERIOD']

            DISCOUNT_FACTOR = 1.0
            if 'DISCOUNT_FACTOR' in mrkt_dict:
                DISCOUNT_FACTOR = mrkt_dict['DISCOUNT_FACTOR']

            if 'PRD_DICT' not in self.data_dict:
                raise ValueError, "missing 'PRD_DICT' key in parameter 'niTuples'"
            prd_dict = self.data_dict['PRD_DICT']

            self.gnw = ProductFactory.Create( prd_dict, [], DISCOUNT_FACTOR, DISPATCH_PERIOD )

        except ( TypeError, ValueError ):
            raise COMException( err_value(), winerror.DISP_E_TYPEMISMATCH )
        except ( IndexError, KeyError ):
            raise COMException( err_value(), winerror.DISP_E_BADINDEX )
        except:
            raise COMException( err_value(), winerror.DISP_E_EXCEPTION )



if __name__ == "__main__" :
    print "gnw.com.product.py"

# ==============================================================================
#
#   Revision Control:
#
#   $Revision:: 1860                    $   Revision of last commit
#   $Author:: re04179                   $   Author of last commit
#   $Date:: 2009-09-07 14:09:18 +0200 (#$   Date of last commit
#
# ==============================================================================
