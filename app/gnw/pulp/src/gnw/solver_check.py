# ==============================================================================
#
#   package         :   GasNetWorks (gnw) Python/pulp fuelled LP/MIP modeller 
#   author          :   Marc Roth (re04179)
#   version         :   $Id: solver_check.py 9768 2010-09-22 20:07:23Z re04179 $
#   heading         :   $HeadURL: http://subversion.rwe.com/svn/s_and_v_projects/GasNetworks/trunk/app/gnw/pulp/src/gnw/solver_check.py $
#
#   Description     :   Package file
#
#   Creation Date   :   20Mar2009
#
#   Copyright       :   RWE Supply and Trading GmbH
#
# ==============================================================================
"""
gnw: Utility to check validity of solver parameter dictionary
"""

from gnw.util import isstring, isint, isfloat
from gnw.xpress_opts_adapter import XpressOptsAdapter

class SolverCheck( object ):
    """
    Utility to check validity of solver parameter dictionary
    passed as a named item (ni) tuple to
    L{gnw.com.network.COM_Network.set_solver}
    
    Usage:
        - SolverCheck.check_dict( solver_dict )
    """
    # Is there a way to extract those solver
    # strings programmatically from the pulp module?
    solvers = ('COIN_MEM', 'COIN_CMD',
               'CPLEX_MEM', 'CPLEX_CMD',
               'GLPK_MEM', 'GLPK_CMD',
               'LP_SOLVE',
               'XPRESS', 'XPRESS_REMOTE_CLIENT', 'XPRESS_SERVICE_CLIENT')

    def check_dict(solver_dict = {}):
        """
        Checks given L{solver_dict} for validity.
        
        @param solver_dict: solver parameter dictionary.
            The dictionary must contain a key 'name' with
            corresponding L{str} value equal to one of
            L{solvers}. Potentially a key 'attr' with
            corresponding value of type L{dict} (@see: 
            L{check_attr_dict} for details on the
            attribute dictionary. 
        @type solver_dict: L{dict}
        
        @return: L{True} or L{False}
        @rtype: L{bool}
        """
        if len( solver_dict ) == 0:
            # empty solver dict is OK, pulp.LpSolverDefault will be used
            return 1
         
        if not 'name' in solver_dict:
            return 0
        name = solver_dict['name']
        if not isstring( name ):
            return 0
        if not name in SolverCheck.solvers:
            return 0
        if 'attr' in solver_dict:
            return SolverCheck.check_attr_dict( name, solver_dict['attr'] )
        
        return 1
    
    check_dict = staticmethod( check_dict )


    def check_attr_dict(name, solver_attr_dict = {}):
        """
        Checks given attribute dictionary L{solver_attr_dict}
        for validity.
        
        @param name: Solver name from L{gnw.solver_check.SolverCheck.solvers}.
        @type name: L{str}
        
        @param solver_attr_dict: solver attribute dictionary
            (@see: methods L{check_XPRESS_REMOTE_CLIENT_attr}
            and L{check_XPRESS_attr} for details).
        @type solver_attr_dict: L{dict}
        
        @return: L{True} or L{False}
        @rtype: L{bool}   
        """
        if name == 'XPRESS_SERVICE_CLIENT':
            return SolverCheck.check_XPRESS_SERVICE_CLIENT_attr( solver_attr_dict )
        elif name == 'XPRESS_REMOTE_CLIENT':
            return SolverCheck.check_XPRESS_REMOTE_CLIENT_attr( solver_attr_dict )
        elif name == 'XPRESS':
            return SolverCheck.check_XPRESS_attr( solver_attr_dict )        
        else:
            return 1
    
    check_attr_dict = staticmethod( check_attr_dict )
    
    
    def check_XPRESS_attr(solver_attr_dict = {}, additional_attr_dict = {}):
        """
        Checks given L{solver_attr_dict} attribute dictionary
        for validity, given that solver is L{pulp.XPRESS}.
        
        @param solver_attr_dict: well formed solver attribute dictionary.
        @type solver_attr_dict: L{dict}
        @param additional_attr_dict: well formed solver attribute dictionary
            to be used to extend admissible dictionary entries.
        @type additional_attr_dict: L{dict}
        
        @return: L{True} or L{False}
        @rtype: L{bool}   
        """
        XPRESS_attr_dict = {}
        XPRESS_attr_dict.update( additional_attr_dict )
        
        # Check whether given attribute key is
        # in XPRESS attribute dict and value has
        # got the correct type
        for k,v in solver_attr_dict.iteritems():
            if not k in XpressOptsAdapter.opt_control_dict and not k in XPRESS_attr_dict:
                return 0
            else:
                if k in XpressOptsAdapter.opt_control_dict:
                    if not XpressOptsAdapter.opt_control_dict[k][2]( v ):
                        return 0
                if k in XPRESS_attr_dict:
                    if not XPRESS_attr_dict[k][0]( v ):
                        return 0
                    
        # Check whether all mandatory XPRESS attributes
        # have been provided
        for k,v in XPRESS_attr_dict.iteritems():
            if v[1] and not k in solver_attr_dict:
                return 0
            
        return 1
            
    check_XPRESS_attr = staticmethod( check_XPRESS_attr )


    def check_XPRESS_REMOTE_CLIENT_attr(solver_attr_dict = {}):
        """
        Checks given L{solver_attr_dict} attribute dictionary
        for validity, given that solver is L{pulp.XPRESS_REMOTE_CLIENT}.
        
        @param solver_attr_dict: well formed solver attribute dictionary.
        @type solver_attr_dict: L{dict}
        
        @return: L{True} or L{False}
        @rtype: L{bool}   
        """
        XPRESS_REMOTE_CLIENT_attr_dict = { 'URL' : (isstring, True) }
        
        return SolverCheck.check_XPRESS_attr( solver_attr_dict, XPRESS_REMOTE_CLIENT_attr_dict )
    
    check_XPRESS_REMOTE_CLIENT_attr = staticmethod( check_XPRESS_REMOTE_CLIENT_attr )


    def check_XPRESS_SERVICE_CLIENT_attr(solver_attr_dict = {}):
        """
        Checks given L{solver_attr_dict} attribute dictionary
        for validity, given that solver is L{pulp.XPRESS_SERVICE_CLIENT}.
        
        @param solver_attr_dict: well formed solver attribute dictionary.
        @type solver_attr_dict: L{dict}
        
        @return: L{True} or L{False}
        @rtype: L{bool}   
        """
        XPRESS_SERVICE_CLIENT_attr_dict = { 'MODE' : (isstring, True) }
        
        return SolverCheck.check_XPRESS_attr( solver_attr_dict, XPRESS_SERVICE_CLIENT_attr_dict )
    
    check_XPRESS_SERVICE_CLIENT_attr = staticmethod( check_XPRESS_SERVICE_CLIENT_attr )


if __name__ == "__main__":
    print "gnw.solver_check.py"

# ==============================================================================
#
#   Revision Control:
#
#   $Revision:: 9768                    $   Revision of last commit
#   $Author:: re04179                   $   Author of last commit
#   $Date:: 2010-09-22 22:07:23 +0200 (#$   Date of last commit
#
# ==============================================================================
