if __name__ == "__main__":
    from math import sin, pi
    from pulp import *
    
    nSteps = 12
    dT = 24.0
    DISPATCH_PERIODS = [dT]*nSteps
#    print DISPATCH_PERIODS


    # Discount factor curve generation 
    DISCOUNT_FACTOR = 1.0

    # Synthetic forward curve generation     
    basePrice = 25.0
    bidAskSprdPct = 0.05
  
    FWD_CURVE_MID = [round(basePrice + sin(2.0*pi*t/(nSteps-1)), 3) for t in xrange( nSteps )]
    print FWD_CURVE_MID
    FWD_CURVE_BID = [round(FWD_CURVE_MID[t]*(1.0 - bidAskSprdPct/2.0), 3) for t in xrange( nSteps)]
    print FWD_CURVE_BID
    FWD_CURVE_ASK = [round(FWD_CURVE_MID[t]*(1.0 + bidAskSprdPct/2.0), 3) for t in xrange( nSteps)]
    print FWD_CURVE_ASK
    












