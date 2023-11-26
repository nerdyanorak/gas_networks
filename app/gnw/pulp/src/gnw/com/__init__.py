# ==============================================================================
#
#   package         :   GasNetWorks (gnw) Python/pulp fuelled LP/MIP modeller 
#   author          :   Marc Roth (re04179)
#   version         :   $Id: __init__.py 2138 2009-09-22 12:02:19Z re04179 $
#   heading         :   $HeadURL: http://subversion.rwe.com/svn/s_and_v_projects/GasNetworks/trunk/app/gnw/pulp/src/gnw/com/__init__.py $
#
#   Description     :   COM interface sub-package
#
#   Creation Date   :   12Mar2009
#
#   Copyright       :   RWE Supply and Trading GmbH
#
# ==============================================================================
import gnw
__version__ = gnw.__version__
__authors__ = gnw.__authors__
__copyright__ = gnw.__copyright__
__debugging__ = gnw.__debugging__


__all__ = [#"btsf_storage_tuples",
           #"btsf_supplier_tuples",
           #"btsf_supplier_tuples2",
           "dispatch_product",
           "entity",
           "firm_profile",
           "interface",
           "market",
           "network",
           #"nidatatuples",
           #"nisolvertuples",
           "product",
           "storage",
           "supplier",
           "tranche",
           "util"]



if __name__ == "__main__":
    print "gnw.com.__init__.py"
    
    print "version:", __version__
    print "authors:", __authors__
    print "copyright:", __copyright__
    print "modules:", __all__
     
# ==============================================================================
#
#   Revision Control:
#
#   $Revision:: 2138                    $   Revision of last commit
#   $Author:: re04179                   $   Author of last commit
#   $Date:: 2009-09-22 14:02:19 +0200 (#$   Date of last commit
#
# ==============================================================================
