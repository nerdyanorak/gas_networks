# ==============================================================================
#
#   package         :   GasNetWorks (gnw) Python/pulp fuelled LP/MIP modeller 
#   author          :   Marc Roth (re04179)
#   version         :   $Id: driver.py 9768 2010-09-22 20:07:23Z re04179 $
#   heading         :   $HeadURL: http://subversion.rwe.com/svn/s_and_v_projects/GasNetworks/trunk/app/gnw/pulp/src/driver.py $
#
#   Description     :   Package file
#
#   Creation Date   :   06Mar2009
#
#   Copyright       :   RWE Supply and Trading GmbH
#
# ==============================================================================
"""
gnw: Driver for running GasNetWorks (gnw) linear optimisation
"""
import pulp
import gnw.pulp_patches
import sys

from gnw.network_factory import NetworkFactory

from gnw.reader import read_coeffs
from gnw.writer import write_product_results 
from gnw.writer import write_dispatch_results
from gnw.util import dbg_print


def main(data_dir, result_dir, verbose=False):
    """ Runs a test (case) from inputs located
    in folder L{data_dir} and outputs results to
    folder L{result_dir} (folder must exist). The
    input data is in form of text files (.dat) as
    created using Excel workbook excel/gnw_com_demo.xls
    or the Excel workbooks located under
    app/gnw/pulp/data/test/<testcase>/*.xls
    
    
    @param data_dir: existing absolute or
        relative path to folder where input data
        is located
    @type data_dir: L{str}
    
    @param result_dir: existing absolute or
        relative path to folder where output data
        will be written to
    @type result_dir: L{str}
    
    @param verbose: flags whether additional progress
        information is written to the console
    @type verbose: L{bool} [default=False] 
    """

    dbg_print( "reading coefficient files ...", verbose )
    data_dict = read_coeffs( data_dir )
    
    dbg_print( "initialising networks ...", verbose )
    ntwrk = NetworkFactory.CreateFromDataDict( {'NAME' : "ntwrk"}, data_dict, verbose )
    
    dbg_print( "creating LP variables ...", verbose )
    ntwrk.create_lp_vars()
    dbg_print( "creating LP model ...", verbose )
    ntwrk.create_model()

    # Create problem and add (objective) constraints
    dbg_print( "initialising LP problem ...", verbose )
    prblm_name = "gnw"
    prblm = pulp.LpProblem( prblm_name, pulp.LpMaximize )
    
    # Get (objective) constraints
    dbg_print( "creating LP objective ...", verbose )
    prblm += ntwrk.get_objective()
    
    dbg_print( "creating LP constraints ...", verbose )
    constraint_list = ntwrk.get_constraints()
    for constraint in constraint_list:
        prblm += constraint 

    pulp.LpSolverDefault.keepFiles = True
#    pulp.pulpTestAll()

#===============================================================================
#    fname = "%s/%s-%s.%s" % (rslt_dir, prblm.name, ntwrk.name, "lp")
#    dbg_print( "writing problem in LP-format to '%s' ..." % fname, verbose )
#    prblm.writeLP( fname )
##    return
#===============================================================================

#===============================================================================
#    fname = "%s/%s-%s.%s" % (rslt_dir, prblm.name, ntwrk.name, "mps")
#    dbg_print( "writing problem in MPS-format to '%s' ..." % fname, verbose )
#    prblm.writeMPS( fname )
##    return
#===============================================================================

    dbg_print( "solving ...", verbose )

#    solver = pulp.GLPK_CMD()
    
    # Essen Production Xpress Server
#    solver = pulp.XPRESS_REMOTE_CLIENT( "http://xpressprod.rwe.com:8080/csgb-xpress/services/XpressExecutionServer?wsdl" )
#    solver = pulp.XPRESS_REMOTE_CLIENT( "http://s030a6800:8080/csgb-xpress/services/XpressExecutionServer?wsdl" )
    
    # Essen Development Xpress Server
#    solver = pulp.XPRESS_REMOTE_CLIENT( "http://xpressdev.rwe.com:8090/csgb-xpress/services/XpressExecutionServer?wsdl" )
#    solver = pulp.XPRESS_REMOTE_CLIENT( "http://s030a6810:8090/csgb-xpress/services/XpressExecutionServer?wsdl" )

    # Swindon Simulation and Xpress Server    
#    solver = pulp.XPRESS_REMOTE_CLIENT( "http://s060a9230:8080/csgb-xpress/services/XpressExecutionServer?wsdl" )

    # Essen Xpress Server using new pulp.XPRESS_SERVICE_CLIENT
    #params= ''              # string of name=value pairs separated by ';' character
    params='MAXTIME=-120;MIPRELSTOP=0.005;MIPRELCUTOFF=1.0e-4;PIVOTTOL=1.0e-10'
    mode = 'DEVELOPMENT'    # one of ['TESTING', 'DEVELOPMENT', ...?]
    solver = pulp.XPRESS_SERVICE_CLIENT( optcontrol=params, optimisationMode=mode )
    
    prblm.solve( solver )

    problem_status = pulp.LpStatus[prblm.status]
    dbg_print( "status = %s" % problem_status, verbose )

    if prblm.status != pulp.LpStatusOptimal:
        return
    obj_value_1 = pulp.value( prblm.objective )
    obj_value_2 = ntwrk.get_objective_value().value()
    mtm_value_1 = ntwrk.get_mark_to_market_value().value()
    
    dbg_print( "objective = %.8f" % obj_value_1, verbose ) 

    dbg_print( "writing results ...", verbose )
    use_std_out = False
    file = sys.stdout
    
    if not use_std_out:
        fname = "%s/%s-%s-%s.%s" % (rslt_dir, prblm.name, ntwrk.name, "rslts", "txt")
        file = open( fname, "w" )
    print >> file, ("%-s%s%-s%s") % ("status", ";", problem_status, ";")
    print >> file, ("%-s%s%.8f%s") % ("objval[1]", ";", obj_value_1, ";")
#    print >> file, ("%-s%s%.8f%s") % ("objval[2]", ";", obj_value_2, ";")
    print >> file, ("%-s%s%.8f%s") % ("mtmval[1]", ";", mtm_value_1, ";")
    
    if not use_std_out:
        file.flush()
        file.close()
    
    dbg_print( "... aggregated standard product and trade tranche results", verbose ) 
    if not use_std_out:
        fname = "%s/%s-%s-%s.%s" % (rslt_dir, prblm.name, ntwrk.name, "product-rslts", "txt")
        file = open( fname, "w" )
    write_product_results( ntwrk, prblm, file )
    if not use_std_out:
        file.flush()
        file.close()

    dbg_print( "... aggregated storage and standard product results", verbose )
    if not use_std_out:
        fname = "%s/%s-%s-%s.%s" % (rslt_dir, prblm.name, ntwrk.name, "dispatch-rslts", "txt")
        file = open( fname, "w"  ) 
    write_dispatch_results( ntwrk, prblm, file )
    if not use_std_out:
        file.flush()
        file.close()

#===============================================================================
#    dbg_print( "... all LP variable values", verbose )
#    fname = "%s/%s-%s-%s.%s" % (rslt_dir, prblm.name, ntwrk.name, "variables", "txt")
#    file = open( fname, "w" )
#    for v in prblm.variables():
#        print >> file, v.name, "=", v.varValue
#    file.flush()
#    file.close()
#===============================================================================

    dbg_print( "... write network results ...", verbose )
    ntwrk.write_results( rslt_dir,
                         basename = "%s-%s" % (prblm.name, ntwrk.name),
                         extension = "txt",
                         canonical = False,
                         verbose = verbose,
                         indent = 4 )
    
    dbg_print( "... done.", verbose )
    
    del ntwrk
    
    
    
if __name__ == "__main__":
    
    import optparse
    parser = optparse.OptionParser()
    parser.add_option( "-i", "--input",
                       dest="data_dir", default=".",
                       help="read input from folder DATA [default=%default]",
                       metavar="DATA" )
    parser.add_option( "-o", "--output",
                       dest="rslt_dir", default=".",
                       help="write output to folder RSLT [default=%default]",
                       metavar="RSLT" )
    parser.add_option( "-v", "--verbose",
                       dest="verbose", action="store_true", default=False,
                       help="being verbose [default=%default]" )
    parser.add_option( "-x", "--exclude-dirs",
                       dest="exclude", action="store_true", default=False,
                       help="ignores input and output folder locations "
                       "(even ones explicitly given by options "
                       "'-i'/'--input' and  '-o'/'--output', respectively) "
                       "and runs internally pre-configured test cases instead "
                       "[default=%default]" )
    parser.add_option( "-t", "--test-list",
                       dest="testlist", action="store_true", default=False,
                       help="list names of internally pre-configured test cases "
                       "[default=%default]" )
    
    (options, args) = parser.parse_args()
    
    tests = []

    tests += ["supplier-dummy-dsp"]
    
    tests += ["supplier-dummy-dsp-bo-negative_curbuypos"]
    tests += ["supplier-dummy-dsp-bo-negative_curbuypos-mup"]
    tests += ["supplier-dummy-dsp-bo-positive_cursellpos"]
    tests += ["supplier-dummy-dsp-bo-positive_cursellpos-mup"]
    tests += ["supplier-dummy-dsp-bo-zero_curpos"]
    tests += ["supplier-dummy-dsp-bo-zero_curpos-mup"]

    tests += ["supplier-dummy-dsp-cfw"]
    tests += ["supplier-dummy-dsp-cfw-mup"]
    tests += ["supplier-dummy-dsp-mup"]

    tests += ["supplier-dummy-dsp-zero_bo-negative_curbuypos"]
    tests += ["supplier-dummy-dsp-zero_bo-negative_curbuypos-mup"]
    tests += ["supplier-dummy-dsp-zero_bo-positive_cursellpos"]
    tests += ["supplier-dummy-dsp-zero_bo-positive_cursellpos-mup"]
    tests += ["supplier-dummy-dsp-zero_bo-zero_curpos"]
    tests += ["supplier-dummy-dsp-zero_bo-zero_curpos-mup"]

    tests += ["supplier-dummy-prd-bo-negative_curbuypos"]
    tests += ["supplier-dummy-prd-bo-negative_curbuypos-mup"]
    tests += ["supplier-dummy-prd-bo-positive_cursellpos"]
    tests += ["supplier-dummy-prd-bo-positive_cursellpos-mup"]
    tests += ["supplier-dummy-prd-bo-zero_curpos"]
    tests += ["supplier-dummy-prd-bo-zero_curpos-mup"]

    tests += ["supplier-dummy-prd-trn"]
    tests += ["supplier-dummy-prd-trn-cfw"]
    tests += ["supplier-dummy-prd-trn-cfw-mup"]
    tests += ["supplier-dummy-prd-trn-mup"]

    tests += ["supplier-dummy-prd-zero_bo-negative_curbuypos"]
    tests += ["supplier-dummy-prd-zero_bo-negative_curbuypos-mup"]
    tests += ["supplier-dummy-prd-zero_bo-positive_cursellpos"]
    tests += ["supplier-dummy-prd-zero_bo-positive_cursellpos-mup"]
    tests += ["supplier-dummy-prd-zero_bo-zero_curpos"]
    tests += ["supplier-dummy-prd-zero_bo-zero_curpos-mup"]
    
    tests += ["supplier-gas-terra"]                         # supply contract base case
    tests += ["supplier-gas-terra-avg-ctrct-price-cfw-exp"] # supply contract with carry forward with given
                                                            # average contract price for initial
                                                            # accounting period (rather calculated
                                                            # by model from contract price curve)
                                                            # and having 3-year volume expiry feature
    tests += ["supplier-gas-terra-avg-ctrct-price-cfw-exp-mup-exp"] # supply contract with carry forward and make-up
                                                            # with given average contract price for initial
                                                            # accounting period (rather calculated
                                                            # by model from contract price curve)
                                                            # and having 3-year volume expiry feature
    tests += ["supplier-gas-terra-avg-ctrct-price-mup"]     # supply contract with make-up with given
                                                            # average contract price for initial
                                                            # accounting period (rather calculated
                                                            # by model from contract price curve)
    tests += ["supplier-gas-terra-avg-ctrct-price-mup-exp"] # supply contract with make-up with given
                                                            # average contract price for initial
                                                            # accounting period (rather calculated
                                                            # by model from contract price curve)
                                                            # and having 3-year volume expiry feature
    tests += ["supplier-gas-terra-cfw"]                     # supply contract with carry forward
    tests += ["supplier-gas-terra-cfw-mup"]                 # supply contract with carry forward and make-up
    tests += ["supplier-gas-terra-curpos"]                  # supply contract with current position set
    tests += ["supplier-gas-terra-mup"]                     # supply contract with make-up
    tests += ["virtstor-3sp-365-24-0cs-11-30ts"]            # storage contract with volume dependent b/o prices
    tests += ["virtstor-3sp-365-24-0cs-11-30ts-30min-sc"]   # storage contract with volume dependent b/o prices, storage rate curves and 30 min trade size
    tests += ["virtstor-3sp-365-24-0cs-11-30ts-sc"]         # storage contract with volume dependent b/o prices and storage rate curves

    tests += ["virtstor-3sp-365-dc-0cs-11-30ts"]            # storage contract without storage rate curves, but using dispatch products rather
                                                            # than standard products/trade tranches.

#===============================================================================
#    tests += ["virtstor-3sp-365-dc-0cs-11-30ts-sc"]         # storage with storage rate curves, but using dispatch products rather
#                                                            # than standard products/trade tranches, results in very long running times!
#===============================================================================
#===============================================================================
#    tests += ["virtstor-3sp-365-24-30cs-11-30ts"]           # potentially almost indefinite running time!
#===============================================================================

    if options.testlist:
        if options.rslt_dir == ".":
            file = sys.stdout
        else:
            file = open( options.rslt_dir, "w" )
        
        for test in tests:
            print >> file, test
        
        file.flush()
        file.close()
        sys.exit( 0 )
    
    if options.exclude:
        num_tests = len( tests )
        cur_test = 0
        tests_failed = 0
        
        base_dir = ".."
        for test in tests:
            try:
                cur_test += 1
                
                dbg_print( "running test '%s' (%d of %d) ..." % (test, cur_test, num_tests), True )
                test_dir = "%s/data/test/%s/pulp" % (base_dir, test)
                
                data_dir = "%s/%s" % (test_dir, "data")
                rslt_dir = "%s/%s" % (test_dir, "results")
                
                main( data_dir, rslt_dir, options.verbose )
            except:
                tests_failed += 1
                dbg_print( "test '%s' failed!" % test, True )
                dbg_print( "error type: %s, error value: %s" % (sys.exc_info()[1], sys.exc_info()[2]), True )
        dbg_print( "... done", True )
        
        sys.exit( -tests_failed )
        
    try:
        data_dir = options.data_dir
        rslt_dir = options.rslt_dir
    
        main( data_dir, rslt_dir, options.verbose )
        sys.exit( 0 )
    except:
        sys.exit( -1 )
        
# ==============================================================================
#
#   Revision Control:
#
#   $Revision:: 9768                    $   Revision of last commit
#   $Author:: re04179                   $   Author of last commit
#   $Date:: 2010-09-22 22:07:23 +0200 (#$   Date of last commit
#
# ==============================================================================
