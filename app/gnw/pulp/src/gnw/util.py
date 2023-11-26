# ==============================================================================
#
#   package         :   GasNetWorks (gnw) Python/pulp fuelled LP/MIP modeller 
#   author          :   Marc Roth (re04179)
#   version         :   $Id: util.py 1860 2009-09-07 12:09:18Z re04179 $
#   heading         :   $HeadURL: http://subversion.rwe.com/svn/s_and_v_projects/GasNetworks/trunk/app/gnw/pulp/src/gnw/util.py $
#
#   Description     :   Package file
#
#   Creation Date   :   06Mar2009
#
#   Copyright       :   RWE Supply and Trading GmbH
#
# ==============================================================================
"""
gnw: utility functions

Quite possibly such utilities do already exist
in Python or some package/module but my ignorance
prevents to find/use them.
"""
import sys

isint = lambda x : isinstance( x, int )
isfloat = lambda x : isinstance( x, float )

isarray = lambda x : isinstance( x, numpy.ndarray )
islist =  lambda x : isinstance( x, list )
istuple = lambda x : isinstance( x, tuple )
isbuffer = lambda x : isinstance( x, buffer )
isrange = lambda x : isinstance( x, xrange )
isstring = lambda x : isinstance( x, (str,unicode) )

isnumeric = lambda x : isinstance( x, (int,float) )
isempty = lambda x : x is None or x == ""
isnumericorempty = lambda x : isnumeric(x) or isempty(x)
issequence = lambda x : isinstance( x, (str,unicode,list,tuple,buffer,xrange) )


def conditional(cond, iftrue, iffalse):
    """
    Conditional function returning L{iftrue} if L{cond} is L{True},
    returning L{iffalse}, otherwise.
    
    @param cond: expression evaluating to L{True} or L{False}
    @type cond: L{bool}
    @param iftrue: return value if L{cond}
    @param iffalse: return value if not L{cond}
    
    @return: L{iftrue} or L{iffalse}
    """
    if cond:
        return iftrue
    else:
        return iffalse


def dbg_print(message, verbose=False, file=None):
    if verbose:
        print >> file, message
        if file is None:
            sys.stdout.flush()



if __name__ == "__main__":
    print "gnw.util.py"
     
# ==============================================================================
#
#   Revision Control:
#
#   $Revision:: 1860                    $   Revision of last commit
#   $Author:: re04179                   $   Author of last commit
#   $Date:: 2009-09-07 14:09:18 +0200 (#$   Date of last commit
#
# ==============================================================================
