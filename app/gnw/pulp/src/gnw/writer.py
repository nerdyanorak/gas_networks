# ==============================================================================
#
#   package         :   GasNetWorks (gnw) Python/pulp fuelled LP/MIP modeller 
#   author          :   Marc Roth (re04179)
#   version         :   $Id: writer.py 2138 2009-09-22 12:02:19Z re04179 $
#   heading         :   $HeadURL: http://subversion.rwe.com/svn/s_and_v_projects/GasNetworks/trunk/app/gnw/pulp/src/gnw/writer.py $
#
#   Description     :   Package file
#
#   Creation Date   :   06Mar2009
#
#   Copyright       :   RWE Supply and Trading GmbH
#
# ==============================================================================
"""
gnw: some utility functions to write results in
a formatted way to a file
@todo: integrate functions contained herein into L{gnw.Network} class
"""
from gnw.network import Network
from gnw.storage import Storage
from gnw.market import Market
from gnw.product import Product
from gnw.tranche import Tranche

from util import conditional

from __init__ import __eSell__
from __init__ import __eBuy___

import sys
import pulp


def write_product_results(ntwrk, lp, file=sys.stdout, sfmt="%-s", ffmt="%.8f", ifmt="%0d", sep=';'):
    """
    Writes product and tranche results to file.
    
    @param ntwrk: gas network class instance
    @type ntwrk: L{gnw.network.Network}
    
    @param lp: a fully setup and solved linear/mip program corresponding
        to ntwrk.
    @type lp: L{pulp.LpProblem}
    
    @param file: file object that has been opened for writing
    @type file: L{file}
    
    @param sfmt: format string for strings
    @type sfmt: L{str}
    
    @param ffmt: format string for floating point numbers
    @type ffmt: L{str}
    
    @param ifmt: format string for integral numbers
    @type ifmt: L{str}
    
    @param sep: field separator
    @type sep: L{str}
    
    @raise ValueError:
    @raise TypeError: 
    """
    if file.closed:
        raise ValueError, "write_product_results: closed file handle"
    if not isinstance( ntwrk, Network ):
        raise TypeError, "write_product_results: Parameter 'ntwrk' needs to be an instance of class 'gnw.Network'"
    if not isinstance( lp, pulp.LpProblem ):
        raise TypeError, "write_product_results: Parameter 'lp' needs to be an instance of class 'pulp.LpProblem'"
    
    mrkt_entity_list = ntwrk.get_entity_list( Market ) 
    prd_entity_list = []
    for mrkt in mrkt_entity_list:
        prd_entity_list += mrkt.get_entity_list( Product )
    nPrds = len( prd_entity_list )/2
    if nPrds == 0:
        return
    
    trn_entity_list = []
    for prd in prd_entity_list:
        trn_entity_list += prd.get_entity_list( Tranche )
    nTrns = len( trn_entity_list )/(2*nPrds)
    if nTrns == 0:
        return
    
    fmt_dict = {'name' : sfmt,
                'start idx' : ifmt,
                'final idx' : ifmt,
                'buy/sell [-1/1]' : ifmt,
                'clips' : ifmt,
                'pos [MW]' : ffmt,
                'cur pos [MW]' : ffmt,
                'net pos [MW]' : ffmt,
                'vol [MWh]' : ffmt,
                'mid price [EUR/MWh]' : ffmt,
                'bid/ask adj [EUR/MWh]' : ffmt,
                'avg df' : ffmt}

    prd_hdr_list = ['name',
                    'start idx',
                    'final idx',
                    'buy/sell [-1/1]',
                    'clips',
                    'pos [MW]',
                    'cur pos [MW]',
                    'net pos [MW]',
                    'vol [MWh]',
                    'mid price [EUR/MWh]',
                    'avg df']

    trn_hdr_list = ['name',
                    'pos [MW]',
                    'vol [MWh]',
                    'bid/ask adj [EUR/MWh]']
    
    hdr_list = prd_hdr_list + trn_hdr_list*nTrns
                
    sb_list = [__eSell__, __eBuy___]
    
    var_dict = lp.variablesDict()
    
    # Print header line
    for item in hdr_list:
        print >> file, (sfmt + sep) % item,
    print >> file
    for sb in sb_list:
        prd_list = [prd for prd in prd_entity_list if prd.SB == sb]
        for prd in prd_list:

            delivery_period_idx = xrange( prd.DELIVERY_PERIOD[0], prd.DELIVERY_PERIOD[1] + 1)

            print >> file, (fmt_dict['name'] + sep) % prd.name,
            print >> file, (fmt_dict['start idx'] + sep) % prd.DELIVERY_PERIOD[0],
            print >> file, (fmt_dict['final idx'] + sep) % prd.DELIVERY_PERIOD[1],
            print >> file, (fmt_dict['buy/sell [-1/1]'] + sep) % prd.SB,
            if prd.CLIP_SIZE > 0.0:
                print >> file, (fmt_dict['clips'] + sep) % var_dict[prd.name + "_num_clips"].varValue,
            else:
                print >> file, (fmt_dict['clips'] + sep) % 0,
            print >> file, (fmt_dict['pos [MW]'] + sep) % var_dict[prd.name + "_pos"].varValue,
            print >> file, (fmt_dict['cur pos [MW]'] + sep) % prd.CURRENT_POSITION,
            print >> file, (fmt_dict['net pos [MW]'] + sep) % (var_dict[prd.name + "_pos"].varValue + prd.CURRENT_POSITION),
            print >> file, (fmt_dict['vol [MWh]'] + sep) % sum( [var_dict[prd.name + "_vol_%d" % t].varValue for t in delivery_period_idx] ),
            print >> file, (fmt_dict['mid price [EUR/MWh]'] + sep) % prd.MID_PRICE,
            print >> file, (fmt_dict['avg df'] + sep) % (sum( [prd.DISPATCH_PERIOD[t]*prd.DISCOUNT_FACTOR[t] for t in delivery_period_idx] )/sum( [prd.DISPATCH_PERIOD[t] for t in delivery_period_idx] )),

            trn_list = [trn for trn in trn_entity_list \
                        if trn.SB == prd.SB \
                        and trn.DELIVERY_PERIOD[0] == prd.DELIVERY_PERIOD[0] \
                        and trn.DELIVERY_PERIOD[1] == prd.DELIVERY_PERIOD[1]]
            for trn in trn_list:
                print >> file, (fmt_dict['name'] + sep) % trn.name,
                print >> file, (fmt_dict['pos [MW]'] + sep) % var_dict[trn.name + "_pos"].varValue,
                print >> file, (fmt_dict['vol [MWh]'] + sep) % (var_dict[trn.name + "_pos"].varValue*sum( [prd.DISPATCH_PERIOD[t] for t in delivery_period_idx] )),
                print >> file, (fmt_dict['bid/ask adj [EUR/MWh]'] + sep) % trn.BID_ASK_ADJ,

            print >> file

    
def write_dispatch_results(ntwrk, lp, file=sys.stdout, sfmt="%-s", ffmt="%.8f", ifmt="%0d", sep=';'): 
    """
    Writes storage dispatch results to file.
    
    @param ntwrk: gas network class instance
    @type ntwrk: L{gnw.network.Network}
    
    @param lp: a fully setup and solved linear/mip program corresponding
        to ntwrk.
    @type lp: L{pulp.LpProblem}
    
    @param file: file object that has been opened for writing
    @type file: L{file}
    
    @param sfmt: format string for strings
    @type sfmt: L{str}
    
    @param ffmt: format string for floating point numbers
    @type ffmt: L{str}
    
    @param ifmt: format string for integral numbers
    @type ifmt: L{str}
    
    @param sep: field separator
    @type sep: L{str} 
    
    @raise ValueError: 
    @raise TypeError: 
    """
    if file.closed:
        raise ValueError, "write_product_results: closed file handle"
    if not isinstance( ntwrk, Network ):
        raise TypeError, "write_dispatch_results: Parameter 'ntwrk' needs to be an instance of class 'gnw.Network'"
    if not isinstance( lp, pulp.LpProblem ):
        raise TypeError, "write_dispatch_results: Parameter 'lp' needs to be an instance of class 'pulp.LpProblem'"
    
    strg_entity_list = ntwrk.get_entity_list( Storage )
    nStrgs = len( strg_entity_list )
    
    mrkt_entity_list = ntwrk.get_entity_list( Market ) 
    prd_entity_list = []
    for mrkt in mrkt_entity_list:
        prd_entity_list += mrkt.get_entity_list( Product )
    nPrds = len( prd_entity_list )
    trn_entity_list = []
    for prd in prd_entity_list:
        trn_entity_list += prd.get_entity_list( Tranche )
    
    nStps = len( ntwrk.DISPATCH_PERIOD )
    nPnts = nStps + 1

    fmt_dict = {'idx' : ifmt,
                'dt [h]' : ffmt,
                'inj cost [EUR]' : ffmt,
                'rel cost [EUR]' : ffmt,
                'inj cost [EUR/MWh]' : ffmt,
                'rel cost [EUR/MWh]' : ffmt,
                'sales revenue [EUR]' : ffmt,
                'purchase cost [EUR]' : ffmt,
                'lev [WGV%]' : ffmt,
                'lev [MWh]' : ffmt,
                'inj [WGV%]' : ffmt,
                'inj [MWh]' : ffmt,
                'rel [WGV%]' : ffmt,
                'rel [MWh]' : ffmt,
                'name' : sfmt,
                'start idx' : ifmt,
                'final idx' : ifmt,
                'buy/sell [-1/1]' : ifmt,
                'clips' : ifmt,
                'pos [MW]' : ffmt,
                'cur pos [MW]' : ffmt,
                'net pos [MW]' : ffmt,
                'vol [MWh]' : ffmt,
                'price [EUR/MWh]' : ffmt,
                'avg df' : ffmt,
                'df' : ffmt}

    dsp_hdr_list = ['idx',
                    'dt [h]',
                    'inj cost [EUR]',
                    'rel cost [EUR]',
                    'sales revenue [EUR]',
                    'purchase cost [EUR]',
                    'df']
    strg_hdr_list = ['inj cost [EUR/MWh]',
                     'rel cost [EUR/MWh]',
                     'lev [WGV%]',
                     'lev [MWh]',
                     'inj [WGV%]',
                     'inj [MWh]',
                     'rel [WGV%]',
                     'rel [MWh]']
    
    prd_hdr_list = ['pos [MW]',
                    'cur pos [MW]',
                    'net pos [MW]',
                    'vol [MWh]']

    hdr_list = dsp_hdr_list + strg_hdr_list*nStrgs + prd_hdr_list*nPrds
                
    sb_list = [__eSell__, __eBuy___]
    
    var_dict = lp.variablesDict()
    
    NA = "N/A"
    
    # Print 1st header row
    for item in hdr_list:
        print >> file, (sfmt + sep) % item,
    print >> file
    
    # Print 2nd header row
    for i in xrange( len( dsp_hdr_list ) ):
        print >> file, (sfmt + sep) % NA,
    for strg in strg_entity_list:
        for i in xrange( len( strg_hdr_list ) ):
            print >> file, (sfmt + sep) % strg.name,
    for prd in prd_entity_list:
        for i in xrange( len( prd_hdr_list ) ):
            print >> file, (sfmt + sep) % prd.name,
    print >> file
            
    # Print 3rd header row
    for i in xrange( len( dsp_hdr_list ) ):
        print >> file, (sfmt + sep) % NA,
    for i in xrange( nStrgs ):
        for j in xrange( len( strg_hdr_list ) ):
            print >> file, (sfmt + sep) % NA,
    for prd in prd_entity_list:
        for i in xrange( len( prd_hdr_list ) ):
            print >> file, (fmt_dict['buy/sell [-1/1]'] + sep) % prd.SB,
    print >> file
    
    # Print data rows
    for t in xrange( nPnts ):
        print >> file, (fmt_dict['idx'] + sep) % t,
        
        if t == nStps:
            # print last data row
            for i in xrange( len( dsp_hdr_list ) - 1 ):
                print >> file, (sfmt + sep) % NA,
            for strg in strg_entity_list:
                print >> file, (sfmt + sep) % NA,
                print >> file, (sfmt + sep) % NA,
                print >> file, (fmt_dict['lev [WGV%]'] + sep) % var_dict[strg.name + '_lev_pct_%d' % t].varValue,
                print >> file, (fmt_dict['lev [MWh]'] + sep) % (var_dict[strg.name + '_lev_pct_%d' % t].varValue*strg.WGV),
                print >> file, (sfmt + sep) % NA,
                print >> file, (sfmt + sep) % NA,
                print >> file, (sfmt + sep) % NA,
                print >> file, (sfmt + sep) % NA,

            for prd in prd_entity_list:
                for item in prd_hdr_list:
                    print >> file, (sfmt + sep) % NA,
        else:
            print >> file, (fmt_dict['dt [h]'] + sep) % ntwrk.DISPATCH_PERIOD[t],
        
            print >> file, (fmt_dict['inj cost [EUR]'] + sep) % (ntwrk.DISCOUNT_FACTOR[t]*sum( [var_dict[strg.name + '_inj_pct_%d' % t].varValue*strg.INJ_COST[t]*strg.WGV  for strg in ntwrk.get_entity_list( Storage )] )),
            print >> file, (fmt_dict['rel cost [EUR]'] + sep) % (ntwrk.DISCOUNT_FACTOR[t]*sum( [var_dict[strg.name + '_rel_pct_%d' % t].varValue*strg.REL_COST[t]*strg.WGV  for strg in ntwrk.get_entity_list( Storage )] )),

            trn_list = [trn for trn in trn_entity_list \
                        if trn.SB == __eSell__ \
                        and t in xrange( trn.DELIVERY_PERIOD[0], trn.DELIVERY_PERIOD[1] + 1 )]
            sales_revenue = 0.0
            for trn in trn_list:
                prd_list = [prd for prd in prd_entity_list \
                            if prd.SB == trn.SB \
                            and prd.DELIVERY_PERIOD[0] == trn.DELIVERY_PERIOD[0] \
                            and prd.DELIVERY_PERIOD[1] == trn.DELIVERY_PERIOD[1]]
                if len( prd_list ) != 1:
                    raise ValueError, "more than one product found for given tranche"
                prd = prd_list[0]
                sales_revenue += var_dict[trn.name + '_pos'].varValue*trn.DISPATCH_PERIOD[t]*(prd.MID_PRICE - trn.SB*trn.BID_ASK_ADJ)
            print >> file, (fmt_dict['sales revenue [EUR]'] + sep) % sales_revenue,

            trn_list = [trn for trn in trn_entity_list \
                        if trn.SB == __eBuy___ \
                        and t in xrange( trn.DELIVERY_PERIOD[0], trn.DELIVERY_PERIOD[1] + 1 )]
            purchase_cost = 0.0
            for trn in trn_list:
                prd_list = [prd for prd in prd_entity_list \
                            if prd.SB == trn.SB \
                            and prd.DELIVERY_PERIOD[0] == trn.DELIVERY_PERIOD[0] \
                            and prd.DELIVERY_PERIOD[1] == trn.DELIVERY_PERIOD[1]]
                if len( prd_list ) != 1:
                    raise ValueError, "more than one product found for given tranche"
                prd = prd_list[0]
                purchase_cost += var_dict[trn.name + '_pos'].varValue*trn.DISPATCH_PERIOD[t]*(prd.MID_PRICE - trn.SB*trn.BID_ASK_ADJ)
            print >> file, (fmt_dict['purchase cost [EUR]'] + sep) % purchase_cost,
    
            print >> file, (fmt_dict['df'] + sep) % ntwrk.DISCOUNT_FACTOR[t],
            
            for strg in strg_entity_list:
                print >> file, (fmt_dict['inj cost [EUR/MWh]'] + sep) % strg.INJ_COST[t],
                print >> file, (fmt_dict['rel cost [EUR/MWh]'] + sep) % strg.REL_COST[t],
                print >> file, (fmt_dict['lev [WGV%]'] + sep) % var_dict[strg.name + '_lev_pct_%d' % t].varValue,
                print >> file, (fmt_dict['lev [MWh]'] + sep) % (var_dict[strg.name + '_lev_pct_%d' % t].varValue*strg.WGV),
                print >> file, (fmt_dict['inj [WGV%]'] + sep) % var_dict[strg.name + '_inj_pct_%d' % t].varValue,
                print >> file, (fmt_dict['inj [MWh]'] + sep) % (var_dict[strg.name + '_inj_pct_%d' % t].varValue*strg.WGV),
                print >> file, (fmt_dict['rel [WGV%]'] + sep) % var_dict[strg.name + '_rel_pct_%d' % t].varValue,
                print >> file, (fmt_dict['rel [MWh]'] + sep) % (var_dict[strg.name + '_rel_pct_%d' % t].varValue*strg.WGV),

            for sb in sb_list:
                prd_list = [prd for prd in prd_entity_list if prd.SB == sb]
                for prd in prd_list:
                    if t in xrange( prd.DELIVERY_PERIOD[0], prd.DELIVERY_PERIOD[1] + 1 ):
                        print >> file, (fmt_dict['pos [MW]'] + sep) % var_dict[prd.name + "_pos"].varValue,
                        print >> file, (fmt_dict['cur pos [MW]'] + sep) % prd.CURRENT_POSITION,
                        print >> file, (fmt_dict['net pos [MW]'] + sep) % (var_dict[prd.name + "_pos"].varValue + prd.CURRENT_POSITION),
                    else:
                        print >> file, (sfmt + sep) % NA,
                        print >> file, (sfmt + sep) % NA,
                        print >> file, (sfmt + sep) % NA,
                    print >> file, (fmt_dict['vol [MWh]'] + sep) % var_dict[prd.name + "_vol_%d" % t].varValue,
    
        print >> file


if __name__ == "__main__":
    ntwrk = Network( "test", [], 1.0 )

    data_dir = "c:/temp/data/out/v0.5/virtstor-3sp-365-24-0cs-11-30ts-30min-sc/00-results"
    file = open( data_dir + "/" + ntwrk.name + "_product_and_tranche_results.txt", "w" )
    
    write_product_results( ntwrk, pulp.LpProblem(), file )
    
    file.flush()
    file.close()
    
# ==============================================================================
#
#   Revision Control:
#
#   $Revision:: 2138                    $   Revision of last commit
#   $Author:: re04179                   $   Author of last commit
#   $Date:: 2009-09-22 14:02:19 +0200 (#$   Date of last commit
#
# ==============================================================================
