"""L{Entity}: The base object of all Gas Network entities"""
import pulp
import numpy
from utils.util import isnumeric
 
class Entity(object):
    """
    Gas Network framework base class.
    
    L{Entity} implements the basic attributes and
    methods for all objects under control of the
    framework.
    In its most simple form a gas network entity,
    as implemented in this class, has an inflow and
    and an outflow variable for each dispatch period t,
    The inflow and outflow variables must relate to
    each other in a balance type constraint, such as
        - in_flow(t) == out_flow(t), for all t
    As derived classes may want to implement more
    complicated balance constraints, no such
    balance constraint is enforced in this base class.
     
    Each entity e object links to zero or more entity
    source objects (src) and to zero or more entity sink
    objects (snk) with conditions
        - sum(src[i].out_flow(t), i in srcs) == e.in_flow(t), and
        - sum(snk[i].in_flow(t), i in snks) == e.out_flow(t), for all t
    
    @ivar name:            is the unique name of the object.\
    Will be used to prefix the LP variables.
    @type name:            L{str}
    @ivar constraint_list:      constraints owned by this L{Entity}
    @type constraint_list:      [L{pulp.LpConstraint}]
    @ivar objective_list:   objective (constraints) owned by this L{Entity}
    @type objective_list:   [L{pulp.LpAffineExpression}]
    @ivar DISPATCH_PERIODS: see L{setDISPATCH_PERIODS}
    @type DISPATCH_PERIODS: L{numpy.ndarray} of dtype='double'
    @ivar srcList:         List of source L{Entity} objects
    @type srcList:         [L{Entity}]
    @ivar snkList:         List of sink L{Entity} objects
    @type snkList:         [L{Entity}]
    @ivar in_flow:          inflow variables of the L{Entity} in [MWh]\
    for all t in L{DISPATCH_PERIODS}
    @type in_flow:          [L{numpy.ndarray} of dtype='object'\
    where object is L{pulp.LpVariable}
    @ivar out_flow:         outflow variables of the L{Entity} in [MWh]\
    for all t in L{DISPATCH_PERIODS}
    @type out_flow:          [L{numpy.ndarray} of dtype='object'\
    where object is L{pulp.LpVariable}   
    """ 
    def __init__(self,
                 name,
                 srcs = [],
                 snks = []):
        """
        @param name:        uniqe, non-empty name string of entity
        @type name:         L{str}
        @param srcs:        source entity object
        @type srcs:         [L{Entity}]
        @param snks:        sink entity object
        @type snks:         [L{Entity}]
        """
        self.set_name( name )
        
        self.constraint_list = []
        self.objective_list = []
        
        self.set_src_list( srcs ) 
        self.set_snk_list( snks )
        
        self.DISPATCH_PERIODS = numpy.array( [], dtype='double' )
        self.in_flow = numpy.empty( 0, dtype='object' )
        self.out_flow = numpy.empty( 0, dtype='object' )

    def create_coefficient_array(member_array, size, message):
        if isinstance( member_array, numpy.ndarray ):
            if len( member_array ) != size:
                raise ValueError, message
        elif isinstance( member_array, list ):
            if len( member_array ) != size:
                raise ValueError, message
            else:
                member_array = numpy.array( member_array, dtype='double' )
        elif isnumeric( member_array ):
            member_array = numpy.array( [member_array]*size, dtype='double' )
        else:
            raise ValueError, message

        return member_array
        
    create_coefficient_array = staticmethod(create_coefficient_array)
    
    def set_DISPATCH_PERIODS(self, value):
        """
        The length of the dispatchPeriods + 1 will be the number
        of time steps in the optimisation.
        The time grid need not be uniform.
        
        @param value: length of the individual dispatch periods in hours.
        @type value: L{numpy.ndarray} of dtype='double'
        """
        self.DISPATCH_PERIODS = value


    def set_name(self, value):
        if not isinstance(value, str):
            raise ValueError, "Name of Entity object must be string"
        if len(value) == 0:
            raise ValueError, "Name of Entity object can not be empty string"
        self.name = value


    def set_src_list(self, value):
        self.src_list = []
        for src in value:
            self.append_to_src_list(src)

    
    def set_snk_list(self, value):
        self.snk_list = []
        for snk in value:
            self.append_to_snk_list(snk)


    def append_to_src_list(self, src):
        """
        If the src L{Entity} is not yet part of
        the L{srcList} and the L{name} is unique
        then add the src to the L{srcList} and add
        myself  to the src's L{snkList}.
        """
        if isinstance(src, Entity):
            if src not in self.src_list:
                if src.name in [item.name for item in self.src_list]:
                    raise ValueError, "Non-unique name for source entity '%s'" % src.name 
                self.src_list.append(src)
                src.append_to_snk_list(self)

            
    def append_to_snk_list(self, snk):
        """
        If the snk L{Entity} is not yet part of
        the L{snkList} and the L{name} is unique
        then add the snk to the L{snkList} and add
        myself to the snk's L{srcList}.  
        """
        if isinstance(snk, Entity):
            if snk not in self.snk_list:
                if snk.name in [item.name for item in self.snk_list]:
                    raise ValueError, "Non-unique name for sink entity '%s'" % snk.name
                self.snk_list.append(snk)
                snk.append_to_src_list(self)
    

    def create_lp_vars(self, prefix=""):
        """
        """
        nSteps = len( self.DISPATCH_PERIODS )
        
        self.in_flow  = numpy.array( pulp.LpVariable.matrix( prefix + self.name + "_iflow", range( nSteps ), lowBound = 0.0 ) )
        self.out_flow = numpy.array( pulp.LpVariable.matrix( prefix + self.name + "_oflow", range( nSteps ), lowBound = 0.0 ) )

    
    def create_model(self, prefix=""):
        """
        """
        self.constraint_list = []
        self.objective_list = []
        
        nSteps = len( self.DISPATCH_PERIODS )
        
        if len( self.src_list ) > 0:
            for t in xrange( nSteps ):
                # The inflow to self cannot be larger than the
                # sum of the outflows from the sources.
                self.constraint_list.append( pulp.lpSum( [src.out_flow[t] for src in self.src_list] ) >= self.in_flow[t] )
            
        if len( self.snk_list ) > 0:
            for t in xrange( nSteps ):
                # The outflow from self cannot be larger than the
                # sum of the inflows to the sinks.
                self.constraint_list.append( pulp.lpSum( [snk.in_flow[t] for snk in self.snk_list] ) >= self.out_flow[t] )

        if len( self.src_list ) == 0 and len( self.snk_list ) > 0:
            # Prevent inflow being unbounded from above
            for t in xrange( nSteps ):
                self.constraint_list.append( self.in_flow[t] == 0.0 )
        if len( self.snk_list ) == 0 and len( self.src_list ) > 0:
            # Prevent outflow being unbounded from above
            for t in xrange( nSteps ):
                self.constraint_list.append( self.out_flow[t] == 0.0 )
                

    def get_lp_vars(self):
        """
        """
        return self.in_flow.tolist() +  self.out_flow.tolist()        
    
    
    def get_topology_graph(self):
        """
        L{edges} keys have the form  (self.name,snk.name) or (src.name,self.name)
        L{edges} values hav the form key[0] + " -> " + key[1]
        L{visited} is a list of L{Entity} object references 
        """
        edges = {}
        visited = []
        edges = self.get_topology_edges( visited, edges )
        
        graph = "digraph \"Topology\" {\n"
        for key, value in edges.iteritems():
            graph += "\t" + value + ";\n"
            
        graph += "}\n"
        
        return graph
    
    def get_topology_edges(self, visited = [], edges = {} ):
        visited += [ self ]
        for src in self.src_list:
            if src not in visited:
                key = (src.name, self.name)
                if key not in edges:
                    edges[key] = "\"" + src.name + "\" -> \"" + self.name + "\""
        for snk in self.snk_list:
            if snk not in visited:
                key = (self.name, snk.name)
                if key not in edges:
                    edges[key] = "\"" + self.name + "\" -> \"" + snk.name + "\""
        
        for src in self.src_list:
            if src not in visited:
                src.get_topology_edges( visited, edges )
        for snk in self.snk_list:
            if snk not in visited:
                snk.get_topology_edges( visited, edges )
        
        return edges
        
    
