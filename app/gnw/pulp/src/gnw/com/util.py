# ==============================================================================
#
#   package         :   GasNetWorks (gnw) Python/pulp fuelled LP/MIP modeller 
#   author          :   Marc Roth (re04179)
#   version         :   $Id: util.py 1860 2009-09-07 12:09:18Z re04179 $
#   heading         :   $HeadURL: http://subversion.rwe.com/svn/s_and_v_projects/GasNetworks/trunk/app/gnw/pulp/src/gnw/com/util.py $
#
#   Description     :   COM interface sub-package
#
#   Creation Date   :   12Mar2009
#
#   Copyright       :   RWE Supply and Trading GmbH
#
# ==============================================================================
"""
gnw.com: provides utilities for gnw.com package modules
"""
from gnw.entity import Entity
from gnw.network import Network
from gnw.storage import Storage
from gnw.supplier import Supplier
from gnw.product import Product
from gnw.tranche import Tranche
from gnw.dispatch_product import DispatchProduct
from gnw.firm_profile import FirmProfile 
from gnw.util import isnumeric, isempty

import sys

isgnwentity = lambda x : isinstance( x, Entity )
isgnwnetwork = lambda x : isinstance( x, Network )
isgnwstorage = lambda x : isinstance( x, Storage )
isgnwsupplier = lambda x : isinstance( x, Supplier )
isgnwproduct = lambda x : isinstance( x, Product )
isgnwtranche = lambda x : isinstance( x, Tranche )
isgnwdispatchproduct = lambda x : isinstance( x, DispatchProduct )
isgnwfirmprofile = lambda x : isinstance( x, FirmProfile )

def err_value():
    return sys.exc_info()[1]

def xl2float( x, default=0.0 ) :
    """depending on format settings empty xl cells are None or ""."""
    if isnumeric( x ) :
        return x
    elif isempty( x ) :
        return default
    else :
        raise ValueError, "Cannot convert to float."

def xl2string( x, default=None ) :
    if isempty( x ) :
        return default
    else :
        return x

class ArrayData( object ) :
    def __init__( self ) :
        self.name = None
        self.attribute = None
        self.data = None

    def check_and_prepare( self, objects={} ) :
        if self.name is None or self.name == "" :
            raise ValueError, "Array data must have a name."

        if not objects.has_key( self.name ) :
            raise ValueError, "Array data refers to unknown object %s."%self.name

        if not objects[self.name].__dict__.has_key(self.attribute) :
            raise ValueError, "Array data refers to unknown attribute %s of object %s."%(self.attribute,self.name)

    def apply( self, objects ) :
        objects[self.name].__dict__[self.attribute] = self.data



if __name__ == "__main__":
    print "gnw.com.util.py"

    anEntity = Storage("strg")

    if isgnwentity( anEntity ):
        print "I'm an entity"
    else:
        print "I'm not an entity"

    if isgnwnetwork( anEntity ):
        print "I'm a network"
    else:
        print "I'm not a nework"

    if isgnwstorage( anEntity ):
        print "I'm a storage"
    else:
        print "I'm not a storage"

    if isgnwsupplier( anEntity ):
        print "I'm a supplier"
    else:
        print "I'm not a supplier"

    if isgnwproduct( anEntity ):
        print "I'm a product"
    else:
        print "I'm not a product"

    if isgnwtranche( anEntity ):
        print "I'm a tranche"
    else:
        print "I'm not a tranche"

# ==============================================================================
#
#   Revision Control:
#
#   $Revision:: 1860                    $   Revision of last commit
#   $Author:: re04179                   $   Author of last commit
#   $Date:: 2009-09-07 14:09:18 +0200 (#$   Date of last commit
#
# ==============================================================================
