"""
Test A.1: Simple storage and market test

The topology of this gas network is
    - dispatch period daily for one year ([24]*365)
    - simple storage linked to
        - buy market as as sink
        - sell market as a source
    - buy market linked to storage as source
    - sell market linked to storage as sink
    - markets are linked to daily standard products:
        - one strip for Buy market acting as sources
        - one strip for Sell market acting as sinks
    - discount factor is 1.0
    - daily forward curve, represented by vectors
    of daily bid and ask prices having sinusodial shape. 
"""

if __name__ == "__main__":
    from entity import Entity
    from storage import Storage
    from market import Market
    from stdprod import StandardProduct
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
#    print FWD_CURVE_BID
#    print FWD_CURVE_MID
#    print FWD_CURVE_ASK

    
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
    
    stdprod_purch_list = []
    stdprod_sales_list = []
    for t in xrange( nSteps ):
        stdprod_purch_list.append( StandardProduct( name = "stdpurch_%d" % t,
                                                    deliveryPeriod = (t, t),
                                                    position = 0.0,
                                                    minTradeSize = 0.0,
                                                    clipSize = None,
                                                    discountFactor = discountFactor,
                                                    fwdCurveBid = fwdCurveBid,
                                                    fwdCurveAsk = fwdCurveAsk ) )
        stdprod_sales_list.append( StandardProduct( name = "stdsales_%d" % t,
                                                    deliveryPeriod = (t, t),
                                                    position = 0.0,
                                                    minTradeSize = 0.0,
                                                    clipSize = None,
                                                    discountFactor = discountFactor,
                                                    fwdCurveBid = fwdCurveBid,
                                                    fwdCurveAsk = fwdCurveAsk ) )

    # Market Entity
    market = Market( name = "mrkt_0",
                     discountFactor = discountFactor,
                     fwdCurveBid = fwdCurveBid,
                     fwdCurveAsk = fwdCurveAsk,
                     srcs = [storage] + stdprod_purch_list,
                     snks = [storage] + stdprod_sales_list )


    print storage.name, "(src_list):", [src.name for src in storage.src_list]    
    print storage.name, "(snk_list):", [snk.name for snk in storage.snk_list]

    print market.name, "(src_list):", [src.name for src in market.src_list]
    print market.name, "(snk_list):", [snk.name for snk in market.snk_list]
    
    for item in stdprod_purch_list:
        print item.name, "(src_list):", [src.name for src in item.src_list]
        print item.name, "(snk_list):", [snk.name for snk in item.snk_list] 
    
    for item in stdprod_sales_list:
        print item.name, "(src_list):", [src.name for src in item.src_list]
        print item.name, "(snk_list):", [snk.name for snk in item.snk_list] 

    
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
    market.set_DISPATCH_PERIODS(DISPATCH_PERIODS)
    for item in stdprod_purch_list:
        item.set_DISPATCH_PERIODS(DISPATCH_PERIODS)
    for item in stdprod_sales_list:
        item.set_DISPATCH_PERIODS(DISPATCH_PERIODS)
        
    # Create lp variables
    storage.create_lp_vars( prefix )
    market.create_lp_vars( prefix )
    for item in stdprod_purch_list:
        item.create_lp_vars( prefix )
    for item in stdprod_sales_list:
        item.create_lp_vars( prefix )

    # Create model
    storage.create_model( prefix )
    market.create_model( prefix )
    for item in stdprod_purch_list:
        item.create_model( prefix )
    for item in stdprod_sales_list:
        item.create_model( prefix )

    # Get (objective) constraints
    objective_list = []
    objective_list += storage.objective_list
    objective_list += market.objective_list
    for item in stdprod_purch_list:
        objective_list += item.objective_list
    for item in stdprod_sales_list:
        objective_list += item.objective_list

    objective = pulp.LpAffineExpression( constant = 0 )
    for item in objective_list:
        objective += item

    constraint_list = []
    constraint_list += storage.constraint_list
    constraint_list += market.constraint_list
    for item in stdprod_purch_list:
        constraint_list += item.constraint_list
    for item in stdprod_sales_list:
        constraint_list += item.constraint_list

    # Create lp problem and add (objective) constraints
    lp = pulp.LpProblem( problemName, pulp.LpMaximize )
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

    print "Objective:", value(lp.objective)
    for v in lp.variables():
        print v.name, "=", v.varValue
    
    print "Objective =", value(lp.objective)
    print "%15s; %15s; %15s; %15s; %15s; %15s;" % ("Index", storage.name, storage.name, storage.name, market.name, market.name),
    for s in xrange( nSteps ):
        print "%15s; %15s;" % (stdprod_purch_list[s].name, stdprod_purch_list[s].name),
    for s in xrange( nSteps ):
        print "%15s; %15s;" % (stdprod_sales_list[s].name, stdprod_sales_list[s].name),
    print

    print "%15s; %15s; %15s; %15s; %15s; %15s;" % ("t", "lev[t] [%]", "inj[t] [%]", "rel[t] [%]", "iflow[t] [MWh]", "oflow[t] [MWh]"),
    for s in xrange( nSteps ):
        print "%15s; %15s;" % ("iflow[t] [MWh]", "oflow[t] [MWh]"),
    for s in xrange( nSteps ):
        print "%15s; %15s;" % ("iflow[t] [MWh]", "oflow[t] [MWh]"),
    print
    for t in xrange( nSteps + 1):
        strg_lev_pct    = storage.name  + "_lev_pct_%d" % t 
        strg_q_inj      = storage.name  + "_q_inj_pct_%d" % t
        strg_q_rel      = storage.name  + "_q_rel_pct_%d" % t
        mkt_iflow       = market.name   + "_iflow_%d" % t
        mkt_oflow       = market.name   + "_oflow_%d" % t
        if t < nSteps:
            print "%15d; %15.12f; %15.12f; %15.12f; %15.2f; %15.2f;" % (t, lp.variablesDict()[strg_lev_pct].varValue, lp.variablesDict()[strg_q_inj].varValue, lp.variablesDict()[strg_q_rel].varValue, lp.variablesDict()[mkt_iflow].varValue, lp.variablesDict()[mkt_oflow].varValue),

            for s in xrange( nSteps ):
                stdpurch_iflow = stdprod_purch_list[s].name + "_iflow_%d" % t
                stdpurch_oflow = stdprod_purch_list[s].name + "_oflow_%d" % t
                print "%15.2f; %15.2f;" % (lp.variablesDict()[stdpurch_iflow].varValue, lp.variablesDict()[stdpurch_oflow].varValue),
            for s in xrange( nSteps ):
                stdsales_iflow = stdprod_sales_list[s].name + "_iflow_%d" % t
                stdsales_oflow = stdprod_sales_list[s].name + "_oflow_%d" % t
                print "%15.2f; %15.2f;" % (lp.variablesDict()[stdsales_iflow].varValue, lp.variablesDict()[stdsales_oflow].varValue),
            print
        else:
            print "%15d; %15.12f; %15s; %15s; %15s; %15s;" % (t, lp.variablesDict()[strg_lev_pct].varValue, "N/A", "N/A", "N/A", "N/A"),
            
            for s in xrange( nSteps ):
                print "%15s; %15s;" % ("N/A", "N/A"),
            for s in xrange( nSteps ):
                print "%15s; %15s;" % ("N/A", "N/A"),
            print
