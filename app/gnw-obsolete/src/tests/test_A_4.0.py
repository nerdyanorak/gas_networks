"""
Test A.1: Simple storage and market test

The topology of this gas network is
    - dispatch period daily for one year ([24]*365)
    - simple storage linked to market as source and sink
    - market linked to storage as source and sink
    - market linked to a strip of daily standard products as
    source and sink
    - daily standard product linked to market as source and sink
    - daily standard product linked to trade tranche of same
    delivery period of one day as source and sink
    - trade tranche linked to standard product of same
    delivery period of one day as source and sink
    - trade tranche has no capacity limits
    - discount factor is 1.0
    - daily forward curve, represented by strip of
    daily standard products and their associated trade
    tranche, has sinusodial shape. 
"""

if __name__ == "__main__":
    from entity import Entity
    from storage import Storage
    from market import Market
    from stdprod import StandardProduct
    from ttranche import TradeTranche
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
  
    FWD_CURVE_MID = [round(basePrice + cos(2.0*pi*t/(nSteps-1)), 3) for t in xrange( nSteps )]
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
  
    storage = Storage( "storage[0]",
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

    # Trading Tranche Entities
    trdtran_list = []
    # Daily StandardProducts Entities
    stdprod_list = []
    for t in xrange( nSteps ):
        trdtran_list.append( TradeTranche( name = "trdtran[%d]" % t,
                                           price = (FWD_CURVE_BID[t], FWD_CURVE_ASK[t]),
                                           deliveryPeriod = (t,t),
                                           capacityLimits = (None, None),
                                           discountFactor = DISCOUNT_FACTOR ) )
        stdprod_list.append( StandardProduct( name = "stdprod[%d]" % t,
                                              deliveryPeriod = (t,t),
                                              position = 0.0,
                                              minTradeSize = 0.0,
                                              clipSize = None) )
    
    for t in xrange( nSteps ):
        stdprod_list[t].append_to_src_list( trdtran_list[t] )
        stdprod_list[t].append_to_snk_list( trdtran_list[t] )
        
    # Market Entity
    market = Market( name = "market[0]",
                     srcs = [storage] + stdprod_list,
                     snks = [storage] + stdprod_list )
       
    print market.name,  "(src_list): ", [src.name for src in market.src_list]
    print market.name,  "(snk_list): ", [snk.name for snk in market.snk_list]
    print storage.name, "(src_list): ", [src.name for src in storage.src_list]    
    print storage.name, "(snk_list): ", [snk.name for snk in storage.snk_list]
    
    for t in xrange( nSteps ):
        print stdprod_list[t].name, "(src_list): ", [src.name for src in stdprod_list[t].src_list]    
        print stdprod_list[t].name, "(snk_list): ", [snk.name for snk in stdprod_list[t].snk_list]

    for t in xrange( nSteps ):
        print trdtran_list[t].name, "(src_list): ", [src.name for src in trdtran_list[t].src_list]    
        print trdtran_list[t].name, "(snk_list): ", [snk.name for snk in trdtran_list[t].snk_list]

    # Un-comment the following two lines
    # to get a dot-graph representation
    # of the gas network set-up above
    # Copy print output into text file
    # 'dotgraph.txt' and run on the
    # command line
    # dot -Tjpg dotgraph.txt -o dotgraph.jpg
    # to create a jpg graphical representation
    # of the graph. 
    graph = market.get_topology_graph()
    print graph

    # Set dispatch periods
    market.set_DISPATCH_PERIODS(DISPATCH_PERIODS)
    storage.set_DISPATCH_PERIODS(DISPATCH_PERIODS)
    for t in range( nSteps ):
        stdprod_list[t].set_DISPATCH_PERIODS(DISPATCH_PERIODS)
        trdtran_list[t].set_DISPATCH_PERIODS(DISPATCH_PERIODS)
        
    # Create lp variables
    market.create_lp_vars( prefix )
    storage.create_lp_vars( prefix )
    for t in range( nSteps ):
        stdprod_list[t].create_lp_vars( prefix )
        trdtran_list[t].create_lp_vars( prefix )

    # Create model
    market.create_model( prefix )
    storage.create_model( prefix )
    for t in range( nSteps ):
        stdprod_list[t].create_model( prefix )
        trdtran_list[t].create_model( prefix )

    # Get (objective) constraints
    objective_list = []
    objective_list += market.objective_list
    objective_list += storage.objective_list
    for t in range( nSteps ):
        objective_list += stdprod_list[t].objective_list
        objective_list += trdtran_list[t].objective_list

    objective = pulp.LpAffineExpression( constant = 0 )
    for item in objective_list:
        objective += item

    constraint_list = []
    constraint_list += market.constraint_list
    constraint_list += storage.constraint_list
    for t in range( nSteps ):
        constraint_list += stdprod_list[t].constraint_list
        constraint_list += trdtran_list[t].constraint_list

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
    print "%15s; %15s; %15s; %15s; %15s; %15s; %15s; %15s;" % ("Index", storage.name, storage.name, storage.name, marketSell.name, marketSell.name, marketBuy.name, marketBuy.name)
    print "%15s; %15s; %15s; %15s; %15s; %15s; %15s; %15s;" % ("t", "lev[t] [%]", "inj[t] [%]", "rel[t] [%]", "iflow[t] [MWh]", "oflow[t] [MWh]", "iflow[t] [MWh]", "oflow[t] [MWh]")
    for t in xrange( nSteps + 1):
        lev_pct = "storage_0_lev_pct_%d" % t 
        q_inj = "storage_0_q_inj_pct_%d" % t
        q_rel = "storage_0_q_rel_pct_%d" % t
        mkt_sell_in_flow = "market_0_iflow_%d" % t
        mkt_sell_out_flow = "market_0_oflow_%d" % t
        mkt_buy_in_flow = "market_1_iflow_%d" % t
        mkt_buy_out_flow = "market_1_oflow_%d" % t
        if t < nSteps:
            print "%15d; %15.12f; %15.12f; %15.12f; %15.2f; %15.2f; %15.2f; %15.2f;" %(t, lp.variablesDict()[lev_pct].varValue, lp.variablesDict()[q_inj].varValue, lp.variablesDict()[q_rel].varValue, lp.variablesDict()[mkt_sell_in_flow].varValue, lp.variablesDict()[mkt_sell_out_flow].varValue, lp.variablesDict()[mkt_buy_in_flow].varValue, lp.variablesDict()[mkt_buy_out_flow].varValue)
        else:
            print "%15d; %15.12f; %15s; %15s; %15s; %15s; %15s; %15s;"%(t, lp.variablesDict()[lev_pct].varValue, "N/A", "N/A", "N/A", "N/A", "N/A", "N/A")
