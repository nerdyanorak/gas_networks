# ==============================================================================
#
#   package         :   GasNetWorks (gnw) Python/pulp fuelled LP/MIP modeller 
#   author          :   Marc Roth (re04179)
#   version         :   $Id: network.py 6858 2010-04-16 09:42:18Z re04179 $
#   heading         :   $HeadURL: http://subversion.rwe.com/svn/s_and_v_projects/GasNetworks/trunk/app/gnw/pulp/src/gnw/com/network.py $
#
#   Description     :   COM interface sub-package
#
#   Creation Date   :   12Mar2009
#
#   Copyright       :   RWE Supply and Trading GmbH
#
# ==============================================================================
"""
gnw.com: provides COM class callable from VB[A] 
encapsulating L{gnw.network.Network} object instance.
"""
import pulp
import winerror
import string

from win32com.server.exception import COMException
from win32com.server.util import wrap, unwrap

from gnw.com import __debugging__

from gnw.named_item_parser import NamedItemParser 

from gnw.network_factory import NetworkFactory

from gnw.solver_check import SolverCheck
from gnw.solver_factory import SolverFactory

from gnw.storage import Storage
from gnw.supplier import Supplier
from gnw.product import Product
from gnw.tranche import Tranche
from gnw.dispatch_product import DispatchProduct
from gnw.firm_profile import FirmProfile
from gnw.market import Market

from gnw.com.entity import COM_Entity
from gnw.com.storage import COM_Storage
from gnw.com.supplier import COM_Supplier
from gnw.com.product import COM_Product
from gnw.com.tranche import COM_Tranche
from gnw.com.dispatch_product import COM_DispatchProduct
from gnw.com.firm_profile import COM_FirmProfile
from gnw.com.market import COM_Market

from gnw.com.util import err_value


class COM_Network( COM_Entity ):
    """
    This is the main object to access the gnw functionality
    through a COM interface.
    
    How to use it:
        - Instantiate an object, i.e.,
            - Dim gnwObj as Object
            - set gnwObj = CreateObject( "RWEST.gnw.Network" )
        - Initialise object, i.e.,
            - gnwObj.set_all_data ( niProblemDataTuples )
        - Solve problem, i.e.,
            - Dim objectiveVal as Double
            - objectiveVal = gnwObj.solve()
        - Retrieve further results, ie.,
            - Dim result as Variant\
            - result = gnwObj.get_lp_var_values( [someQueryKeys] )
            
    @ivar problem: interface object to optimisation engine
    @type problem: L{pulp.LpProblem}
    @ivar solver: holds reference to solver instance. 
    @type solver: L{pulp.LpSolver}

    In order to (re-)generate a GUID do the following
    in a python shell:
        >>> import pythoncom
        >>> print pythoncom.CreateGuid()
    """
    _public_methods_ = ['set_data', 'solve',
                        'get_solver_status', 'get_objective_value', 'get_mark_to_market_value',
                        'set_solver',
                        'set_all_data',
                        'set_entities', 'add_entity', 'get_entity'
                        'create_storage', 'get_storage_results', 'get_storage',
                        'create_supplier', 'get_supplier_results', 'get_supplier',
                        'create_product', 'get_product_results', 'get_product',
                        'create_tranche', 'get_tranche_results', 'get_tranche',
                        'create_dispatch_product', 'get_dispatch_product_results', 'get_dispatch_product',
                        'create_firm_profile', 'get_firm_profile_results', 'get_firm_profile',
                        'create_market', 'get_market_results', 'get_market']
    _reg_progid_ = "RWEST.gnw.Network"
    _reg_clsid_ = '{D2337751-CED8-4FEA-B045-32F2B444DD9B}'


    def __init__(self):
        """
        URLs :
            - "http://s060a9230:8080/csgb-xpress/services/XpressExecutionServer?wsdl"
            - "http://xpressprod.rwe.com:8080/csgb-xpress/services/XpressExecutionServer?wsdl"                
            - "http://xpressdev.rwe.com:8090/csgb-xpress/services/XpressExecutionServer?wsdl"                
        """
        super( COM_Network, self ).__init__()
        self.problem = pulp.LpProblem
        self.solver = pulp.LpSolverDefault


    def set_solver(self, niSolverTuples ):
        """
        (Re-)initialise the L{self.solver} with
        new solver definition.
        
        @param niSolverTuples: holds named item tuples (NI)
            describing a solver (see
            L{gnw.com.nisolvertuples.niSolverTuples} for an
            example) which will be converted into a dictionary
            and passed to L{gnw.solver_factory.SolverFactory.create}
            to initialise a new solver instance.
        @type niSolverTuples: L{tuple} of NI tuples  
        
        @raise win32com.server.exception.COMException: if niSolverTuples fail consistency check. 
        """
        try:
            named_item_list = []
            for item in niSolverTuples:
                named_item_list.append( NamedItemParser.parse( item, str( item[0] ) != 'key' ) )

            solver_dict = {}
            for item in named_item_list:
                solver_dict.update( item.get_dict() )

            if not SolverCheck.check_dict( solver_dict ):
                raise ValueError, "parameter 'niSolverTuples' failed consistency check"

            self.solver = SolverFactory.create( solver_dict )
 
        except ( TypeError, ValueError ):
            raise COMException( err_value(), winerror.DISP_E_TYPEMISMATCH )
        except ( IndexError, KeyError ):
            raise COMException( err_value(), winerror.DISP_E_BADINDEX )
        except:
            raise COMException( err_value(), winerror.DISP_E_EXCEPTION )


    def set_all_data(self, niTuples):
        """
        Sets up entire gas network topology using
        data given in parameter niTuples. This means
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
            providing all information to set up entire gas
            network topology.
        @type niTuples: L{tuple} [of L{tuple}s [...]]
        
        @raise win32com.server.exception.COMException:
        """
        try:
            super( COM_Network, self ).set_data( niTuples )
            
            ntwrk_dict = {'NAME' : "ntwrk"}
            if 'NAME' in self.data_dict:
                ntwrk_dict['NAME'] = self.data_dict['NAME']
                
            self.gnw = NetworkFactory.CreateFromDataDict( ntwrk_dict, self.data_dict )

        except ( TypeError, ValueError ):
            raise COMException( err_value(), winerror.DISP_E_TYPEMISMATCH )
        except ( IndexError, KeyError ):
            raise COMException( err_value(), winerror.DISP_E_BADINDEX )
        except:
            raise COMException( err_value(), winerror.DISP_E_EXCEPTION )


    def set_data(self, niTuples):
        """
        Sets up only L{gnw.network.Network} entity.
        Other entities making up the network topology
        have to be set using method
        L{set_entities}
        
        @param niTuples: well formed named item (NI) tuples
            providing information to set up only
            encapsulated L{gnw.network.Network} entity.
        @type niTuples: L{tuple} [of L{tuple}s [...]]
        
        @raise win32com.server.exception.COMException:
        """
        try:
            super( COM_Network, self ).set_data( niTuples )
            
            if 'MRKT_DICT' not in self.data_dict:
                raise ValueError, "missing 'MRKT_DICT' key in parameter 'niTuples'"
            mrkt_dict = self.data_dict['MRKT_DICT']

            if 'DISCOUNT_FACTOR' not in self.data_dict['MRKT_DICT']:
                raise ValueError, "missing 'DISCOUNT_FACTOR' key under 'MRKT_DICT' key"
            DISCOUNT_FACTOR = mrkt_dict['DISCOUNT_FACTOR']

            if 'DISPATCH_PERIOD' not in self.data_dict['MRKT_DICT']:
                raise ValueError, "missing 'DISPATCH_PERIOD' key under 'MRKT_DICT' key"
            DISPATCH_PERIOD = mrkt_dict['DISPATCH_PERIOD']

            if 'NTWRK_DICT' not in self.data_dict:
                raise ValueError, "missing 'NTWRK_DICT' key in parameter 'niTuples'"
            ntwrk_dict = self.data_dict['NTWRK_DICT']

            self.gnw = NetworkFactory.Create( ntwrk_dict, [], DISCOUNT_FACTOR, DISPATCH_PERIOD)

        except ( TypeError, ValueError ):
            raise COMException( err_value(), winerror.DISP_E_TYPEMISMATCH )
        except ( IndexError, KeyError ):
            raise COMException( err_value(), winerror.DISP_E_BADINDEX )
        except:
            raise COMException( err_value(), winerror.DISP_E_EXCEPTION )


    def set_entities(self, com_item_list):
        """
        Sets entities in encapsulated
        L{gnw.network.Network} entity that
        make up network toplogy
        
        @todo: Refactor class hierarchy by introducing
            a super class COM_ContainerEntity that
            inherits from COM_Entity and handles all
            object instantiations/initialisations of
            gnw entities encapsulated in
            self.gnw,  which is itself a a sub-class
            of {gnw.container_entity.ContainerEntity} 
        
        @param com_item_list: a list of COM object instances
            sub-classed from L{gnw.com.entity.Entity}
            instantiated on client side.
        @type com_item_list: L{list} of
            COM object instances
            derived from L{gnw.com.entity.Entity}
            
        @raise win32com.server.exception.COMException: 
        """
        try:
            item_list = []
            for com_item in com_item_list:
                item = unwrap( com_item )
                item_list.append( item.gnw )

            self.gnw.set_entity_list( item_list )

        except ( TypeError, ValueError ):
            raise COMException( err_value(), winerror.DISP_E_TYPEMISMATCH )
        except ( IndexError, KeyError ):
            raise COMException( err_value(), winerror.DISP_E_BADINDEX )
        except:
            raise COMException( err_value(), winerror.DISP_E_EXCEPTION )


    def add_entity(self, com_item):
        """
        Adds a single entity to list of
        L{gnw.entity.Entity}s encapsulated
        in L{gnw.network.Network}.
        
        @todo: Refactor class hierarchy by introducing
            a super class COM_ContainerEntity that
            inherits from COM_Entity and handles all
            object instantiations/initialisations of
            gnw entities encapsulated in
            self.gnw,  which is itself a a sub-class
            of {gnw.container_entity.ContainerEntity} 
        
        @param com_item: COM object instance
            sub-classed from L{gnw.com.entity.Entity}
            instantiated on the client side.
        @type com_item: COM object instance
            dervied from L{gnw.com.entity.Entity}
        
        @raise win32com.server.exception.COMException:
        """
        try:
            item = unwrap( com_item )
            self.gnw.add_entity( item.gnw )

        except ( TypeError, ValueError ):
            raise COMException( err_value(), winerror.DISP_E_TYPEMISMATCH )
        except ( IndexError, KeyError ):
            raise COMException( err_value(), winerror.DISP_E_BADINDEX )
        except:
            raise COMException( err_value(), winerror.DISP_E_EXCEPTION )


    def get_entity(self, name, instance_name):
        """
        Return a L{gnw.entity.Entity} object
        instance wrapped in a corresponding
        L{gnw.com.entity.Entity} object instance
        of given name and instance_name.
        
        @todo: Refactor class hierarchy by introducing
            a super class COM_ContainerEntity that
            inherits from COM_Entity and handles all
            object instantiations/initialisations of
            gnw entities encapsulated in
            self.gnw,  which is itself a a sub-class
            of {gnw.container_entity.ContainerEntity} 
        
        @param name: name of existing entity object instance
        @type name: L{str} or L{unicode}
        
        @param instance_name: instance type name as
            given in dictionary instance_name_dict
        @type instance_name: L{str} or L{unicode}
        
        @return: sub-class of L{gnw.com.entity.Entity}
            corresponding to instance_name
        @rtype: appropriately wrapped sub-class of L{gnw.com.entity.Entity}
        
        @raise win32com.server.exception.COMException: if no instance of given type and name is found
        """
        try:
            instance_name_dict = {"storage"             : Storage,
                                  "supplier"            : Supplier,
                                  "product"             : Product,
                                  "tranche"             : Tranche,
                                  "dispatch_product"    : DispatchProduct,
                                  "firm_profile"        : FirmProfile,
                                  "market"              : Market}

            instance_name = string.lower( str( instance_name ) )

            if instance_name not in instance_name_dict:
                raise ValueError, "instance_name '%s' not supported" % instance_name 
            instance = instance_name_dict[instance_name]

            e = self.gnw.get_entity( str( name ), instance )
            if e is None:
                raise IndexError, "instance '%s% with name '%s' not found" (instance_name, name)

            com_instance_name_dict = {"storage"             : COM_Storage,
                                      "supplier"            : COM_Supplier,
                                      "product"             : COM_Product,
                                      "tranche"             : COM_Tranche,
                                      "dispatch_product"    : COM_DispatchProduct,
                                      "firm_profile"        : COM_FirmProfile,
                                      "market"              : COM_Market}

            com_e = com_instance_name_dict[instance_name]()
            com_e.gnw = e
            return wrap( com_e, useDispatcher=self.dispatcher )

        except ( TypeError, ValueError ):
            raise COMException( err_value(), winerror.DISP_E_TYPEMISMATCH )
        except ( IndexError, KeyError ):
            raise COMException( err_value(), winerror.DISP_E_BADINDEX )
        except:
            raise COMException( err_value(), winerror.DISP_E_EXCEPTION )


    def create_storage(self, niTuples):
        """
        Returns and appropriately created and
        wrapped L{gnw.com.storage.Storage} COM object
        instance given construction data.
        
        @param niTuples: named item (NI) tuples encapsulating
            all necessary information to create a
            L{gnw.com.storage.Storage} COM object.
            See L{gnw.storage_factory.StorageFactory} for
            details on required data.
        @type niTuples: L{tuple} [of L{tuple}s [...]]
        
        @return: COM object instance of type
            L{gnw.com.storage.Storage}
        @rtype: appropriately wrapped sub-class of L{gnw.com.storage.Storage}

        @raise win32com.server.exception.COMException:
        """
        try:
            com_entity = COM_Storage()
            com_entity.set_data( niTuples )
            return wrap( com_entity, useDispatcher=self.dispatcher )

        except ( TypeError, ValueError ):
            raise COMException( err_value(), winerror.DISP_E_TYPEMISMATCH )
        except ( IndexError, KeyError ):
            raise COMException( err_value(), winerror.DISP_E_BADINDEX )
        except:
            raise COMException( err_value(), winerror.DISP_E_EXCEPTION )


    def get_storage(self, name):
        """
        Return a L{gnw.storage.Storage} object
        instance wrapped in a corresponding
        L{gnw.com.storage.Storage} object instance
        of given name.
        
        @param name: name of existing entity object instance
        @type name: L{str} or L{unicode}
        
        @return: sub-class of L{gnw.com.storage.Storage}
            corresponding to instance_name
        @rtype: appropriately wrapped sub-class of L{gnw.com.storage.Storage}

        @raise win32com.server.exception.COMException:
        """
        try:
            return self.get_entity( name, "storage" )

        except ( TypeError, ValueError ):
            raise COMException( err_value(), winerror.DISP_E_TYPEMISMATCH )
        except ( IndexError, KeyError ):
            raise COMException( err_value(), winerror.DISP_E_BADINDEX )
        except:
            raise COMException( err_value(), winerror.DISP_E_EXCEPTION )


    def create_supplier(self, niTuples):
        """
        Returns and appropriately created and
        wrapped L{gnw.com.supplier.Supplier} COM object
        instance given construction data.
        
        @param niTuples: named item (NI) tuples encapsulating
            all necessary information to create a
            L{gnw.com.supplier.Supplier} COM object.
            See L{gnw.supplier_factory.SupplierFactory} for
            details on required data.
        @type niTuples: L{tuple} [of L{tuple}s [...]]
        
        @return: COM object instance of type
            L{gnw.com.supplier.Supplier}
        @rtype: appropriately wrapped sub-class of L{gnw.com.supplier.Supplier}

        @raise win32com.server.exception.COMException:
        """
        try:
            com_entity = COM_Supplier()
            com_entity.set_data( niTuples )
            return wrap( com_entity, useDispatcher=self.dispatcher )

        except ( TypeError, ValueError ):
            raise COMException( err_value(), winerror.DISP_E_TYPEMISMATCH )
        except ( IndexError, KeyError ):
            raise COMException( err_value(), winerror.DISP_E_BADINDEX )
        except:
            raise COMException( err_value(), winerror.DISP_E_EXCEPTION )


    def get_supplier(self, name):
        """
        Return a L{gnw.supplier.Supplier} object
        instance wrapped in a corresponding
        L{gnw.com.supplier.Supplier} object instance
        of given name.
        
        @param name: name of existing entity object instance
        @type name: L{str} or L{unicode}
        
        @return: sub-class of L{gnw.com.supplier.Supplier}
            corresponding to instance_name
        @rtype: appropriately wrapped sub-class of L{gnw.com.supplier.Supplier}

        @raise win32com.server.exception.COMException:
        """
        try:
            return self.get_entity( name, "supplier" )

        except ( TypeError, ValueError ):
            raise COMException( err_value(), winerror.DISP_E_TYPEMISMATCH )
        except ( IndexError, KeyError ):
            raise COMException( err_value(), winerror.DISP_E_BADINDEX )
        except:
            raise COMException( err_value(), winerror.DISP_E_EXCEPTION )


    def create_product(self, niTuples):
        """
        Returns and appropriately created and
        wrapped L{gnw.com.product.Product} COM object
        instance given construction data.
        
        @param niTuples: named item (NI) tuples encapsulating
            all necessary information to create a
            L{gnw.com.product.Product} COM object.
            See L{gnw.product_factory.ProductFactory} for
            details on required data.
        @type niTuples: L{tuple} [of L{tuple}s [...]]
        
        @return: COM object instance of type
            L{gnw.com.product.Product}
        @rtype: appropriately wrapped sub-class of L{gnw.com.product.Product}

        @raise win32com.server.exception.COMException:
        """
        try:
            com_entity = COM_Product()
            com_entity.set_data( niTuples )
            return wrap( com_entity, useDispatcher=self.dispatcher )

        except ( TypeError, ValueError ):
            raise COMException( err_value(), winerror.DISP_E_TYPEMISMATCH )
        except ( IndexError, KeyError ):
            raise COMException( err_value(), winerror.DISP_E_BADINDEX )
        except:
            raise COMException( err_value(), winerror.DISP_E_EXCEPTION )


    def get_product(self, name):
        """
        Return a L{gnw.product.Product} object
        instance wrapped in a corresponding
        L{gnw.com.product.Product} object instance
        of given name.
        
        @param name: name of existing entity object instance
        @type name: L{str} or L{unicode}
        
        @return: sub-class of L{gnw.com.product.Product}
            corresponding to instance_name
        @rtype: appropriately wrapped sub-class of L{gnw.com.product.Product}

        @raise win32com.server.exception.COMException:
        """
        try:
            return self.get_entity( name, "product" )

        except ( TypeError, ValueError ):
            raise COMException( err_value(), winerror.DISP_E_TYPEMISMATCH )
        except ( IndexError, KeyError ):
            raise COMException( err_value(), winerror.DISP_E_BADINDEX )
        except:
            raise COMException( err_value(), winerror.DISP_E_EXCEPTION )


    def create_tranche(self, niTuples):
        """
        Returns and appropriately created and
        wrapped L{gnw.com.trance.Tranche} COM object
        instance given construction data.
        
        @param niTuples: named item (NI) tuples encapsulating
            all necessary information to create a
            L{gnw.com.trance.Tranche} COM object.
            See L{gnw.tranche_factory.TrancheFactory} for
            details on required data.
        @type niTuples: L{tuple} [of L{tuple}s [...]]
        
        @return: COM object instance of type
            L{gnw.com.trance.Tranche}
        @rtype: appropriately wrapped sub-class of L{gnw.com.trance.Tranche}

        @raise win32com.server.exception.COMException:
        """
        try:
            com_entity = COM_Tranche()
            com_entity.set_data( niTuples )
            return wrap( com_entity, useDispatcher=self.dispatcher )

        except ( TypeError, ValueError ):
            raise COMException( err_value(), winerror.DISP_E_TYPEMISMATCH )
        except ( IndexError, KeyError ):
            raise COMException( err_value(), winerror.DISP_E_BADINDEX )
        except:
            raise COMException( err_value(), winerror.DISP_E_EXCEPTION )


    def get_tranche(self, name):
        """
        Return a L{gnw.tranche.Tranche} object
        instance wrapped in a corresponding
        L{gnw.com.tranche.Tranche} object instance
        of given name.
        
        @param name: name of existing entity object instance
        @type name: L{str} or L{unicode}
        
        @return: sub-class of L{gnw.com.tranche.Tranche}
            corresponding to instance_name
        @rtype: appropriately wrapped sub-class of L{gnw.com.tranche.Tranche}

        @raise win32com.server.exception.COMException:
        """
        try:
            return self.get_entity( name, "tranche" )

        except ( TypeError, ValueError ):
            raise COMException( err_value(), winerror.DISP_E_TYPEMISMATCH )
        except ( IndexError, KeyError ):
            raise COMException( err_value(), winerror.DISP_E_BADINDEX )
        except:
            raise COMException( err_value(), winerror.DISP_E_EXCEPTION )


    def create_dispatch_product(self, niTuples):
        """
        Returns and appropriately created and
        wrapped L{gnw.com.dispatch_product.DispatchProduct} COM object
        instance given construction data.
        
        @param niTuples: named item (NI) tuples encapsulating
            all necessary information to create a
            L{gnw.com.dispatch_product.DispatchProduct} COM object.
            See L{gnw.dispatch_product_factory.DispatchProductFactory} for
            details on required data.
        @type niTuples: L{tuple} [of L{tuple}s [...]]
        
        @return: COM object instance of type
            L{gnw.com.dispatch_product.DispatchProduct}
        @rtype: appropriately wrapped sub-class of L{gnw.com.dispatch_product.DispatchProduct}

        @raise win32com.server.exception.COMException:
        """
        try:
            com_entity = COM_DispatchProduct()
            com_entity.set_data( niTuples )
            return wrap( com_entity, useDispatcher=self.dispatcher )

        except ( TypeError, ValueError ):
            raise COMException( err_value(), winerror.DISP_E_TYPEMISMATCH )
        except ( IndexError, KeyError ):
            raise COMException( err_value(), winerror.DISP_E_BADINDEX )
        except:
            raise COMException( err_value(), winerror.DISP_E_EXCEPTION )


    def get_dispatch_product(self, name):
        """
        Return a L{gnw.dispatch_product.DispatchProduct} object
        instance wrapped in a corresponding
        L{gnw.com.dispatch_product.DispatchProduct} object instance
        of given name.
        
        @param name: name of existing entity object instance
        @type name: L{str} or L{unicode}
        
        @return: sub-class of L{gnw.com.dispatch_product.DispatchProduct}
            corresponding to instance_name
        @rtype: appropriately wrapped sub-class of L{gnw.com.dispatch_product.DispatchProduct}

        @raise win32com.server.exception.COMException:
        """
        try:
            return self.get_entity( name, "dispatch_product" )

        except ( TypeError, ValueError ):
            raise COMException( err_value(), winerror.DISP_E_TYPEMISMATCH )
        except ( IndexError, KeyError ):
            raise COMException( err_value(), winerror.DISP_E_BADINDEX )
        except:
            raise COMException( err_value(), winerror.DISP_E_EXCEPTION )


    def create_firm_profile(self, niTuples):
        """
        Returns and appropriately created and
        wrapped L{gnw.com.firm_profile.FirmProfile} COM object
        instance given construction data.
        
        @param niTuples: named item (NI) tuples encapsulating
            all necessary information to create a
            L{gnw.com.profile.FirmProfile} COM object.
            See L{gnw.firm_profile_factory.FirmProfileFactory} for
            details on required data.
        @type niTuples: L{tuple} [of L{tuple}s [...]]
        
        @return: COM object instance of type
            L{gnw.com.profile.FirmProfile}
        @rtype: appropriately wrapped sub-class of L{gnw.com.profile.FirmProfile}

        @raise win32com.server.exception.COMException:
        """
        try:
            com_entity = COM_FirmProfile()
            com_entity.set_data( niTuples )
            return wrap( com_entity, useDispatcher=self.dispatcher )

        except ( TypeError, ValueError ):
            raise COMException( err_value(), winerror.DISP_E_TYPEMISMATCH )
        except ( IndexError, KeyError ):
            raise COMException( err_value(), winerror.DISP_E_BADINDEX )
        except:
            raise COMException( err_value(), winerror.DISP_E_EXCEPTION )


    def get_firm_profile(self, name):
        """
        Return a L{gnw.firm_profile.FirmProfile} object
        instance wrapped in a corresponding
        L{gnw.com.firm_profile.FirmProfile} object instance
        of given name.
        
        @param name: name of existing entity object instance
        @type name: L{str} or L{unicode}
        
        @return: sub-class of L{gnw.com.firm_profile.FirmProfile}
            corresponding to instance_name
        @rtype: appropriately wrapped sub-class of L{gnw.com.firm_profile.FirmProfile}

        @raise win32com.server.exception.COMException:
        """
        try:
            return self.get_entity( name, "firm_profile" )

        except ( TypeError, ValueError ):
            raise COMException( err_value(), winerror.DISP_E_TYPEMISMATCH )
        except ( IndexError, KeyError ):
            raise COMException( err_value(), winerror.DISP_E_BADINDEX )
        except:
            raise COMException( err_value(), winerror.DISP_E_EXCEPTION )

    
    def create_market(self, niTuples):
        """
        Returns and appropriately created and
        wrapped L{gnw.com.market.Market} COM object
        instance given construction data.
        
        @param niTuples: named item (NI) tuples encapsulating
            all necessary information to create a
            L{gnw.com.market.Market} COM object.
            See L{gnw.market_factory.MarketFactory} for
            details on required data.
        @type niTuples: L{tuple} [of L{tuple}s [...]]
        
        @return: COM object instance of type
            L{gnw.com.market.Market}
        @rtype: appropriately wrapped sub-class of L{gnw.com.market.Market}

        @raise win32com.server.exception.COMException:
        """
        try:
            com_entity = COM_Market()
            com_entity.set_data( niTuples )
            return wrap( com_entity, useDispatcher=self.dispatcher )

        except ( TypeError, ValueError ):
            raise COMException( err_value(), winerror.DISP_E_TYPEMISMATCH )
        except ( IndexError, KeyError ):
            raise COMException( err_value(), winerror.DISP_E_BADINDEX )
        except:
            raise COMException( err_value(), winerror.DISP_E_EXCEPTION )


    def get_market(self, name):
        """
        Return a L{gnw.market.Market} object
        instance wrapped in a corresponding
        L{gnw.com.market.Market} object instance
        of given name.
        
        @param name: name of existing entity object instance
        @type name: L{str} or L{unicode}
        
        @return: sub-class of L{gnw.com.market.Market}
            corresponding to instance_name
        @rtype: appropriately wrapped sub-class of L{gnw.com.market.Market}

        @raise win32com.server.exception.COMException:
        """
        try:
            return self.get_entity( name, "market" )

        except ( TypeError, ValueError ):
            raise COMException( err_value(), winerror.DISP_E_TYPEMISMATCH )
        except ( IndexError, KeyError ):
            raise COMException( err_value(), winerror.DISP_E_BADINDEX )
        except:
            raise COMException( err_value(), winerror.DISP_E_EXCEPTION )

    
    def solve(self):
        """
        Optimises network problem given by the ensemble
        of the instantiated (sub-)classes of type
        L{gnw.entity.Entity} contained in the 
        L{gnw.network.Network} entity referenced
        by L{self.gnw} by recursively creating
        all LP variables, by setting up LP model,
        creating a L{pulp.LpProblem} and initialising
        it with the combined objective function and
        all constraints of all entities. And
        solves the problem using the solver 
        setup with in L{gnw.com.network.COM_Network.set_solver}
        or using pulp's default solver.
         
        @return: if solved to optimality, L{True},
            L{False} otherwise.
        @rtype: L{bool}
        
        @raise win32com.server.exception.COMException: 
        """
        try:
            self.gnw.create_lp_vars()
            self.gnw.create_model()

            prblm_name = "gnw"
            self.problem = pulp.LpProblem( prblm_name, pulp.LpMaximize )
            self.problem += self.gnw.get_objective()

            constraint_list = self.gnw.get_constraints()
            for constraint in constraint_list:
                self.problem += constraint 

            if __debugging__:
                fname = "%s/%s-%s-%d.%s" % ("c:/temp", self.problem.name, "network", len( self.gnw.DISPATCH_PERIOD ), "lp")
                self.problem.writeLP( fname )

            status = self.problem.solve( self.solver )

            return status == pulp.LpStatusOptimal

        except ( TypeError, ValueError ):
            raise COMException( err_value(), winerror.DISP_E_TYPEMISMATCH )
        except ( IndexError, KeyError ):
            raise COMException( err_value(), winerror.DISP_E_BADINDEX )
        except:
            raise COMException( err_value(), winerror.DISP_E_EXCEPTION )


    def get_solver_status(self):
        """
        @return: solver status
        @rtype: L{int}

        @raise win32com.server.exception.COMException:
        """
        try:
            return self.problem.status

        except ( TypeError, ValueError ):
            raise COMException( err_value(), winerror.DISP_E_TYPEMISMATCH )
        except ( IndexError, KeyError ):
            raise COMException( err_value(), winerror.DISP_E_BADINDEX )
        except:
            raise COMException( err_value(), winerror.DISP_E_EXCEPTION )


    def get_objective_value(self):
        """
        @return: objective value if solver status
            is optimal (i.e., L{pulp.LpStatusOptimal},
            zero otherwise.
        @rtype: L{float}

        @raise win32com.server.exception.COMException:
        """
        try:
            if self.get_solver_status() == pulp.LpStatusOptimal:
                return self.problem.objective.value()
            else:
                return 0.0

        except ( TypeError, ValueError ):
            raise COMException( err_value(), winerror.DISP_E_TYPEMISMATCH )
        except ( IndexError, KeyError ):
            raise COMException( err_value(), winerror.DISP_E_BADINDEX )
        except:
            raise COMException( err_value(), winerror.DISP_E_EXCEPTION )


    def get_mark_to_market_value(self):
        """
        Returns the value of the mark to market, i.e.,
        all standard product positions are marked at
        mid rather than bid/ask prices.
        
        @return: mark to market value if optimisation
            status is equal to L{pulp.LpStatusOptimal},
            zero otherwise.
        @rtype: L{float}

        @raise win32com.server.exception.COMException:
        """
        try:
            if self.get_solver_status() == pulp.LpStatusOptimal:
                return self.gnw.get_mark_to_market_value().value()
            else:
                return 0.0

        except ( TypeError, ValueError ):
            raise COMException( err_value(), winerror.DISP_E_TYPEMISMATCH )
        except ( IndexError, KeyError ):
            raise COMException( err_value(), winerror.DISP_E_BADINDEX )
        except:
            raise COMException( err_value(), winerror.DISP_E_EXCEPTION )


    def get_lp_var_values(self, key_list=[]):
        """
        @return: LP decision variable values for
        given list of keys (for all if list is empty)
        @rtype: L{gnw.named_item.NamedItem}

        @raise win32com.server.exception.COMException:
        """
        try:
            return self.gnw.get_lp_var_values( key_list )

        except ( TypeError, ValueError ):
            raise COMException( err_value(), winerror.DISP_E_TYPEMISMATCH )
        except ( IndexError, KeyError ):
            raise COMException( err_value(), winerror.DISP_E_BADINDEX )
        except:
            raise COMException( err_value(), winerror.DISP_E_EXCEPTION )


    def get_storage_results(self):
        """
        @return: LP decision variable values and
            coefficient data
        @rtype: L{list} [of L{list}s [of ...]]

        @raise win32com.server.exception.COMException:
        """
        try:
            return self.gnw.get_storage_results()

        except ( TypeError, ValueError ):
            raise COMException( err_value(), winerror.DISP_E_TYPEMISMATCH )
        except ( IndexError, KeyError ):
            raise COMException( err_value(), winerror.DISP_E_BADINDEX )
        except:
            raise COMException( err_value(), winerror.DISP_E_EXCEPTION )


    def get_supplier_results(self):
        """
        @return: LP decision variable values and
            coefficient data
        @rtype: L{list} [of L{list}s [of ...]]

        @raise win32com.server.exception.COMException:
        """
        try:
            return self.gnw.get_supplier_results()

        except ( TypeError, ValueError ):
            raise COMException( err_value(), winerror.DISP_E_TYPEMISMATCH )
        except ( IndexError, KeyError ):
            raise COMException( err_value(), winerror.DISP_E_BADINDEX )
        except:
            raise COMException( err_value(), winerror.DISP_E_EXCEPTION )


    def get_product_results(self):
        """
        @return: LP decision variable values and
            coefficient data
        @rtype: L{list} [of L{list}s [of ...]]

        @raise win32com.server.exception.COMException:
        """
        try:
            return self.gnw.get_product_results()

        except ( TypeError, ValueError ):
            raise COMException( err_value(), winerror.DISP_E_TYPEMISMATCH )
        except ( IndexError, KeyError ):
            raise COMException( err_value(), winerror.DISP_E_BADINDEX )
        except:
            raise COMException( err_value(), winerror.DISP_E_EXCEPTION )


    def get_tranche_results(self):
        """
        @return: LP decision variable values and
            coefficient data
        @rtype: L{list} [of L{list}s [of ...]]

        @raise win32com.server.exception.COMException:
        """
        try:
            return self.gnw.get_tranche_results()

        except ( TypeError, ValueError ):
            raise COMException( err_value(), winerror.DISP_E_TYPEMISMATCH )
        except ( IndexError, KeyError ):
            raise COMException( err_value(), winerror.DISP_E_BADINDEX )
        except:
            raise COMException( err_value(), winerror.DISP_E_EXCEPTION )


    def get_dispatch_product_results(self):
        """
        @return: LP decision variable values and
            coefficient data
        @rtype: L{list} [of L{list}s [of ...]]

        @raise win32com.server.exception.COMException:
        """
        try:
            return self.gnw.get_dispatch_product_results()

        except ( TypeError, ValueError ):
            raise COMException( err_value(), winerror.DISP_E_TYPEMISMATCH )
        except ( IndexError, KeyError ):
            raise COMException( err_value(), winerror.DISP_E_BADINDEX )
        except:
            raise COMException( err_value(), winerror.DISP_E_EXCEPTION )


    def get_firm_profile_results(self):
        """
        @return: LP decision variable values and
            coefficient data
        @rtype: L{list} [of L{list}s [of ...]]

        @raise win32com.server.exception.COMException:
        """
        try:
            return self.gnw.get_firm_profile_results()

        except ( TypeError, ValueError ):
            raise COMException( err_value(), winerror.DISP_E_TYPEMISMATCH )
        except ( IndexError, KeyError ):
            raise COMException( err_value(), winerror.DISP_E_BADINDEX )
        except:
            raise COMException( err_value(), winerror.DISP_E_EXCEPTION )


    def get_market_results(self):
        """
        @return: LP decision variable values and
            coefficient data
        @rtype: L{list} [of L{list}s [of ...]]

        @raise win32com.server.exception.COMException:
        """
        try:
            return self.gnw.get_market_results()

        except ( TypeError, ValueError ):
            raise COMException( err_value(), winerror.DISP_E_TYPEMISMATCH )
        except ( IndexError, KeyError ):
            raise COMException( err_value(), winerror.DISP_E_BADINDEX )
        except:
            raise COMException( err_value(), winerror.DISP_E_EXCEPTION )


if __name__ == "__main__" :
    print "gnw.com.network.py"
    

    gnwNtwrkObj = COM_Network()

    from gnw.com.nisolvertuples import niSolverTuples
    #niSolverTuples = ((u'name', (0, (), u'str'), u'XPRESS_REMOTE_CLIENT'), (u'attr', (1, (5,), (u'NI',)), ((u'URL', (0, (), u'str'), u'http://xpressprod.rwe.com:8080/csgb-xpress/services/XpressExecutionServer?wsdl'), (u'MIPRELCUTOFF', (0, (), u'float'), 0.0001), (u'MIPRELSTOP', (0, (), u'float'), 0.050000000000000003), (u'MAXTIME', (0, (), u'int'), 0), (u'PIVOTTOL', (0, (), u'float'), 9.9999999999999994e-012))))
#    niSolverTuples = ((u'name', (0, (), u'str'), u'LP_SOLVE'), (u'attr', (1, (0,), (u'NI',)), None))
    niSolverTuples = ((u'name', (0, (), u'str'), u'XPRESS_REMOTE_CLIENT'), (u'attr', (1, (6,), (u'NI',)), ((u'URL', (0, (), u'str'), u'http://xpressprod.rwe.com:8080/csgb-xpress/services/XpressExecutionServer?wsdl'), (u'MIPRELCUTOFF', (0, (), u'float'), 9.9999999999999995e-008), (u'MIPRELSTOP', (0, (), u'float'), 1.0000000000000001e-005), (u'MAXTIME', (0, (), u'int'), 0), (u'PIVOTTOL', (0, (), u'float'), 9.9999999999999994e-012), (u'FEASTOL', (0, (), u'float'), 1.0000000000000001e-005))))
    gnwNtwrkObj.set_solver( niSolverTuples ) 

#    from gnw.com.nidatatuples import niDataTuples
#    gnwNtwrkObj.set_all_data( niDataTuples )

#    from gnw.com.btsf_supplier_tuples import btsfSplrTuples
#    gnwNtwrkObj.set_all_data( btsfSplrTuples )

#    from gnw.com.btsf_supplier_tuples2 import btsfSplrTuples2
#    gnwNtwrkObj.set_all_data( btsfSplrTuples2 )

    from gnw.com.btsf_supplier_tuples3 import btsfSplrTuples3
    gnwNtwrkObj.set_all_data( btsfSplrTuples3 )

#    from gnw.com.btsf_storage_tuples import btsfStrgTuples
#    gnwNtwrkObj.set_all_data( btsfStrgTuples )

    success = gnwNtwrkObj.solve()
    print "Status =", pulp.LpStatus[gnwNtwrkObj.get_solver_status()]

    splrStdResults = gnwNtwrkObj.get_supplier_results()
    
#    ICOMobj = gnwNtwrkObj.get_entity( "gasterra", "supplier" )
    ICOMobj = gnwNtwrkObj.get_entity( "Wingas", "supplier" )
#        ICOMobj = gnwNtwrkObj.get_storage("virtstor")

    comObj = unwrap( ICOMobj )

    keys = comObj.get_keys()
    
    constraint_coeff_list = comObj.gnw.CONSTRAINT_COEFF
    print "START;FINAL;BOUND;BTYPE;CTYPE"
    for c in constraint_coeff_list:
            print "%d;%d;%f;%d;%d" % (c.START, c.FINAL, c.BOUND, c.BTYPE, c.CTYPE)
        
        
    ICOMMrktObj = gnwNtwrkObj.get_entity( "mrkt", "market" )
    comMrktObj = unwrap( ICOMMrktObj )
    
    prd_entity_list = comMrktObj.gnw.get_entity_list( Product )
    print "NAME;SB;START;END;CAP_MIN;CAP_MAX;CLIP_SIZE;CUR_POS;MID_PRICE"
    for prd in prd_entity_list:
        from gnw.util import conditional
        print "%s;%d;%d;%d;%f;%f;%f;%f;%f;;" % (prd.name, prd.SB,
                                              prd.DELIVERY_PERIOD[0], prd.DELIVERY_PERIOD[1],
                                              conditional( prd.CAPACITY_LIMIT[0], prd.CAPACITY_LIMIT[0], 0.0 ),
                                              conditional( prd.CAPACITY_LIMIT[1], prd.CAPACITY_LIMIT[1], 0.0 ),
                                              conditional( prd.CLIP_SIZE, prd.CLIP_SIZE, 0.0 ),
                                              prd.CURRENT_POSITION, prd.MID_PRICE),
        
        trn_entity_list = prd.get_entity_list( Tranche )
        for trn in trn_entity_list:
            print "%s;%d;%d;%d;%f;%f;%f;;" % (trn.name, trn.SB, trn.DELIVERY_PERIOD[0], trn.DELIVERY_PERIOD[1],
                                            conditional( trn.CAPACITY_LIMIT[0], trn.CAPACITY_LIMIT[0], 0.0 ),
                                            conditional( trn.CAPACITY_LIMIT[1], trn.CAPACITY_LIMIT[1], 0.0 ), trn.BID_ASK_ADJ),
            
        print

        
    if success:
        print "Objective =", gnwNtwrkObj.get_objective_value()
    
        rslt = comObj.get_lp_var_values((u'pos_pct',u'vol'))
    
        from gnw.util import issequence

        mup_acc_period_rslts = comObj.get_mup_results( True )
        if mup_acc_period_rslts is not None \
        and issequence( mup_acc_period_rslts ) \
        and len( mup_acc_period_rslts ) >= 2:
            print "Make-up Accounting Period Results:"
            for k in xrange( len( mup_acc_period_rslts[0] ) ):
                print "Period =", k, "; Balance =", mup_acc_period_rslts[0][k], "; Change =", mup_acc_period_rslts[1][k]
        

        mup_dsp_period_rslts  = comObj.get_mup_results( False )
        if mup_dsp_period_rslts is not None \
        and issequence( mup_dsp_period_rslts ) \
        and len( mup_dsp_period_rslts ) >= 1 \
        and mup_dsp_period_rslts[0] is not None \
        and issequence( mup_dsp_period_rslts[0] ):
            print "Make-up Dispatch Period Results:"
            for t in xrange( len( mup_dsp_period_rslts[0] ) ):
                print "Period =", t, "; Take =", mup_dsp_period_rslts[0][t]
                
            print "Sum =", sum( [mup_dsp_period_rslts[0][t] for t in xrange( len( mup_dsp_period_rslts[0] ) )] )
            

        cfw_rslts = comObj.gnw.get_cfw_results()
    
        strg_rslt = gnwNtwrkObj.get_storage_results()
        print strg_rslt
    
        splr_rslt = gnwNtwrkObj.get_supplier_results()
        print splr_rslt
    
        prd_rslt = gnwNtwrkObj.get_product_results()
        print prd_rslt
    
        trn_rslt = gnwNtwrkObj.get_tranche_results()
        print trn_rslt
        
        dsp_rslt = gnwNtwrkObj.get_dispatch_product_results()
        print dsp_rslt
        
        frm_rslt = gnwNtwrkObj.get_firm_profile_results()
        print frm_rslt
        
        mrkt_rslt = gnwNtwrkObj.get_market_results()
        print mrkt_rslt
        
        lp_var_vals = gnwNtwrkObj.get_lp_var_values()
        
    print "... done."

# ==============================================================================
#
#   Revision Control:
#
#   $Revision:: 6858                    $   Revision of last commit
#   $Author:: re04179                   $   Author of last commit
#   $Date:: 2010-04-16 11:42:18 +0200 (#$   Date of last commit
#
# ==============================================================================
