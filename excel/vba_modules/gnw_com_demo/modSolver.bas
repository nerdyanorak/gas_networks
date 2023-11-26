Attribute VB_Name = "modSolver"
Option Explicit
Option Base 1

Private Const ModuleVersion As String = "0pt2"

'Private Const SOLVER_URL As String = "http://s060a9230:8080/csgb-xpress/services/XpressExecutionServer?wsdl"
'Private Const SOLVER_URL As String = "http://xpressdev.rwe.com:8090/csgb-xpress/services/XpressExecutionServer?wsdl"
Private Const SOLVER_URL As String = "http://xpressprod.rwe.com:8080/csgb-xpress/services/XpressExecutionServer?wsdl"

Sub solve()

    Range(["SolverStatus"]) = "Solving..."
    Range(["ObjectiveValue"]) = "#N/A!"
    
    Dim currCursor
    currCursor = Application.Cursor
    Application.Cursor = xlWait
    Dim arrBase
    arrBase = Range(["Base"])
    Range(["Base"]) = 0
    
    Dim niHdlr As gnw.NamedItemHdlr
    Set niHdlr = New gnw.NamedItemHdlr
    
    Dim gnrl_data() As Variant
    gnrl_data = gnw_addin.NamedItemArrayType1("b11", "General")
    Dim niGnrlData As Variant
    Set niGnrlData = niHdlr.Create("GNRL_DICT", "array", Array("NI"), gnrl_data)
    
    Dim mrkt_data() As Variant
    mrkt_data = gnw_addin.NamedItemArrayType1("b11", "Market")
    Dim niMrktData As Variant
    Set niMrktData = niHdlr.Create("MRKT_DICT", "array", Array("NI"), mrkt_data)
    
    Dim strg_data() As Variant
    If Range(["nStrgs"]) > 0 Then
        strg_data = gnw_addin.NamedItemArrayType1b("d11", "Storage", Range(["nStrgs"]), Range(["numEntriesPerStorage"]))
    End If
    Dim niStrgData As Variant
    Set niStrgData = niHdlr.Create("STRG_DICT_LIST", "array", Array("NI"), strg_data)
    
    Dim splr_data() As Variant
    If Range(["nSplrs"]) > 0 Then
        splr_data = gnw_addin.NamedItemArrayType1b("d11", "Supplier", Range(["nSplrs"]), Range(["numEntriesPerSupplier"]))
    End If
    Dim niSplrData As Variant
    Set niSplrData = niHdlr.Create("SPLR_DICT_LIST", "array", Array("NI"), splr_data)
    
    Dim prd_data() As Variant
    prd_data = gnw_addin.NamedItemArrayType2("g10", "g8", "g11", "StdPrdDef")
    Dim niPrdData As Variant
    Set niPrdData = niHdlr.Create("PRD_DICT_LIST", "array", Array("NI"), prd_data)
    
    Dim trn_data() As Variant
    trn_data = gnw_addin.NamedItemArrayType2("h10", "h8", "h11", "TrdTrnDef")
    Dim niTrnData As Variant
    Set niTrnData = niHdlr.Create("TRN_DICT_LIST", "array", Array("NI"), trn_data)
    
    Dim niTupleArray As Variant
    niTupleArray = Array( _
            niHdlr.AsArrayData(niGnrlData), _
            niHdlr.AsArrayData(niMrktData), _
            niHdlr.AsArrayData(niStrgData), _
            niHdlr.AsArrayData(niSplrData), _
            niHdlr.AsArrayData(niPrdData), _
            niHdlr.AsArrayData(niTrnData))
    
    Set niHdlr = Nothing
    
    Dim gnwNtwrkObj As Object
    Set gnwNtwrkObj = CreateObject("RWEST.gnw.Network")
    
    Dim niSolverTupleArray As Variant
    niSolverTupleArray = CreateSolverParams(SOLVER_URL)
    gnwNtwrkObj.set_solver niSolverTupleArray
    
    gnwNtwrkObj.set_all_data niTupleArray
    
    Dim success As Boolean
    success = gnwNtwrkObj.solve()
    
    Range(["SolverStatus"]) = gnwNtwrkObj.get_solver_status()
    Range(["ObjectiveValue"]) = gnwNtwrkObj.get_objective_value()
    
    If success Then
        Dim rslt As Variant
        rslt = gnwNtwrkObj.get_storage_results()
        Call writeResultsTransposed(rslt, "StorageRslt", "b11")
        
        rslt = gnwNtwrkObj.get_supplier_results()
        Call writeResultsTransposed(rslt, "SupplierRslt", "b11")
        
''       ###
'        Dim gnwSplrObj As Object
'        Set gnwSplrObj = gnwNtwrkObj.get_supplier("splr_gasexport")
'
'        Dim keys As Variant
'        keys = gnwSplrObj.get_keys()
'
'        rslt = gnwSplrObj.get_lp_var_values(Array("pos_pct", "vol"))
'        rslt = gnwSplrObj.get_lp_var_values(Array("mup_period_vol", "mup_period_vol_chg"))
'        rslt = gnwSplrObj.get_lp_var_values(Array("cfw_period_vol", "cfw_period_vol_chg"))
'
'        Set gnwSplrObj = Nothing
''       ###
    
        rslt = gnwNtwrkObj.get_product_results()
        Call writeResults(rslt, "StdPrdRslt", "b11")
    
        rslt = gnwNtwrkObj.get_tranche_results()
        Call writeResults(rslt, "TrdTrnRslt", "b11")
    
    End If
    
    Set gnwNtwrkObj = Nothing
    
    Range(["Base"]) = arrBase
'    Application.Cursor = currCursor
    Application.Cursor = xlDefault

End Sub

Sub solve2()
    
    Range(["SolverStatus"]) = "Solving..."
    Range(["ObjectiveValue"]) = "#N/A!"
    
    Dim currCursor
    currCursor = Application.Cursor
    Application.Cursor = xlWait
    Dim arrBase
    arrBase = Range(["Base"])
    Range(["Base"]) = 0
    
    Dim niHdlr As gnw.NamedItemHdlr
    Set niHdlr = New gnw.NamedItemHdlr
    
    Dim gnrl_data() As Variant
    gnrl_data = gnw_addin.NamedItemArrayType1("b11", "General")
    Dim niGnrlData As Variant
    Set niGnrlData = niHdlr.Create("GNRL_DICT", "array", Array("NI"), gnrl_data)
    
    Dim mrkt_data() As Variant
    mrkt_data = gnw_addin.NamedItemArrayType1("b11", "Market")
    Dim niMrktData As Variant
    Set niMrktData = niHdlr.Create("MRKT_DICT", "array", Array("NI"), mrkt_data)
    
    Dim strg_data() As Variant
    strg_data = gnw_addin.NamedItemArrayType1b("d11", "Storage", Range(["nStrgs"]), Range(["numEntriesPerStorage"]))
    Dim lbStrg As Long, ubStrg As Long, nStrgs As Long
    lbStrg = LBound(strg_data, 1)
    ubStrg = UBound(strg_data, 1)
    nStrgs = ubStrg - lbStrg + 1
    
    Dim splr_data() As Variant
    splr_data = gnw_addin.NamedItemArrayType1b("d11", "Supplier", Range(["nSplrs"]), Range(["numEntriesPerSupplier"]))
    Dim lbSplr As Long, ubSplr As Long, nSplrs As Long
    lbSplr = LBound(splr_data, 1)
    ubSplr = UBound(splr_data, 1)
    nSplrs = ubSplr - lbSplr + 1
    
    Dim prd_data() As Variant
    prd_data = gnw_addin.NamedItemArrayType2("g10", "g8", "g11", "StdPrdDef")
    Dim lbPrd As Long, ubPrd As Long, nPrds As Long
    lbPrd = LBound(prd_data, 1)
    ubPrd = UBound(prd_data, 1)
    nPrds = ubPrd - lbPrd + 1
    
    Dim trn_data() As Variant
    trn_data = gnw_addin.NamedItemArrayType2("h10", "h8", "h11", "TrdTrnDef")
    Dim lbTrn As Long, ubTrn As Long, nTrns As Long
    lbTrn = LBound(trn_data, 1)
    ubTrn = UBound(trn_data, 1)
    nTrns = ubTrn - lbTrn + 1
    
    
    Dim lb As Long, ub As Long, nEntities As Long
    nEntities = nStrgs + nSplrs + nPrds + nTrns
    lb = 1
    ub = lb + nEntities - 1
    Dim gnwEntityArray() As Object
    ReDim gnwEntityArray(lb To ub) As Object
    
    
    Dim eIdx As Long, idx As Long
    Dim niData As NamedItem
    Dim niTupleArray As Variant
    
    eIdx = lb
    If nStrgs > 0 Then
        For idx = lbStrg To ubStrg
            Set niData = niHdlr.Create("STRG_DICT", "array", strg_data(idx).Types, strg_data(idx).Data)
            niTupleArray = Array(niHdlr.AsArrayData(niMrktData), niHdlr.AsArrayData(niData))
            
            Set gnwEntityArray(eIdx) = CreateObject("RWEST.gnw.Storage")
            gnwEntityArray(eIdx).set_data niTupleArray
            eIdx = eIdx + 1
        Next idx
    End If
    If nSplrs > 0 Then
        For idx = lbSplr To ubSplr
            Set niData = niHdlr.Create("SPLR_DICT", "array", splr_data(idx).Types, splr_data(idx).Data)
            niTupleArray = Array(niHdlr.AsArrayData(niMrktData), niHdlr.AsArrayData(niData))
            
            Set gnwEntityArray(eIdx) = CreateObject("RWEST.gnw.Supplier")
            gnwEntityArray(eIdx).set_data niTupleArray
            eIdx = eIdx + 1
        Next idx
    End If
    If nPrds > 0 Then
        For idx = lbPrd To ubPrd
            Set niData = niHdlr.Create("PRD_DICT", "array", prd_data(idx).Types, prd_data(idx).Data)
            niTupleArray = Array(niHdlr.AsArrayData(niMrktData), niHdlr.AsArrayData(niData))
            
            Set gnwEntityArray(eIdx) = CreateObject("RWEST.gnw.Product")
            gnwEntityArray(eIdx).set_data niTupleArray
            eIdx = eIdx + 1
        Next idx
    End If
    If nTrns > 0 Then
        For idx = lbTrn To ubTrn
            Set niData = niHdlr.Create("TRN_DICT", "array", trn_data(idx).Types, trn_data(idx).Data)
            niTupleArray = Array(niHdlr.AsArrayData(niMrktData), niHdlr.AsArrayData(niData))
            
            Set gnwEntityArray(eIdx) = CreateObject("RWEST.gnw.Tranche")
            gnwEntityArray(eIdx).set_data niTupleArray
            eIdx = eIdx + 1
        Next idx
    End If
    
    Dim ntwrk_name As NamedItem
    Set ntwrk_name = niHdlr.Create("NAME", "str", "GNW-Network")
    Dim niNtwrkData As NamedItem
    Set niNtwrkData = niHdlr.Create("NTWRK_DICT", "array", Array("NI"), Array(ntwrk_name))
    
    niTupleArray = Array(niHdlr.AsArrayData(niMrktData), niHdlr.AsArrayData(niNtwrkData))
    
    Set niHdlr = Nothing
    
    Dim gnwNtwrkObj As Object
    Set gnwNtwrkObj = CreateObject("RWEST.gnw.Network")
    
    Dim niSolverTupleArray As Variant
    niSolverTupleArray = CreateSolverParams(SOLVER_URL)
    gnwNtwrkObj.set_solver niSolverTupleArray
    
    gnwNtwrkObj.set_data niTupleArray
    
    gnwNtwrkObj.set_entities gnwEntityArray
   
    Dim success As Boolean
    success = gnwNtwrkObj.solve()
    Range(["SolverStatus"]) = gnwNtwrkObj.get_solver_status()
    Range(["ObjectiveValue"]) = gnwNtwrkObj.get_objective_value()

    Set gnwNtwrkObj = Nothing
    
    Range(["Base"]) = arrBase
'    Application.Cursor = currCursor
    Application.Cursor = xlDefault
    
End Sub

Sub solve3()
    
    Range(["SolverStatus"]) = "Solving..."
    Range(["ObjectiveValue"]) = "#N/A!"
    
    Dim currCursor
    currCursor = Application.Cursor
    Application.Cursor = xlWait
    Dim arrBase
    arrBase = Range(["Base"])
    Range(["Base"]) = 0
    
    Dim niHdlr As gnw.NamedItemHdlr
    Set niHdlr = New gnw.NamedItemHdlr
    
    Dim gnrl_data() As Variant
    gnrl_data = gnw_addin.NamedItemArrayType1("b11", "General")
    Dim niGnrlData As Variant
    Set niGnrlData = niHdlr.Create("GNRL_DICT", "array", Array("NI"), gnrl_data)
    
    Dim mrkt_data() As Variant
    mrkt_data = gnw_addin.NamedItemArrayType1("b11", "Market")
    Dim niMrktData As Variant
    Set niMrktData = niHdlr.Create("MRKT_DICT", "array", Array("NI"), mrkt_data)
    
    Dim lb As Long, ub As Long
    Dim idx As Long
    Dim niData As NamedItem
    Dim niTupleArray As Variant

    Dim ntwrk_name As NamedItem
    Set ntwrk_name = niHdlr.Create("NAME", "str", "GNW-Network")
    Dim niNtwrkData As NamedItem
    Set niNtwrkData = niHdlr.Create("NTWRK_DICT", "array", Array("NI"), Array(ntwrk_name))
    
    niTupleArray = Array(niHdlr.AsArrayData(niMrktData), niHdlr.AsArrayData(niNtwrkData))
    
    Dim gnwNtwrkObj As Object
    Set gnwNtwrkObj = CreateObject("RWEST.gnw.Network")
    
    Dim niSolverTupleArray As Variant
    niSolverTupleArray = CreateSolverParams(SOLVER_URL)
    gnwNtwrkObj.set_solver niSolverTupleArray
    
    gnwNtwrkObj.set_data niTupleArray
    
    Dim strg_data() As Variant
    strg_data = gnw_addin.NamedItemArrayType1b("d11", "Storage", Range(["nStrgs"]), Range(["numEntriesPerStorage"]))
    lb = LBound(strg_data, 1)
    ub = UBound(strg_data, 1)
    Dim gnwStrgArray() As Object
    ReDim gnwStrgArray(lb To ub) As Object
    
    For idx = lb To ub
        Set niData = niHdlr.Create("STRG_DICT", "array", strg_data(idx).Types, strg_data(idx).Data)
        niTupleArray = Array(niHdlr.AsArrayData(niMrktData), niHdlr.AsArrayData(niData))
        Set gnwStrgArray(idx) = gnwNtwrkObj.create_storage(niTupleArray)
        gnwNtwrkObj.add_entity gnwStrgArray(idx)
    Next idx
    
    Dim splr_data() As Variant
    splr_data = gnw_addin.NamedItemArrayType1b("d11", "Supplier", Range(["nSplrs"]), Range(["numEntriesPerSupplier"]))
    lb = LBound(splr_data, 1)
    ub = UBound(splr_data, 1)
    Dim gnwSplrArray() As Object
    ReDim gnwSplrArray(ub To lb) As Object
    
    For idx = lb To ub
        Set niData = niHdlr.Create("SPLR_DICT", "array", splr_data(idx).Types, splr_data(idx).Data)
        niTupleArray = Array(niHdlr.AsArrayData(niMrktData), niHdlr.AsArrayData(niData))
        Set gnwSplrArray(idx) = gnwNtwrkObj.create_supplier(niTupleArray)
        gnwNtwrkObj.add_entity gnwSplrArray(idx)
    Next idx
    
    Dim prd_data() As Variant
    prd_data = gnw_addin.NamedItemArrayType2("g10", "g8", "g11", "StdPrdDef")
    lb = LBound(prd_data, 1)
    ub = UBound(prd_data, 1)
    Dim gnwPrdArray() As Object
    ReDim gnwPrdArray(lb To ub) As Object
    
    For idx = lb To ub
        Set niData = niHdlr.Create("PRD_DICT", "array", prd_data(idx).Types, prd_data(idx).Data)
        niTupleArray = Array(niHdlr.AsArrayData(niMrktData), niHdlr.AsArrayData(niData))
        Set gnwPrdArray(idx) = gnwNtwrkObj.create_product(niTupleArray)
        gnwNtwrkObj.add_entity gnwPrdArray(idx)
    Next idx
    
    
    Dim trn_data() As Variant
    trn_data = gnw_addin.NamedItemArrayType2("h10", "h8", "h11", "TrdTrnDef")
    lb = LBound(trn_data, 1)
    ub = UBound(trn_data, 1)
    Dim gnwTrnArray() As Object
    ReDim gnwTrnArray(lb To ub) As Object
    
    For idx = lb To ub
        Set niData = niHdlr.Create("TRN_DICT", "array", trn_data(idx).Types, trn_data(idx).Data)
        niTupleArray = Array(niHdlr.AsArrayData(niMrktData), niHdlr.AsArrayData(niData))
        Set gnwTrnArray(idx) = gnwNtwrkObj.create_tranche(niTupleArray)
        gnwNtwrkObj.add_entity gnwTrnArray(idx)
    Next idx
    
    Set niHdlr = Nothing
    
    Dim success As Boolean
    success = gnwNtwrkObj.solve()
    Range(["SolverStatus"]) = gnwNtwrkObj.get_solver_status()
    Range(["ObjectiveValue"]) = gnwNtwrkObj.get_objective_value()
    
    Set gnwNtwrkObj = Nothing
    
    Range(["Base"]) = arrBase
'    Application.Cursor = currCursor
    Application.Cursor = xlDefault
    
End Sub

Function CreateSolverParams(url As String, _
        Optional mip_rel_cutoff As Double = 0.0001, _
        Optional mip_rel_stop As Double = 0.005, _
        Optional time_limit As Double = 0#) As Variant
    Dim solver_name As String
    Dim mip_rel_cutoff_attr As Double
    Dim mip_rel_stop_attr As Double
    Dim time_limit_attr As Double
    Dim url_attr As String
    
'        self.solver_dict = {'name' : 'XPRESS_REMOTE_CLIENT',
'                            'attr' : {'MIPRELCUTOFF' : 1.0e-4,
'                                      'MIPRELSTOP' : 0.005,
'                                      'URL' : "http://s060a9230:8080/csgb-xpress/services/XpressExecutionServer?wsdl"}}
    solver_name = "XPRESS_REMOTE_CLIENT"
    url_attr = url
    mip_rel_cutoff_attr = mip_rel_cutoff
    mip_rel_stop_attr = mip_rel_stop
    time_limit_attr = time_limit
    
    Dim niHdlr As gnw.NamedItemHdlr
    Set niHdlr = New gnw.NamedItemHdlr
    
    
    Dim niName As gnw.NamedItem
    Set niName = niHdlr.Create("name", "str", solver_name)
    
    Dim niMipRelCutoffAttr As gnw.NamedItem
    Dim niMipRelStopAttr As gnw.NamedItem
    Dim niTimeLimitAttr As gnw.NamedItem
    Dim niUrlAttr As gnw.NamedItem
    
    Set niMipRelCutoffAttr = niHdlr.Create("MIPRELCUTOFF", "float", mip_rel_cutoff_attr)
    Set niMipRelStopAttr = niHdlr.Create("MIPRELSTOP", "float", mip_rel_stop_attr)
    Set niTimeLimitAttr = niHdlr.Create("TIMELIMIT", "float", time_limit_attr)
    Set niUrlAttr = niHdlr.Create("URL", "str", url_attr)
    
    Dim niAttrArray As Variant
    niAttrArray = Array(niMipRelCutoffAttr, _
                        niMipRelStopAttr, _
                        niUrlAttr)
                        
    Dim niAttr As gnw.NamedItem
    Set niAttr = niHdlr.Create("attr", "array", Array("NI"), niAttrArray)
                        
    CreateSolverParams = Array(niHdlr.AsArrayData(niName), niHdlr.AsArrayData(niAttr))
    
    Set niHdlr = Nothing
End Function

