import cStringIO
import SOAPpy.WSDL
import gzip
import base64
from pulp.solvers import XPRESS, LpSolver_CMD
import pulp.rwest_solvers
from pulp.constants import LpStatusNotSolved, LpStatusOptimal, LpStatusInfeasible, LpStatusUnbounded, LpStatusUndefined

def XPRESS_REMOTE_CLIENT__init__(self,
                                 path=None, keepFiles=0,  
                                 mip=1, msg=1, options=[],
                                 str_url='http://xpressprod.rwe.com:8080/csgb-xpress/services/XpressExecutionServer?wsdl',
                                 mip_rel_cutoff=1.0e-4, mip_rel_stop=0.0, timeLimit=0, 
                                 str_params=""):
    """ Used to 'overwrite' L{pulp.rwest_solvers.XPRESS_REMOTE_CLIENT.__init__}
    method, until patch from package developer is available.
    
    @param path: path to temporary directory to be used. If equal to
        None class attempts to derive location from common environment
        variables like 'TMP', 'TEMP', 'TMPDIR' or 'TEMPDIR' 
    @type path: L{str} or None
    
    @param keepFiles: flag whether intermediary files should be kept
    @type keepFiles: L{bool}
    
    @param mip: flag whether problem has to be solved as MIP
    @type mip: L{bool}
    
    @param msg:
    @type msg: L{bool} 
    
    @param options: list of additional option strings to be passed to underlying solver
    @type options: L{list} of L{str}
    
    @param str_url: url of the wsdl
    @type str_url: L{str}
    
    @param mip_rel_cutoff: (deprecated, see str_params)
    @type mip_rel_cutoff: L{double} >= 0.0
    
    @param mip_rel_stop: (deprecated, see str_params)
    @type mip_rel_stop: L{double} >= 0.0
    
    @param timeLimit: (deprecated, see str_params)
    @type timeLimit: L{int} >= 0
    
    @param str_params: control parameter string. The string has the form
        <controlId_1>=<controlValue_1>[;<controlId_2>=<controlValue_2>[...]],
        where
            - <controlId_n> is a numeric string representing the control
            parameter to be set, and
            - <controlValue_n> is the corresponding value given as string
        In order to simplify the creation this input helper class
        L{gnw.xpress_opts_adapter.XpressOptsAdapter} is provided
    @type str_params: L{str} 
    """
    XPRESS.__init__( self,
                     path = path,
                     keepFiles = keepFiles,
                     mip = mip,
                     msg = msg,
                     options = options )
    self.server = SOAPpy.WSDL.Proxy( str_url )
    self.mip_rel_cutoff = mip_rel_cutoff
    self.mip_rel_stop = mip_rel_stop
    self.timeLimit = timeLimit
    self.params = str_params

pulp.rwest_solvers.XPRESS_REMOTE_CLIENT.__init__ = XPRESS_REMOTE_CLIENT__init__


def XPRESS_REMOTE_CLIENTactualSolve(self, lp) :
        """Solve a well formulated LP problem
        
        @param lp: reference to LP
        @type lp: L{pulp.LpProblem}  
        
        @return: problem status
        @rtype: L{int}
        """

        mem_file = cStringIO.StringIO()
        # write the lp file to a string
        lp.writeLP(mem_file, writeSOS = 1, mip = self.mip)
        lp_string = mem_file.getvalue()
        mem_file.close()
        del mem_file
        lp_name = lp.name + ".lp"

        request = {'OPTCONTROL' : self.params,
                   'problemFile' : lp_string,
                   'problemFileName' : lp_name}
        
        if lp.isMIP() :
            request.update( {'MIPRELCUTOFF' : self.mip_rel_cutoff,   # only kept for backwards compatibility
                             'MIPRELSTOP' : self.mip_rel_stop,
                             'MAXTIME' : self.timeLimit} )
            result = self.server.executeMIP( request )
        else :
            result = self.server.executeLP( request )

        # the result is stored as base64 encoded zipfile in resultFile
        # if problemStatus is -1 we are in trouble. Very likely the result file
        # is garbage. Best we can do is assume the problem was infeasible.
        lp.status = self.STATUS_MAP[(result.problemStatus,lp.isMIP())]
        if lp.status not in [ LpStatusInfeasible, LpStatusNotSolved, LpStatusUnbounded ] :
            mem_file = gzip.GzipFile( mode='r', fileobj=cStringIO.StringIO( base64.decodestring( result['resultFile'] ) ) )
            ignore, values = self.readsol( mem_file )
            mem_file.close()
            del mem_file
            lp.assignVarsVals(values)
            
        return lp.status

pulp.rwest_solvers.XPRESS_REMOTE_CLIENT.actualSolve = XPRESS_REMOTE_CLIENTactualSolve


def LP_SOLVE__init__(self, timeLimit=0, path=None, keepFiles=0, mip=1, msg=1, options=[]):
    """Adapt initialisation function to have at least the same named arguments
    as its parent class' LpSolver_CMD initialisation function in order to allow
    factory to initialise class objects using base class' 'constructor'
    """
    LpSolver_CMD.__init__( self, path=path, keepFiles=keepFiles, mip=mip, msg=msg, options=options )
    self.timeLimit = timeLimit

pulp.rwest_solvers.LP_SOLVE.__init__ = LP_SOLVE__init__ 
