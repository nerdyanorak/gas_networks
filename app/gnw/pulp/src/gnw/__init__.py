# ==============================================================================
#
#   package         :   GasNetWorks (gnw) Python/pulp fuelled LP/MIP modeller 
#   author          :   Marc Roth (re04179)
#   version         :   $Id: __init__.py 9768 2010-09-22 20:07:23Z re04179 $
#   heading         :   $HeadURL: http://subversion.rwe.com/svn/s_and_v_projects/GasNetworks/trunk/app/gnw/pulp/src/gnw/__init__.py $
#
#   Description     :   Package file
#
#   Creation Date   :   06Mar2009
#
#   Copyright       :   RWE Supply and Trading GmbH
#
# ==============================================================================
__major__ = 1
__minor__ = 4
__release__ = 3
__version__ = "%d.%d.%d" % (__major__, __minor__, __release__)
__authors__ = ["Marc Roth"]
__copyright__ = "RWE Supply & Trading GmbH"
__eSell__ = 1
__eBuy___ = -1
__very_large_positive_number__ = 1.0e6 # 1 Mio MW capacity
#__debugging__ = 1   # set this to 0 for production deployments
__debugging__ = 0   # set this to 0 for production deployments

__all__ = ["constraint",
           "container_entity",
           "dispatch_product_factory",
           "dispatch_product",
           "entity",
           "firm_profile_factory",
           "firm_profile",
           "market_factory",
           "market",
           "mosel",
           "named_item_parser",
           "named_item",
           "network_factory",
           "network",
           "product_factory",
           "product",
           "pulp_patches",
           "reader",
           "solver_check",
           "solver_factory",
           "storage_factory",
           "storage",
           "supplier_factory",
           "supplier",
           "tranche_factory",
           "tranche",
           "util",
           "writer",
           "xpress_opts_adapter"]

if __name__ == "__main__":
    print "gnw.__init__.py"
    
    print "version:", __version__
    print "authors:", __authors__
    print "copyright:", __copyright__ 
    print "modules:", __all__
    
# ==============================================================================
#
#   Revision Control:
#
#   $Revision:: 9768                    $   Revision of last commit
#   $Author:: re04179                   $   Author of last commit
#   $Date:: 2010-09-22 22:07:23 +0200 (#$   Date of last commit
#
# ==============================================================================
