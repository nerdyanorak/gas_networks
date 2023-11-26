"""
Test A.1: Simple standalone storage test

The topology of this gas network is
    - dispatch period daily for one year ([24]*365)
    - simple storage standalone
    - discount factor is 1.0
    - daily forward curve, represented by vectors
    of daily bid and ask prices
    having sinusodial shape. 
"""

if __name__ == "__main__":
    from entity import Entity
    from storage import Storage
    from math import sin, cos, pi, exp
    from pulp import *
    import os
    
#    prefix = "A_1"
    problemName = os.path.splitext( os.path.basename( __file__ ) )[0]
    prefix = ""
       
#    nSteps = 365
    nSteps = 12
    dT = 24.0
    DISPATCH_PERIODS = [dT]*nSteps
#    print DISPATCH_PERIODS


    # Discount factor curve generation 
#    DISCOUNT_FACTOR = 1.0
    DISCOUNT_FACTOR = [exp(-0.03*t*24.0/365.0/dT) for t in xrange( nSteps )]

    # Synthetic forward curve generation     
    basePrice = 25.0
    bidAskSprdPct = 0.02
  
    FWD_CURVE_MID = [round(basePrice + cos(2.0*pi*t/(nSteps)), 3) for t in xrange( nSteps )]
    FWD_CURVE_BID = [round(FWD_CURVE_MID[t]*(1.0 - bidAskSprdPct/2.0), 3) for t in xrange( nSteps)]
    FWD_CURVE_ASK = [round(FWD_CURVE_MID[t]*(1.0 + bidAskSprdPct/2.0), 3) for t in xrange( nSteps)]
    print FWD_CURVE_BID
    print FWD_CURVE_MID
    print FWD_CURVE_ASK
    
    
    # Storage Entity
    nominalInjectionCapacity = 400.0 # [MW/h]  24*400=9600 [MW/d]
    nominalReleaseCapacity = 300.0 # [MW/h]
    nominalWorkingGasVolume = min(1.0e6, 0.75*nSteps*24.0*nominalInjectionCapacity) # [MWh] WGV
    startStorageLevelPct = 0.0  # percentage of WGV
    endStorageLevelPct = None # percentage of WGV
    maxStorageLevelPct = 1.0 # percentage of WGV
    minStorageLevelPct = 0.0 # percentage of WGV
    maxInjectionCapacityPct = 1.0 # percentage of nominalInjectionCapacity
    maxReleaseCapacityPct = 1.0 # percentage of nominalReleaseCapacity
    injectionCost = 0.2 # [EUR/MWh]
    releaseCost = 0.05 # [EUR/MWh]
    discountFactor = DISCOUNT_FACTOR
    fwdCurveBid = FWD_CURVE_BID
    fwdCurveAsk = FWD_CURVE_ASK
    
    print "Storage Inputs:"
    print "-----------------------------------------------"
    print "nominalInjectionCapacity: ", nominalInjectionCapacity
    print "nominalReleaseCapacity: ", nominalReleaseCapacity
    print "nominalWorkingGasVolume: ", nominalWorkingGasVolume
    print "startStorageLevelPct: ", startStorageLevelPct
    print "endStorageLevelPct: ", endStorageLevelPct
    print "maxStorageLevelPct: ", maxStorageLevelPct
    print "minStorageLevelPct: ", minStorageLevelPct
    print "maxInjectionCapacityPct: ", maxInjectionCapacityPct
    print "maxReleaseCapacityPct: ", maxReleaseCapacityPct
    print "injectionCost: ", injectionCost
    print "releaseCost: ", releaseCost
    print "discountFactor: ", discountFactor
    print "fwdCurveBid: ", fwdCurveBid
    print "fwdCurveAsk: ", fwdCurveAsk
    
    storage = Storage( "strg_0",
                       nominalWorkingGasVolume,
                       nominalInjectionCapacity,
                       nominalReleaseCapacity,
                       startStorageLevelPct,
                       endStorageLevelPct,
                       maxStorageLevelPct,
                       minStorageLevelPct,
                       maxInjectionCapacityPct,
                       maxReleaseCapacityPct,
                       injectionCost,
                       releaseCost,
                       discountFactor,
                       fwdCurveBid,
                       fwdCurveAsk )

    # Un-comment the following two lines
    # to get a dot-graph representation
    # of the gas network set-up above
    # Copy print output into text file
    # 'dotgraph.txt' and run on the
    # command line
    # dot -Tjpg dotgraph.txt -o dotgraph.jpg
    # to create a jpg graphical representation
    # of the graph. 
    graph = storage.get_topology_graph()
    print graph

    storage.set_DISPATCH_PERIODS(DISPATCH_PERIODS)
        
    storage.create_lp_vars( prefix )

    storage.create_model( prefix )

    # Get (objective) constraints
    objective_list = []
    objective_list += storage.objective_list
    objective = pulp.LpAffineExpression( constant = 0 )
    for item in objective_list:
        objective += item

    constraint_list = []
    constraint_list += storage.constraint_list

    # Create lp problem and add (objective) constraints
    lp = pulp.LpProblem( problemName , pulp.LpMaximize )
    lp += objective
    for constraint in constraint_list:
        lp += constraint 
    
    pulp.LpSolverDefault.keepFiles = True
#    pulp.pulpTestAll()

    lp.writeLP( "c:\\temp\\" + problemName + ".lp" )
    lp.writeMPS("c:\\temp\\" + problemName + ".mps")
 
#    lp.solve()   
#    lp.solve(pulp.GLPK_CMD())
    lp.solve(pulp.COINMP_DLL())

    print "Objective =", value(lp.objective)
    print "%15s; %15s; %15s; %15s" % ("t", "lev[t] [%]", "inj[t] [%]", "rel[t] [%]")
    for t in xrange( nSteps + 1):
        lev_pct = storage.name + "_lev_pct_%d" % t 
        q_inj = storage.name + "_q_inj_pct_%d" % t
        q_rel = storage.name + "_q_rel_pct_%d" % t
        if t < nSteps:
            print "%15d; %15.12f; %15.12f; %15.12f"%(t, lp.variablesDict()[lev_pct].varValue, lp.variablesDict()[q_inj].varValue, lp.variablesDict()[q_rel].varValue)
        else:
            print "%15d; %15.12f; %15s; %15s"%(t, lp.variablesDict()[lev_pct].varValue, "", "")
