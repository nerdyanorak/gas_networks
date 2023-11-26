"""
Test A.1: Simple storage and market test

The topology of this gas network is
    - dispatch period daily for one year ([24]*365)
    - simple storage linked to
        - buy market as as sink
        - sell market as a source
    - buy market linked to storage as source
    - sell market linked to storage as sink
    - discount factor is 1.0
    - daily forward curve, represented by vectors
    of daily bid and ask prices having sinusodial shape. 
"""

if __name__ == "__main__":
    from entity import Entity
    from storage import Storage
    from market import Market
    from math import sin, cos, pi, exp
    from pulp import *
    
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
    nominalWorkingGasVolume = min(1.0e6, 0.75*24.0*nSteps*nominalInjectionCapacity) # [MWh] WGV
    startStorageLevelPct = 0.0  # percentage of WGV
    endStorageLevelPct = None # percentage of WGV
    maxStorageLevelPct = 1.0 # percentage of WGV
    minStorageLevelPct = 0.0 # percentage of WGV
    maxInjectionCapacityPct = 1.0 # percentage of nominalInjectionCapacity
    maxReleaseCapacityPct = 1.0 # percentage of nominalReleaseCapacity
    injectionCost = 0.20 # [EUR/MWh]
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

    # Market Entity
    marketSell = Market( name = "mrkt_0",
                         discountFactor = discountFactor,
                         fwdCurveBid = fwdCurveBid,
                         fwdCurveAsk = fwdCurveAsk,
                         srcs = [storage],
                         snks = [] )

    marketBuy = Market( name = "mrkt_1",
                        discountFactor = discountFactor,
                        fwdCurveBid = fwdCurveBid,
                        fwdCurveAsk = fwdCurveAsk,
                        srcs = [],
                        snks = [storage] )
       
    print storage.name, "(src_list): ", [src.name for src in storage.src_list]    
    print storage.name, "(snk_list): ", [snk.name for snk in storage.snk_list]
    print marketSell.name,  "(src_list): ", [src.name for src in marketSell.src_list]
    print marketSell.name,  "(snk_list): ", [snk.name for snk in marketSell.snk_list]
    print marketBuy.name,  "(src_list): ", [src.name for src in marketBuy.src_list]
    print marketBuy.name,  "(snk_list): ", [snk.name for snk in marketBuy.snk_list]
    
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

    # Set dispatch periods
    storage.set_DISPATCH_PERIODS(DISPATCH_PERIODS)
    marketSell.set_DISPATCH_PERIODS(DISPATCH_PERIODS)
    marketBuy.set_DISPATCH_PERIODS(DISPATCH_PERIODS)
        
    # Create lp variables
    storage.create_lp_vars( prefix )
    marketSell.create_lp_vars( prefix )
    marketBuy.create_lp_vars( prefix )

    # Create model
    storage.create_model( prefix )
    marketSell.create_model( prefix )
    marketBuy.create_model( prefix )

    # Get (objective) constraints
    objective_list = []
    objective_list += storage.objective_list
    objective_list += marketSell.objective_list
    objective_list += marketBuy.objective_list

    objective = pulp.LpAffineExpression( constant = 0 )
    for item in objective_list:
        objective += item

    constraint_list = []
    constraint_list += storage.constraint_list
    constraint_list += marketSell.constraint_list
    constraint_list += marketBuy.constraint_list

    # Create lp problem and add (objective) constraints
    lp = pulp.LpProblem( "Test A.1", pulp.LpMaximize )
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

#    print "Objective:", value(lp.objective)
#    for v in lp.variables():
#        print v.name, "=", v.varValue

    print "Objective =", value(lp.objective)
    print "%15s; %15s; %15s; %15s; %15s; %15s; %15s; %15s;" % ("Index", storage.name, storage.name, storage.name, marketSell.name, marketSell.name, marketBuy.name, marketBuy.name)
    print "%15s; %15s; %15s; %15s; %15s; %15s; %15s; %15s;" % ("t", "lev[t] [%]", "inj[t] [%]", "rel[t] [%]", "iflow[t] [MWh]", "oflow[t] [MWh]", "iflow[t] [MWh]", "oflow[t] [MWh]")
    for t in xrange( nSteps + 1):
        strg_lev_pct    = storage.name      + "_lev_pct_%d" % t 
        strg_q_inj      = storage.name      + "_q_inj_pct_%d" % t
        strg_q_rel      = storage.name      + "_q_rel_pct_%d" % t
        mkt_0_in_flow   = marketSell.name   + "_iflow_%d" % t
        mkt_0_out_flow  = marketSell.name   + "_oflow_%d" % t
        mkt_1_in_flow   = marketBuy.name    + "_iflow_%d" % t
        mkt_1_out_flow  = marketBuy.name    + "_oflow_%d" % t
        if t < nSteps:
            print "%15d; %15.12f; %15.12f; %15.12f; %15.2f; %15.2f; %15.2f; %15.2f;" %(t, lp.variablesDict()[strg_lev_pct].varValue, lp.variablesDict()[strg_q_inj].varValue, lp.variablesDict()[strg_q_rel].varValue, lp.variablesDict()[mkt_0_in_flow].varValue, lp.variablesDict()[mkt_0_out_flow].varValue, lp.variablesDict()[mkt_1_in_flow].varValue, lp.variablesDict()[mkt_1_out_flow].varValue)
        else:
            print "%15d; %15.12f; %15s; %15s; %15s; %15s; %15s; %15s;"%(t, lp.variablesDict()[strg_lev_pct].varValue, "N/A", "N/A", "N/A", "N/A", "N/A", "N/A")
