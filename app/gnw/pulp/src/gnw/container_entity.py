# ==============================================================================
#
#   package         :   GasNetWorks (gnw) Python/pulp fuelled LP/MIP modeller 
#   author          :   Marc Roth (re04179)
#   version         :   $Id: container_entity.py 1996 2009-09-15 07:53:36Z re04179 $
#   heading         :   $HeadURL: http://subversion.rwe.com/svn/s_and_v_projects/GasNetworks/trunk/app/gnw/pulp/src/gnw/container_entity.py $
#
#   Description     :   COM interface sub-package
#
#   Creation Date   :   13Aug2009
#
#   Copyright       :   RWE Supply and Trading GmbH
#
# ==============================================================================
"""
gnw: 'abstract' base class for GasNetWorks (gnw) entity classes
that encapsulate one or more other gnw entity class objects.
"""
from gnw.entity import Entity, FmtDictEntry
from gnw.util import dbg_print

from gnw.util import conditional

class ContainerEntity( Entity ):
    """
    Abstract base class for all GasNetWorks (gnw) entity classes
    that encapsulate one or more other gnw entity class objects.
    Typically, a entity class is sub-classed from this class
    when inter-entity relationships have to be modelled between
    the entities that the ContainerEntity class encapsulates.
    
    @ivar entity_list_dict: is a dictionary holding lists
        of entity object instance references as values having
        the object reference's classinfo as key. Therefore
        each list only holds references to class object
        instances being (direct or indirect) sub-classes
        of the type used as the dictionary entry's key.
    @type entity_list_dict:  L{dict} with classinfo as keys
        of sub-classes of L{gnw.entity.Entity} and lists
        of corresponding object instance references as
        values.
    """
    def __init__(self, name,
                 entityTypeList=[],
                 entityList=[]):
        """
        Initialises entity_list_dict. Keys are
        set to the classinfo elements given in entityTypeList
        and values are initialised with object references
        given in entityList.
        
        @param name: uniqe entity identifier
        @type name: L{str}
        
        @param entityTypeList: List of classinfo elements
        @type entityTypeList: sub-classes (direct or indirect) of
            L{gnw.entity.Entity}
            
        @param entityList: List of references to objects
            being classes, or (direct or indirect) sub-classes
            of the classinfo elements given in entityTypeList
        @type entityList: L{list} of object references of
            (direct or indirect) sub-classes of
            L{gnw.entity.Entity}
        """
        super( ContainerEntity, self ).__init__( name )
        
        self.set_entity_type_list( entityTypeList )
        self.set_entity_list( entityList )
    
    
    def set_entity_type_list(self, entityTypeList):
        """
        For each entity type given in argument
        entityTypeList adds an item to a dictionary
        with entity's instance type
        as key and an empty list as value.
        The dictionary serves two purposes:
            - Firstly, the set of its keys define
            the instance types that an object instance of class
            ContainerEntity may contain, and
            - secondly, each dictionary value will hold
            a list of references to the object instances of the
            class with key's instance type.
        
        @param entityTypeList: a list of classinfo elements
            derived from L{gnw.entity.Entity}
        @type entityTypeList: list of classinfo elements
            of being (direct or indirect) sub-classes of
            L{gnw.entity.Entity}
            
        @raise TypeError: if
            issubclass( classinfo, L{gnw.entity.Entity} )
            evaluates to False, for any of the classinfo
            elements in entityTypeList 

        @note: the client of the class is responsible
            to provide a meaningful set of classinfo
            elements in parameter entityTypeList. I.e.,
            it is not advisable that the list contains
            classinfo elements with a (direct or indirect)
            inheritance relationship. This is because
            a given object reference may be added to
            more than one dictionary entry which may
            lead to undesired results/side effects. 
        """
        self.entity_list_dict = {}
        for entity_type in entityTypeList:
            if not issubclass( entity_type, Entity ):
                raise TypeError, "Entity type '%s' is not a sub-class of of gnw.entity.Entity" % entity_type
            self.entity_list_dict[entity_type] = []
            
            
    def set_entity_list(self, entityList):
        """
        Adds class instance references provided
        in parameter entityList to appropriate entity_list_dict
        entry.
         
        @param entityList: list of Entity class instance references.
        @type entityList: (direct or indirect) instances
            of L{gwn.entity.Entity}.  
        """
        for item in entityList:
            self.add_entity( item )


    def get_entity_list(self, classinfo=Entity):
        """
        Returns a list of entity object references
        that are encapsulated by this class instance.
        
        @param classinfo: used
            as filter for object references that
            are returned by this method. All
            object references are added to the
            resulting list that are (direct or
            indirect) instances of the given
            classinfo.
        @type classinfo: classinfo or tuple of
            classinfo elements
        """
        if not issubclass(classinfo, Entity):
            raise TypeError, "parameter 'classinfo' not  a (sub-class of) 'Entity' class"

        entity_list = []
        for k,v in self.entity_list_dict.iteritems():
            if issubclass( k, classinfo ):
                entity_list += v
        return entity_list


    def add_entity(self, item):
        """
        Adds item to entity list corresponding to
        item's instance type.
        
        @param item: class instance reference 
        @type item: (direct or indirect)
            sub-class of L{gnw.entity.Entity} 
        
        @raise TypeError: item is not an instance
            of any of the types held as key's in
            the entity_list_dict.
        """
        for k,v in self.entity_list_dict.iteritems():
            if isinstance( item, k ):
                v.append( item )
                return

        raise TypeError, "Given item (%s) is not one of the admissible instance types" % item 


    def get_entity(self, name, classinfo=Entity):
        """
        Returns first entity found in entity_list_dict
        of given classinfo with matching name
        
        @param name: name of entity
        @type name: L{str}
        
        @param classinfo: type of entity
        @type classinfo: classinfo or tuple of
            classinfo elements
            
        @return: None, if not found, class reference otherwise
        
        @raise TypeError: if classinfo is not a (sub-)class
            of L{gnw.entity.Entity}
        """
        
        if not issubclass( classinfo, Entity ):
            raise TypeError, "parameter 'classinfo' not  a (sub-class of) 'Entity' class"
        
        for k,v in self.entity_list_dict.iteritems():
            if issubclass( k, classinfo ):
                for e in v:
                    if name == e.name:
                        return e
        return None   


    def set_DISPATCH_PERIOD(self, value):
        """
        Sets dispatch period in super class and
        calls L{set_DISPATCH_PERIOD} on
        all L{gnw.entity.Entity} sub-class
        instances contained in entity_list_dict.
        
        @param value: dispatch periods
        @type value: L{list} of L{float} or
            L{numpy.array} of dtype='double'
        """
        super( ContainerEntity, self ).set_DISPATCH_PERIOD( value )
        for item in self.get_entity_list():
            item.set_DISPATCH_PERIOD( value )


    def create_lp_vars(self, prefix=""):
        """
        Creates lp variables in super class and
        calls L{create_lp_vars} on
        all L{gnw.entity.Entity} sub-class
        instances contained in entity_list_dict.
        
        @param prefix: prefix string prepended to all symbolic
            lp variable names
        @type prefix: L{str}
        """
        super( ContainerEntity, self ).create_lp_vars( prefix )
        for item in self.get_entity_list():
            item.create_lp_vars( prefix )


    def create_model(self, prefix=""):
        """
        Creates lp model in super class and
        calls L{create_model} on
        all L{gnw.entity.Entity} sub-class
        instances contained in entity_list_dict.
        
        @param prefix: prefix string prepended to all symbolic
            lp variable names
        @type prefix: L{str}
        """
        super( ContainerEntity, self ).create_model( prefix )
        for item in self.get_entity_list():
            item.create_model( prefix )


    def get_lp_vars(self):
        """
        This method returns a list containing all
        lp variables including the lp variables from
        L{gnw.entity.Entity} sub-class instances
        contained in entity_list_dict.
        
        @return: list of lp variables
        @rtype: L{list} of L{pulp.LpVariable}
        """
        return super( ContainerEntity, self ).get_lp_vars() \
            + [item.get_lp_vars() for item in self.get_entity_list()]


    def get_objective(self):
        """
        Returns objective function of
        self including objective function
        terms of all entities it contains.
        
        @return: objective function.
        @rtype: L{pulp.LpAffineExpression}
        """
        objective = super( ContainerEntity, self ).get_objective()
        for item in self.get_entity_list():
            objective += item.get_objective()
        return objective


    def get_constraints(self):
        """
        Returns list of constraints of 
        self including constraints of all entities
        it contains.
        
        @return: list of constraints
        @rtype: L{list} of L{pulp.LpConstraint}
        """
        constraints = super( ContainerEntity, self ).get_constraints()
        for item in self.get_entity_list():
            constraints += item.get_constraints()
        return constraints

    
    def get_objective_value(self):
        """
        Returns affine expression of
        entity and all entities it contains,
        representing the objective value.
        
        @return: markt to market value.
        @rtype: L{pulp.LpAffineExpression}
        """
        obj = super( ContainerEntity, self ).get_objective_value()
        for item in self.get_entity_list():
            obj += item.get_objective_value()
        return obj


    def get_mark_to_market_value(self):
        """
        Returns affine expression of
        entity and all entities it contains,
        representing the mark to market value.
        
        @return: markt to market value.
        @rtype: L{pulp.LpAffineExpression}
        """
        mtm = super( ContainerEntity, self ).get_mark_to_market_value()
        for item in self.get_entity_list():
            mtm += item.get_mark_to_market_value()
        return mtm


    def write_results(self, rslt_dir, basename, extension="txt", canonical=False, sep=";", verbose=False, indent=0):
        """
        Writes results of self to file with filename
        derived from parameters rslt_dir, basename, and extension
        and calls recursively write_results on all entities it
        contains with basename = basename + "-" + self.name, if
        canonical is True, original basename, otherwise.
        Parameters verbose and indent are only used for printing
        progress messages to the console if (verbose is True).
        The progress messages are indented by indent for self
        and by indent+4 for entities self contains.
        
        @param rslt_dir: (relative or absolute) path to
            result directory location. Note directory must exist
            on file system
        @type rslt_dir: L{str}
        
        @param basename: base name of file name the results are
            written to.
        @type basename: L{str} conforming to the requirements
            of file names for given file system
            
        @param extension: filename extension
        @type extension: L{str} conforming to the requirements
             of file name extension for given file system

        @param canonical: if true the base name passed to 
            calls to write_results of entities encapsulated
            in self is extended by "-" + self.name.
        @type canonical: L{bool}
        
        @param sep: separator character to be used between elements
            in the output written
        @type sep: L{str} (typically one of '\t', '\b', ';', ':', ',', etc.)
  
        @param verbose: whether progress messages are printed to the console
        @type verbose: L{bool}
        
        @param indent: indentation of progress messages in number of characters.
        @type indent: L{int}     
        """
        super( ContainerEntity, self).write_results( rslt_dir,
                                                     basename = basename,
                                                     extension = extension,
                                                     canonical = canonical,
                                                     sep = sep,
                                                     verbose = verbose,
                                                     indent = indent )
        
        indent += 4
        dbg_print( "%s... entities of '%s'" % (" "*indent, self.name) , verbose )
        
        for entity in self.get_entity_list():
            entity.write_results( rslt_dir,
                                  basename = conditional( canonical,
                                                          "%s-%s" % (basename, self.name),
                                                          basename ),
                                  extension = extension,
                                  canonical = canonical,
                                  sep = sep,
                                  verbose = verbose,
                                  indent = indent + 4 )


if __name__ == "__main__" :
    print "gnw.container_entity.py"
    
# ==============================================================================
#
#   Revision Control:
#
#   $Revision:: 1996                    $   Revision of last commit
#   $Author:: re04179                   $   Author of last commit
#   $Date:: 2009-09-15 09:53:36 +0200 (#$   Date of last commit
#
# ==============================================================================
