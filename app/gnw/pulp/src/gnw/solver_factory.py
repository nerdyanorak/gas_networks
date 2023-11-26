# ==============================================================================
#
#   package         :   GasNetWorks (gnw) Python/pulp fuelled LP/MIP modeller 
#   author          :   Marc Roth (re04179)
#   version         :   $Id: solver_factory.py 9768 2010-09-22 20:07:23Z re04179 $
#   heading         :   $HeadURL: http://subversion.rwe.com/svn/s_and_v_projects/GasNetworks/trunk/app/gnw/pulp/src/gnw/solver_factory.py $
#
#   Description     :   Package file
#
#   Creation Date   :   20Mar2009
#
#   Copyright       :   RWE Supply and Trading GmbH
#
# ==============================================================================
"""
gnw: Solver factory class
"""

import pulp
import gnw.pulp_patches
from gnw.xpress_opts_adapter import XpressOptsAdapter
from gnw.solver_check import SolverCheck

class SolverFactory:
    """
    """
    solver_by_name = {'COIN_MEM'               : pulp.COIN_MEM,
                      'COIN_CMD'               : pulp.COIN_CMD,
                      'CPLEX_MEM'              : pulp.CPLEX_MEM,
                      'CPLEX_CMD'              : pulp.CPLEX_CMD,
                      'GLPK_MEM'               : pulp.GLPK_MEM,
                      'GLPK_CMD'               : pulp.GLPK_CMD,
                      'LP_SOLVE'               : pulp.LP_SOLVE,
                      'XPRESS'                 : pulp.XPRESS,
                      'XPRESS_REMOTE_CLIENT'   : pulp.XPRESS_REMOTE_CLIENT,
                      'XPRESS_SERVICE_CLIENT'  : pulp.XPRESS_SERVICE_CLIENT}

    def create(solver_dict):
        """
        @return: solver instance
        @rtype: L{pulp.LpSolver}
        """
        if len( solver_dict ) == 0:
            return pulp.LpSolverDefault
            
        solver = None
        if not SolverCheck.check_dict( solver_dict ):
            raise ValueError, "parameter 'solver_dict' failed consistency check"

        solverType = SolverFactory.solver_by_name[solver_dict['name']]

        # Extract optional parameters that are
        # common to all pulp solvers
        mip = 1
        if 'mip' in solver_dict:
            mip = solver_dict['mip']
            
        msg = 1
        if 'msg' in solver_dict:
            msg = solver_dict['msg']
            
        options = []
        if 'options' in solver_dict:
            options = solver_dict['options']

        # Depending on (in-)direct superclass 
        # of given solver, arguments to __init__ method
        # may vary 
        if issubclass( solverType, pulp.LpSolver_CMD ):
            
            # Extract additional optional arguments
            # common to all solvers derived from
            # pulp.LpSolver_CMD
            path = None
            if 'path' in solver_dict:
                path = solver_dict['path']
                 
            keepFiles = 1
            if 'keepFiles' in solver_dict:
                keepFiles = solver_dict['keepFiles']

            if issubclass( solverType, pulp.XPRESS_SERVICE_CLIENT ):
                attr_dict = solver_dict['attr']     # must have a 'attr' entry
                mode = attr_dict['MODE']            # must have a 'MODE' attribute
                del attr_dict['MODE']               # remove it from attr dictionary
                pedantic = False
                params = XpressOptsAdapter.get_opt_control_string( attr_dict, pedantic )
                solver = solverType( optcontrol=params, optimisationMode=mode )

            elif issubclass( solverType, pulp.XPRESS_REMOTE_CLIENT ):
            
                attr_dict = solver_dict['attr']     # must have a 'attr' entry
                url = attr_dict['URL']
                del attr_dict['URL']
                pedantic = False
                params = XpressOptsAdapter.get_opt_control_string( attr_dict, pedantic )
                solver = solverType( path = path,
                                     keepFiles = keepFiles,
                                     mip = mip,
                                     msg = msg,
                                     options = options,
                                     str_url = url,
                                     str_params = params )

            else:

                solver = solverType( path = path,
                                     keepFiles = keepFiles,
                                     mip = mip,
                                     msg = msg,
                                     options = options )
                
        elif issubclass( solverType, pulp.LpSolver ):
            
            solver = solverType( mip = mip,
                                 msg = msg,
                                 options = options )
            
        else:
            # we shouldn't get here ever, as all pulp solvers are derived (in-)directly from pulp.LpSolver
            raise TypeError, "solver type is not a subclass of %s or %s" % (pulp.LpSolver_CMD, pulp.LpSolver)

        return solver

    create = staticmethod( create )
    
    
if __name__ == "__main__":
    print "gnw.solver_factory.py"

# ==============================================================================
#
#   Revision Control:
#
#   $Revision:: 9768                    $   Revision of last commit
#   $Author:: re04179                   $   Author of last commit
#   $Date:: 2010-09-22 22:07:23 +0200 (#$   Date of last commit
#
# ==============================================================================
