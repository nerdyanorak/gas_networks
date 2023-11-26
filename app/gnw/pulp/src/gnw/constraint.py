# ==============================================================================
#
#   package         :   GasNetWorks (gnw) Python/pulp fuelled LP/MIP modeller 
#   author          :   Marc Roth (re04179)
#   version         :   $Id: constraint.py 1860 2009-09-07 12:09:18Z re04179 $
#   heading         :   $HeadURL: http://subversion.rwe.com/svn/s_and_v_projects/GasNetworks/trunk/app/gnw/pulp/src/gnw/constraint.py $
#
#   Description     :   Package file
#
#   Creation Date   :   18May2009
#
#   Copyright       :   RWE Supply and Trading GmbH
#
# ==============================================================================
"""
gnw: ConstraintCoeff holds constraint coefficient data. 
"""

from gnw.util import isint
from gnw.util import isnumeric
from gnw.util import isstring
from gnw.util import conditional

class ConstraintCoeff( object ):
    """
    Encapsulates information on a single (multi-)period constraint
    by holding a start and end index into dispatch periods array
    (see L{gnw.entity.Entity.DISPATCH_PERIOD}), constraint type,
    boundary type, and boundary value.
    
    @ivar START: start index into
        L{gnw.entity.Entity.DISPATCH_PERIOD} array.
    @type START: L{int}
    
    @ivar FINAL: end index into
        L{gnw.entity.Entity.DISPATCH_PERIOD} array.
    @type FINAL: L{int}
    
    @ivar CTYPE: constraint type mask,
        e.g., what decision variables
        the constraint relates to/is used for.
        (see L{gnw.constraint.ConstraintCoeff.ConstraintType}
        for admissible constraint types and their values)
    @type CTYPE: L{str} 
    
    @ivar BTYPE: boundary type,
        e.g., how the L{BOUND} is used to
        constrain, i.e., from below, from above or as equality
        (see L{gnw.constraint.ConstraintCoeff.BoundaryType}
        for admissible boundary types and their values)
    @type BTYPE: L{int} 
    
    @ivar BOUND: limit value applicable to (multi-)period constraint
        given by
        [L{gnw.entity.Entity.DISPATCH_PERIOD}[t] for t in xrange( START, FINAL + 1)].
        I.e., constraints have the form
        L{pulp.LpConstraint}( L{pulp.lpSum}( [lpvar[t] t in xrange( START, FINAL + 1)] ) <op> BOUND ),
        where <op> is one of <=, ==, >= depending on L{BTYPE} and
        actual lpvar depends on value of L{CTYPE}.
    @type BOUND: L{float} 
    """
    class BoundaryType( object ):
        unknown = -1
        LB = 0
        UB = 1
        EQ = 2


    class ConstraintType( object ):
        unknown = 0
        # supplier bit masks
        POS_PCT = 2**0
        ACC_PERIOD = 2**1
        MUP_BND_PCT = 2**2
        CFW_BND_PCT = 2**3
        SPLR_NA_4 = 2**4
        SPLR_NA_5 = 2**5
        
        # storage bit masks
        LEV_PCT = 2**6
        INJ_CAP_PCT = 2**7
        REL_CAP_PCT = 2**8
        INJ_VOL_PCT = 2**9
        REL_VOL_PCT = 2**10


    def __init__(self, start = None, final = None, bound = None, btype = None, ctype = None):
        """
        @param start: start index into
            L{gnw.entity.Entity.DISPATCH_PERIOD} array.
            If not given or None then START is
            initialised to 0
        @type start: L{int} or None
        
        @param final: end index into
            L{gnw.entity.Entity.DISPATCH_PERIOD} array.
            If not given or None then FINAL is
            initialised to 0
        @type final: L{int} or None
        
        @param bound: limit value applicable to multiple dispatch period
            given by
            [L{gnw.entity.Entity.DISPATCH_PERIOD}[t] for t in xrange( start, final + 1)].
            If not given or None then BOUND is
            initialised to 0.0
        @type bound: L{float} or None
        
        @param btype: boundary type set to a value from
            L{gnw.constraint.ConstraintCoeff.ConstraintType}.
            If not given or None then BTYPE is
            initialised to L{gnw.constraint.ConstraintCoeff.BoundaryType.unknown}.
        @type btype: L{int} or None 
        
        @param ctype: constraint type bit mask combining values from class
            L{gnw.constraint.ConstraintCoeff.ConstraintType}
            If not given or None then CTYPE is
            initialised to L{gnw.constraint.ConstraintCoeff.ConstraintType.unknown}.
        @type ctype: L{int} or None
        """
        self.START = conditional( start is not None and isint( start ), start, 0 )
        self.FINAL = conditional( final is not None and isint( final ), final, 0 )
        self.BOUND = conditional( bound is not None and isnumeric( bound ), bound, 0.0 )
        self.BTYPE = conditional( btype is not None and isint( btype ), btype, ConstraintCoeff.BoundaryType.unknown )
        self.CTYPE = conditional( ctype is not None and isint( ctype ), ctype, ConstraintCoeff.ConstraintType.unknown )


    def __str__(self):
        return "%s" % self.__dict__


if __name__ == "__main__":
    print "gnw.constraint.py"

    cnstr1 = ConstraintCoeff(0, 5, 500.0, ConstraintCoeff.BoundaryType.UB,
                             ConstraintCoeff.ConstraintType.POS_PCT|ConstraintCoeff.ConstraintType.ACC_PERIOD)
    cnstr2 = ConstraintCoeff()
    
    print cnstr1.__str__()
    print cnstr2.__str__()
    
# ==============================================================================
#
#   Revision Control:
#
#   $Revision:: 1860                    $   Revision of last commit
#   $Author:: re04179                   $   Author of last commit
#   $Date:: 2009-09-07 14:09:18 +0200 (#$   Date of last commit
#
# ==============================================================================
