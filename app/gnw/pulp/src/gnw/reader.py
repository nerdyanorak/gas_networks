# ==============================================================================
#
#   package         :   GasNetWorks (gnw) Python/pulp fuelled LP/MIP modeller 
#   author          :   Marc Roth (re04179)
#   version         :   $Id: reader.py 1860 2009-09-07 12:09:18Z re04179 $
#   heading         :   $HeadURL: http://subversion.rwe.com/svn/s_and_v_projects/GasNetworks/trunk/app/gnw/pulp/src/gnw/reader.py $
#
#   Description     :   Package file
#
#   Creation Date   :   06Mar2009
#
#   Copyright       :   RWE Supply and Trading GmbH
#
# ==============================================================================
"""
gnw: Facilitates reading of problem data from
initialisation text files
"""
from mosel import MoselInitFileReader
 
from util import conditional

def read_coeffs(data_dir, reader=MoselInitFileReader.read_mosel_init_file):
    dsc_dict = create_coeff_desc_dict( [data_dir + "/CoefficientDescription.dat"], reader )
    gnrl_dict = create_coeff_dict( data_dir, "General", "Values", "dat", dsc_dict, reader )  
    mrkt_dict = create_coeff_dict( data_dir, "Market", "Values", "dat", dsc_dict, reader )

    strg_dict_list = {}
    if 'nStrgs' in gnrl_dict and gnrl_dict['nStrgs'] > 0:
        if 'STRG_NAMES' not in gnrl_dict:
            raise ValueError, "Expected key 'STRG_NAMES' not found in gnrl_dict"
        for strg in gnrl_dict['STRG_NAMES']:
            strg_dict = create_coeff_dict( data_dir, "Storage_" + strg, "Values", "dat", dsc_dict, reader )
            strg_dict_list[strg] = strg_dict

    splr_dict_list = {}
    if 'nSplrs' in gnrl_dict and gnrl_dict['nSplrs'] > 0:
        if 'SPLR_NAMES' not in gnrl_dict:
            raise ValueError, "Expected key 'SPLR_NAMES' not found in gnrl_dict"            
        for splr in gnrl_dict['SPLR_NAMES']:
            splr_dict = create_coeff_dict( data_dir, "Supplier_" + splr, "Values", "dat", dsc_dict, reader )
            splr_dict_list[splr] = splr_dict

    prd_dict_list = {}
    if 'nStdPrds' in gnrl_dict and gnrl_dict['nStdPrds'] > 0:
        if 'STDPRD_NAMES' not in gnrl_dict:
            raise ValueError, "Expected key 'STDPRD_NAMES' not found in gnrl_dict"            
        for prd in gnrl_dict['STDPRD_NAMES']:
            prd_dict = create_coeff_dict( data_dir, "StandardProduct_" + prd, "Values", "dat", dsc_dict, reader )
            prd_dict_list[prd] = prd_dict

    trn_dict_list = {}
    if 'nTrdTrns' in gnrl_dict and gnrl_dict['nTrdTrns'] > 0:
        if 'TRDTRN_NAMES' not in gnrl_dict:
            raise ValueError, "Expected key 'TRDTRN_NAMES' not found in gnrl_dict"            
        for trn in gnrl_dict['TRDTRN_NAMES']:
            trn_dict = create_coeff_dict( data_dir, "TradeTranche_" + trn, "Values", "dat", dsc_dict, reader )
            trn_dict_list[trn] = trn_dict

    dsp_dict_list = {}
    if 'nDspPrds' in gnrl_dict and gnrl_dict['nDspPrds'] > 0:
        if 'DSPPRD_NAMES' not in gnrl_dict:
            raise ValueError, "Expected key 'DSPPRD_NAMES' not found in gnrl_dict"            
        for dsp in gnrl_dict['DSPPRD_NAMES']:
            dsp_dict = create_coeff_dict( data_dir, "DispatchProduct_" + dsp, "Values", "dat", dsc_dict, reader )
            dsp_dict_list[dsp] = dsp_dict

    frm_dict_list = {}
    if 'nFrmPrfls' in gnrl_dict and gnrl_dict['nFrmPrfls'] > 0:
        if 'FRMPRFL_NAMES' not in gnrl_dict:
            raise ValueError, "Expected key 'FRMPRFL_NAMES' not found in gnrl_dict"            
        for frm in gnrl_dict['FRMPRFL_NAMES']:
            frm_dict = create_coeff_dict( data_dir, "FirmProfile_" + frm, "Values", "dat", dsc_dict, reader )
            frm_dict_list[frm] = frm_dict

    return {'DSC_DICT'          : dsc_dict,
            'GNRL_DICT'         : gnrl_dict,
            'MRKT_DICT'         : mrkt_dict,
            'STRG_DICT_LIST'    : strg_dict_list,
            'SPLR_DICT_LIST'    : splr_dict_list,
            'PRD_DICT_LIST'     : prd_dict_list,
            'TRN_DICT_LIST'     : trn_dict_list,
            'DSP_DICT_LIST'     : dsp_dict_list,
            'FRM_DICT_LIST'     : frm_dict_list}


def create_coeff_desc_dict(fname_list, reader=MoselInitFileReader.read_mosel_init_file):
    # list of currently supported atomic coefficient types
    coeff_type_list = [ 'int', 'float', 'bool', 'str' ]

    dsc_dict = {}
    # read coefficient description data from all files into dictionary
    for fname in fname_list:
        dsc_dict = reader( fname, dsc_dict )
        
    # check dictionary description data for validity
    # the format of a coefficient description data entry is:
    # [ [ <dim> ], [ <cols> ], [ <type>, <type>, ..., <type> ] ]
    # <dim> is an integer for the dimensionality of the coefficient data
    #    0:    atomic
    #    1:    1-d array
    #    2:    2-d array
    # <cols> is an integer gives the number of columns in an array.
    # for dim in [ 0, 1 ]:    <cols> is 1
    # for dim in [ 2 ]:       <cols> is the number of columns
    # i.e., the size of the second dimension
    # <type> is a string in coeff_type_list
    # and len( [ <type>, <type>, ..., <type> ] ) == <cols> must hold.
    
    for k in dsc_dict.keys():
        if len( dsc_dict[k] ) != 3:
            raise IndexError, "create_coeff_desc_dict: Require list of 3 sublists"
        if len( dsc_dict[k][0] ) != 1:
            raise IndexError, "create_coeff_desc_dict: Length of first sublist different from 1"
        if len( dsc_dict[k][1] ) != 1:
            raise IndexError, "create_coeff_desc_dict: Length of second sublist different from 1"

        dsc_dict[k][0][0] = int( dsc_dict[k][0][0] )
        dsc_dict[k][1][0] = int( dsc_dict[k][1][0] )
        if (dsc_dict[k][0][0] == 0 or dsc_dict[k][0][0] == 1) and dsc_dict[k][1][0] != 1:
            raise ValueError, "create_coeff_desc_dict: 0-dimensional or 1-dimensional with column size greater than 1"
        if len( dsc_dict[k][2] ) != dsc_dict[k][1][0]:
            raise ValueError, "create_coeff_desc_dict: Column size and number of type string mismatch"
        for i in xrange( dsc_dict[k][1][0] ):
            if dsc_dict[k][2][i] not in coeff_type_list:
                raise ValueError, "create_coeff_desc_dict: Invalid type string '%s' found" % dsc_dict[k][2][i]
            
    return dsc_dict


def create_coeff_dict(data_dir, fname_prefix, fname_suffix, fname_extension, dsc_dict, reader=MoselInitFileReader.read_mosel_init_file, key="FILE_SUFFIX_LIST"):
    coeff_dict = {}
    fname = data_dir + "/" + fname_prefix + "_" + fname_suffix + "." + fname_extension
    coeff_dict = reader( fname, coeff_dict )
    if key in coeff_dict:
        suffix_list = coeff_dict[key]
        for suffix in suffix_list:
            fname = data_dir + "/" + fname_prefix + "_" + suffix + "." + fname_extension
            coeff_dict = reader( fname, coeff_dict )
            
    for key in coeff_dict.keys():
        coeff_dict[key] = convert_to( coeff_dict[key], dsc_dict[key] )
        
    return coeff_dict


def convert_to(coeff, coeff_desc):
    coeff_dim = coeff_desc[0][0]
    if coeff_dim == 0:
        coeff_type = coeff_desc[2][0] 
        if coeff_type == 'int':
            coeff = int( coeff )
        elif coeff_type == 'float':
            coeff = float( coeff )
        elif coeff_type == 'bool':
            coeff = conditional( coeff == 'true', True, False )
        elif coeff_type == 'str':
            pass
        else:
            raise ValueError, "convert_to: Unknown coefficient type string '%s'" % coeff_type
    elif coeff_dim == 1:
        for r in xrange( len( coeff ) ):
            coeff[r] = convert_to( coeff[r], [ [ coeff_dim - 1 ], coeff_desc[1] , coeff_desc[2] ] )
    elif coeff_dim == 2:
        coeff_cols = coeff_desc[1][0]
        for c in xrange( coeff_cols ):
            coeff_type = coeff_desc[2][c]
            for r in xrange( len( coeff ) ):
                coeff[r][c] = convert_to( coeff[r][c], [ [ coeff_dim - 2 ], [ 1 ] , [ coeff_type ] ] )
    else:
        raise ValueError, "convert_to: Only dimensions 0, 1 and 2 supported. Have got %d" % coeff_dim
    
    return coeff


if __name__ == "__main__":
    baseDir = "C:/home/re04179/svn/GasNetworks/app/gnw/pulp/data/test/supplier-gas-terra-mup/pulp/data"
    
    coeff_dict = read_coeffs( baseDir ) 

    for strg_dict in coeff_dict['STRG_DICT_LIST']:
        print strg_dict['NAME'], "--------------------"  
        for k,v in strg_dict.iteritems():
            print k, "=", v
        print    

    for splr_dict in coeff_dict['SPLR_DICT_LIST']:
        print splr_dict['NAME'], "--------------------"  
        for k,v in splr_dict.iteritems():
            print k, "=", v
        print    

    for prd_dict in coeff_dict['PRD_DICT_LIST']:
        print prd_dict['NAME'], "--------------------"  
        for k,v in prd_dict.iteritems():
            print k, "=", v
        print
        
    for trn_dict in coeff_dict['TRN_DICT_LIST']:
        print trn_dict['NAME'], "--------------------"  
        for k,v in trn_dict.iteritems():
            print k, "=", v
        print
    
# ==============================================================================
#
#   Revision Control:
#
#   $Revision:: 1860                    $   Revision of last commit
#   $Author:: re04179                   $   Author of last commit
#   $Date:: 2009-09-07 14:09:18 +0200 (#$   Date of last commit
#
# ==============================================================================
