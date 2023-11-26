"""Interpolation utilities"""

def interp_interval(x, l=[0.0,1.0], left_open = False):
    """Given a list of strictly monotonically
    increasing numbers of at least length 2 and
    a numerical value x, this function returns
    an index tuple
    (idx-1,idx) such that l[idx-1] < x <= l[idx], if l[0] < x <= l[-1],
    (0,1) if x <= l[0], and
    (-2,-1) if x > l[-1], holds, if not left_open,
    otherwise an index tuple
    (idx-1,idx) such that l[idx-1] <= x < l[idx], if l[0] <= x < l[-1],
    (0,1) if x < l[0], and
    (-2,-1) if x >= l[-1]
    
    >>> l = [1, 3, 4, 7, 11, 18]
    >>> interp_interval(0, l)
    (0, 1)
    >>> interp_interval(1, l)
    (0, 1)
    >>> interp_interval(3.5, l)
    (1, 2)
    >>> interp_interval(11, l)
    (3, 4)
    >>> interp_interval(18, l)
    (4, 5)
    >>> interp_interval(18.2, l)
    (-2, -1)
    """
    list_len = len(l)
    if list_len == 0:
        return (None,None)
    elif list_len == 1:
        return (0,0)
    else:
        if not left_open:
            if x <= l[0]:
                return (0,1)
            elif x > l[-1]:
                return (-2,-1)
            else:
                import bisect
                idx = bisect.bisect_left(l, x)
                return (idx-1,idx)
        else:
            if x < l[0]:
                return (0,1)
            elif x >= l[-1]:
                return (-2,-1)
            else:
                import bisect
                idx = bisect.bisect_right(l, x)
                return (idx-1, idx)
            
def interp_linear(x, xList = [0.0,1.0], yList = [0.0,1.0], extrapolate = True):
    """Linear interpolation function.

    If extrapolate is True extrapolates linearly
    using the first two points in
    xList and yList, if x <= xList[0],
    using the last two points in
    xList and yList, if xList[-1] < x.
    Otherwise, returns yList[0] or yList[-1], respectively.

    >>> xList = [0.0, 1.0,  3.0,  4.0,  7.0, 11.0, 18.0]
    >>> yList = [1.0, 2.0, 10.0, 15.0, 12.0, 15.0,  8.0]
    >>> interp_linear(5.5, xList, yList)
    13.5
    >>> interp_linear(0, xList, yList)
    1.0
    >>> interp_linear(-1, xList, yList)
    0.0
    >>> interp_linear(-1, xList, yList, False)
    1.0
    >>> interp_linear(19, xList, yList)
    7.0
    >>> interp_linear(19, xList, yList, False)
    8.0
    """
    if not extrapolate:
        if x <= xList[0]:
            return yList[0]
        if x > xList[-1]:
            return yList[-1]

    t = interp_interval(x, xList)
    f = (xList[t[1]] - x)/(xList[t[1]] - xList[t[0]])
    return yList[t[0]]*f + yList[t[1]]*(1.0 - f)
    
def interp_backstep(x, xList = [0.0,1.0], yList = [0.0,1.0], extrapolate = True):
    """Backstep interpolation function

    extrapolate flag has no effect as backstep extrapolated value
    is equivalent to boundary value.

    >>> xList = [0.0, 1.0,  3.0,  4.0,  7.0, 11.0, 18.0]
    >>> yList = [1.0, 2.0, 10.0, 15.0, 12.0, 15.0,  8.0]
    >>> interp_backstep(5.5, xList, yList)
    12.0
    >>> interp_backstep(7, xList, yList)
    12.0
    >>> interp_backstep(7.0, xList, yList)
    12.0
    >>> interp_backstep(4.0, xList, yList)
    15.0
    >>> interp_backstep(0.0, xList, yList)
    1.0
    >>> interp_backstep(0.1, xList, yList)
    2.0
    >>> interp_backstep(-1.0, xList, yList)
    1.0
    >>> interp_backstep(18.0, xList, yList)
    8.0
    >>> interp_backstep(18.5, xList, yList)
    8.0
    """
    if x <= xList[0]:
        return yList[0]
    if x > xList[-1]:
        return yList[-1]

    t = interp_interval(x, xList)
    return yList[t[1]]


def interp_frontstep(x, xList = [0.0,1.0], yList = [0.0,1.0], extrapolate = True):
    """Frontstep interpolation function

    extrapolate flag has no effect as frontstep extrapolated value
    is equivalent to boundary value.

    >>> xList = [0.0,  1.0,  3.0,  4.0,  7.0, 11.0, 18.0]
    >>> yList = [1.0,  2.0, 10.0, 15.0, 12.0, 15.0,  8.0]
    >>> interp_frontstep(5.5, xList, yList)
    15.0
    >>> interp_frontstep(4.0, xList, yList)
    15.0
    >>> interp_frontstep(7.0, xList, yList)
    12.0
    >>> interp_frontstep(0.0, xList, yList)
    1.0
    >>> interp_frontstep(-1.0, xList, yList)
    1.0
    >>> interp_frontstep(18.0, xList, yList)
    8.0
    >>> interp_frontstep(18.3, xList, yList)
    8.0
    """
    if x < xList[0]:
        return yList[0]
    if x >= xList[-1]:
        return yList[-1]

    t = interp_interval(x , xList, True)
    return yList[t[0]]

if __name__ == "__main__":
    import doctest
    doctest.testmod()
