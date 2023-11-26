# ==============================================================================
#
#   package         :   GasNetWorks (gnw) Python/pulp fuelled LP/MIP modeller 
#   author          :   Marc Roth (re04179)
#   version         :   $Id: firm_profile.py 1860 2009-09-07 12:09:18Z re04179 $
#   heading         :   $HeadURL: http://subversion.rwe.com/svn/s_and_v_projects/GasNetworks/trunk/app/gnw/pulp/src/gnw/com/firm_profile.py $
#
#   Description     :   COM interface sub-package
#
#   Creation Date   :   13Aug2009
#
#   Copyright       :   RWE Supply and Trading GmbH
#
# ==============================================================================
"""
gnw.com: provides COM class callable from VB[A]
encapsulating L{gnw.firm_profile.FirmProfile} object instance.
"""
import winerror

from win32com.server.exception import COMException

from gnw.com.entity import COM_Entity
from gnw.firm_profile_factory import FirmProfileFactory
from gnw.com.util import err_value


class COM_FirmProfile( COM_Entity ):
    """
    In order to (re-)generate a GUID do the following
    in a python shell:
        >>> import pythoncom
        >>> print pythoncom.CreateGuid()
    """
    _public_methods_ = ['set_data', 'get_keys', 'get_lp_var_values']
    _reg_progid_ = "RWEST.gnw.FirmProfile"
    _reg_clsid_ = '{233F196C-4FEC-4381-9A84-5892F4085FAF}'


    def set_data(self, niTuples):
        """
        Sets up only L{gnw.firm_profile.FirmProfile} entity.
        If a client instantiates and initialises this class
        as COM object he can add it to the network topology by
        passing it as argument to call of
        L{gnw.com.network.COM_Network.add_entity}
        
        @param niTuples: well formed named item (NI) tuples
            providing information to set up encapsulated
            L{gnw.firm_profile.FirmProfile} entity.
        @type niTuples: L{tuple} [of L{tuple}s [...]]
         
        @raise win32com.server.exception.COMException:
        """
        try:
            super( COM_FirmProfile, self ).set_data( niTuples )
            if 'MRKT_DICT' not in self.data_dict:
                raise ValueError, "missing 'MRKT_DICT' key in parameter 'niTuples'"
            mrkt_dict = self.data_dict['MRKT_DICT']
            
            if 'DISPATCH_PERIOD' not in mrkt_dict:
                raise ValueError, "missing 'DISPATCH_PERIOD' key under 'MRKT_DICT' key"
            DISPATCH_PERIOD = mrkt_dict['DISPATCH_PERIOD']
            
            DISCOUNT_FACTOR = 1.0
            if 'DISCOUNT_FACTOR' in mrkt_dict:
                DISCOUNT_FACTOR = mrkt_dict['DISCOUNT_FACTOR']

            if 'FRM_DICT' not in self.data_dict:
                raise ValueError, "missing 'FRM_DICT' key in parameter 'niTuples'"
            frm_dict = self.data_dict['FRM_DICT']

            self.gnw = FirmProfileFactory.Create( frm_dict, DISCOUNT_FACTOR, DISPATCH_PERIOD )
        
        except ( TypeError, ValueError ):
            raise COMException( err_value(), winerror.DISP_E_TYPEMISMATCH )
        except ( IndexError, KeyError ):
            raise COMException( err_value(), winerror.DISP_E_BADINDEX )
        except:
            raise COMException( err_value(), winerror.DISP_E_EXCEPTION )


        
if __name__ == "__main__" :
    print "gnw.com.firm_profile.py"
    
# ==============================================================================
#
#   Revision Control:
#
#   $Revision:: 1860                    $   Revision of last commit
#   $Author:: re04179                   $   Author of last commit
#   $Date:: 2009-09-07 14:09:18 +0200 (#$   Date of last commit
#
# ==============================================================================
