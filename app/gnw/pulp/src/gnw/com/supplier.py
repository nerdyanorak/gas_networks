# ==============================================================================
#
#   package         :   GasNetWorks (gnw) Python/pulp fuelled LP/MIP modeller 
#   author          :   Marc Roth (re04179)
#   version         :   $Id: supplier.py 2393 2009-10-11 15:12:50Z re04179 $
#   heading         :   $HeadURL: http://subversion.rwe.com/svn/s_and_v_projects/GasNetworks/trunk/app/gnw/pulp/src/gnw/com/supplier.py $
#
#   Description     :   COM interface sub-package
#
#   Creation Date   :   25May2009
#
#   Copyright       :   RWE Supply and Trading GmbH
#
# ==============================================================================
"""
gnw.com: provides COM class callable from VB[A] 
encapsulating L{gnw.supplier.Supplier} object instance.
"""
import winerror

from win32com.server.exception import COMException

from gnw.com.entity import COM_Entity
from gnw.supplier_factory import SupplierFactory
from gnw.com.util import err_value


class COM_Supplier( COM_Entity ):
    """
    In order to (re-)generate a GUID do the following
    in a python shell:
        >>> import pythoncom
        >>> print pythoncom.CreateGuid()
    """
    _public_methods_ = ['set_data', 'get_keys', 'get_lp_var_values',
                        'get_results', 'get_mup_results', 'get_cfw_results']
    _reg_progid_ = "RWEST.gnw.Supplier"
    _reg_clsid_ = '{53A50794-4C34-4647-858C-9F693141505F}'


    def set_data(self, niTuples):
        """
        Sets up only L{gnw.supplier.Supplier} entity.
        If a client instantiates and initialises this class
        as COM object he can add it to the network topology by
        passing it as argument to call of
        L{gnw.com.network.COM_Network.add_entity}
        
        @param niTuples: well formed named item (NI) tuples
            providing information to set up encapsulated
            L{gnw.supplier.Supplier} entity.
        @type niTuples: L{tuple} [of L{tuple}s [...]]
         
        @raise win32com.server.exception.COMException:
        """
        try:
            super( COM_Supplier, self ).set_data( niTuples )

            if 'MRKT_DICT' not in self.data_dict:
                raise ValueError, "missing 'MRKT_DICT' key in parameter 'niTuples'"
            mrkt_dict = self.data_dict['MRKT_DICT']

            if 'DISPATCH_PERIOD' not in mrkt_dict:
                raise ValueError, "missing 'DISPATCH_PERIOD' key under 'MRKT_DICT' key"
            DISPATCH_PERIOD = mrkt_dict['DISPATCH_PERIOD']

            DSICOUNT_FACTOR = 1.0
            if 'DISCOUNT_FACTOR' in mrkt_dict:
                DISCOUNT_FACTOR = mrkt_dict['DISCOUNT_FACTOR']

            if 'SPLR_DICT' not in self.data_dict:
                raise ValueError, "missing 'SPLR_DICT' key in parameter 'niTuples'"
            splr_dict = self.data_dict['SPLR_DICT']

            self.gnw = SupplierFactory.Create( splr_dict, DISCOUNT_FACTOR, DISPATCH_PERIOD )
                                                    
        except ( TypeError, ValueError ):
            raise COMException( err_value(), winerror.DISP_E_TYPEMISMATCH )
        except ( IndexError, KeyError ):
            raise COMException( err_value(), winerror.DISP_E_BADINDEX )
        except:
            raise COMException( err_value(), winerror.DISP_E_EXCEPTION )


    def get_results(self):
        """
        @return: LP decision variable values and
            coefficient data
        @rtype: L{list} [of L{list}s [of ...]]

        @raise win32com.server.exception.COMException:
        """
        try:
            return self.gnw.get_results()

        except ( TypeError, ValueError ):
            raise COMException( err_value(), winerror.DISP_E_TYPEMISMATCH )
        except ( IndexError, KeyError ):
            raise COMException( err_value(), winerror.DISP_E_BADINDEX )
        except:
            raise COMException( err_value(), winerror.DISP_E_EXCEPTION )


    def get_mup_results(self, accountingPeriod):
        """
        @param accountingPeriod: flag indicating whether
            accounting period make-up results (accountingPeriod == True), or
            dispatch period make-up results (accountingPeriod == False)
            shall be returned
        @type accountingPeriod: L{bool}
         
        @return: LP decision variable values and
            coefficient data
        @rtype: L{list} [of L{list}s [of ...]]

        @raise win32com.server.exception.COMException:
        """
        try:
            return self.gnw.get_mup_results( accountingPeriod )

        except ( TypeError, ValueError ):
            raise COMException( err_value(), winerror.DISP_E_TYPEMISMATCH )
        except ( IndexError, KeyError ):
            raise COMException( err_value(), winerror.DISP_E_BADINDEX )
        except:
            raise COMException( err_value(), winerror.DISP_E_EXCEPTION )


    def get_cfw_results(self):
        """
        @return: LP decision variable values and
            coefficient data
        @rtype: L{list} [of L{list}s [of ...]]

        @raise win32com.server.exception.COMException:
        """
        try:
            return self.gnw.get_cfw_results()

        except ( TypeError, ValueError ):
            raise COMException( err_value(), winerror.DISP_E_TYPEMISMATCH )
        except ( IndexError, KeyError ):
            raise COMException( err_value(), winerror.DISP_E_BADINDEX )
        except:
            raise COMException( err_value(), winerror.DISP_E_EXCEPTION )


if __name__ == "__main__" :
    print "gnw.com.supplier.py"

# ==============================================================================
#
#   Revision Control:
#
#   $Revision:: 2393                    $   Revision of last commit
#   $Author:: re04179                   $   Author of last commit
#   $Date:: 2009-10-11 17:12:50 +0200 (#$   Date of last commit
#
# ==============================================================================
