# ==============================================================================
#
#   package         :   GasNetWorks (gnw) Python/pulp fuelled LP/MIP modeller 
#   author          :   Marc Roth (re04179)
#   version         :   $Id: storage.py 1860 2009-09-07 12:09:18Z re04179 $
#   heading         :   $HeadURL: http://subversion.rwe.com/svn/s_and_v_projects/GasNetworks/trunk/app/gnw/pulp/src/gnw/com/storage.py $
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
encapsulating L{gnw.storage.Storage} object instance.
"""
import winerror

from win32com.server.exception import COMException

from gnw.com.entity import COM_Entity
from gnw.storage_factory import StorageFactory
from gnw.com.util import err_value


class COM_Storage( COM_Entity ):
    """
    In order to (re-)generate a GUID do the following
    in a python shell:
        >>> import pythoncom
        >>> print pythoncom.CreateGuid()
    """
    _public_methods_ = ['set_data', 'get_keys', 'get_lp_var_values']
    _reg_progid_ = "RWEST.gnw.Storage"
    _reg_clsid_ = '{3D0F5B36-3034-45D9-BCC5-8D98EE9D24EC}'


    def set_data(self, niTuples):
        """
        Sets up only L{gnw.storage.Storage} entity.
        If a client instantiates and initialises this class
        as COM object he can add it to the network topology by
        passing it as argument to call of
        L{gnw.com.network.COM_Network.add_entity}
        
        @param niTuples: well formed named item (NI) tuples
            providing information to set up encapsulated
            L{gnw.storage.Storage} entity.
        @type niTuples: L{tuple} [of L{tuple}s [...]]
         
        @raise win32com.server.exception.COMException:
        """
        try:
            super( COM_Storage, self ).set_data( niTuples )

            if 'MRKT_DICT' not in self.data_dict:
                raise ValueError, "missing 'MRKT_DICT' key in parameter 'niTuples'"
            mrkt_dict = self.data_dict['MRKT_DICT']

            if 'DISPATCH_PERIOD' not in mrkt_dict:
                raise ValueError, "missing 'DISPATCH_PERIOD' key under 'MRKT_DICT' key"
            DISPATCH_PERIOD = self.data_dict['MRKT_DICT']['DISPATCH_PERIOD']

            DISCOUNT_FACTOR = 1.0
            if 'DISCOUNT_FACTOR' in mrkt_dict:
                DISCOUNT_FACTOR = mrkt_dict['DISCOUNT_FACTOR']

            if 'STRG_DICT' not in self.data_dict:
                raise ValueError, "missing 'STRG_DICT' key in parameter 'niTuples'"
            strg_dict = self.data_dict['STRG_DICT']

            self.gnw = StorageFactory.Create( strg_dict, DISCOUNT_FACTOR, DISPATCH_PERIOD ) 

        except ( TypeError, ValueError ):
            raise COMException( err_value(), winerror.DISP_E_TYPEMISMATCH )
        except ( IndexError, KeyError ):
            raise COMException( err_value(), winerror.DISP_E_BADINDEX )
        except:
            raise COMException( err_value(), winerror.DISP_E_EXCEPTION )



if __name__ == "__main__" :
    print "gnw.com.storage.py"

# ==============================================================================
#
#   Revision Control:
#
#   $Revision:: 1860                    $   Revision of last commit
#   $Author:: re04179                   $   Author of last commit
#   $Date:: 2009-09-07 14:09:18 +0200 (#$   Date of last commit
#
# ==============================================================================
