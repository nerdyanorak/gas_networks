"""
Utility functions that come in handy.

Quite possibly such utilities do already exist
in Python or some package/module but my ignorance
prevents to find/use them.
"""

isnumeric = lambda x : isinstance( x, (int,float) )



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
