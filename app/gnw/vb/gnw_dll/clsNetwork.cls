VERSION 1.0 CLASS
BEGIN
  MultiUse = -1  'True
  Persistable = 0  'NotPersistable
  DataBindingBehavior = 0  'vbNone
  DataSourceBehavior  = 0  'vbNone
  MTSTransactionMode  = 0  'NotAnMTSObject
END
Attribute VB_Name = "Network"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = True
Attribute VB_PredeclaredId = False
Attribute VB_Exposed = True
'#  $Id: clsNetwork.cls 6679 2010-04-09 07:34:57Z re04179 $
'#  $URL: http://subversion.rwe.com/svn/s_and_v_projects/GasNetworks/trunk/app/gnw/vb/gnw_dll/clsNetwork.cls $
'#  $Revision: 6679 $
'#  $Date: 2010-04-09 09:34:57 +0200 (Fri, 09 Apr 2010) $
'#  $Author: re04179 $
Option Explicit
Option Base 0
Private Const ModuleVersion As String = "0pt2"

Private m_objective As Variant
Private m_mtm As Variant
Private m_status As Integer

Private m_name As String
Private m_strgArray() As gnw.Storage
Private m_splrArray() As gnw.Supplier
Private m_prdArray() As gnw.Product
Private m_trnArray() As gnw.Tranche
Private m_dspArray() As gnw.DispatchProduct
Private m_frmArray() As gnw.FirmProfile

Private m_dfArray() As Double
Private m_dpArray() As Double
Private m_fcArray() As Double

Private m_nStps As Long
Private m_nPnts As Long
Private m_nStrgs As Long
Private m_nSplrs As Long
Private m_nPrds As Long
Private m_nTrns As Long
Private m_nDsps As Long
Private m_nFrms As Long

Private m_gnwObj As Object

Public Function CreateStorage() As gnw.Storage
    Set CreateStorage = New gnw.Storage
End Function

Public Function CreateSupplier() As gnw.Supplier
    Set CreateSupplier = New gnw.Supplier
End Function

Public Function CreateProduct() As gnw.Product
    Set CreateProduct = New gnw.Product
End Function

Public Function CreateTranche() As gnw.Tranche
    Set CreateTranche = New gnw.Tranche
End Function

Public Function CreateDispatchProduct() As gnw.DispatchProduct
    Set CreateDispatchProduct = New gnw.DispatchProduct
End Function

Public Function CreateFirmProfile() As gnw.FirmProfile
    Set CreateFirmProfile = New gnw.FirmProfile
End Function


Public Property Get name() As String
    name = m_name
End Property


Private Sub Class_Initialize()
    Set m_gnwObj = CreateObject("RWEST.gnw.Network")
End Sub

Private Sub Class_Terminate()
    Set m_gnwObj = Nothing
    ClearStorageList
    ClearSupplierList
    ClearProductList
    ClearTrancheList
    ClearDispatchProductList
    ClearFirmProfileList
End Sub


Public Sub Initialise( _
        name As String, _
        strgArray() As gnw.Storage, _
        splrArray() As gnw.Supplier, _
        prdArray() As gnw.Product, _
        trnArray() As gnw.Tranche, _
        dspArray() As gnw.DispatchProduct, _
        frmArray() As gnw.FirmProfile, _
        dfArray() As Double, _
        dpArray() As Double, _
        fcArray() As Double, _
        Optional shortForm As Boolean = False)
    ' name          : unique network identifier
    ' strgArray     : array of gnw.Storage object references
    ' splrArray     : array of gnw.Supplier object references
    ' prdArray      : array of gnw.Product object references
    ' trnArray      : array of gnw.Tranche object references
    ' dspArray      : array of gnw.DispatchProduct object references
    ' frmArray      : array of gnw.FirmProfile object references
    ' dfArray       : array of discount factors of same length as dpArray
    ' dpArray       : array of dispatch periods in hours [h]
    ' fcArray       : 2-d array of size N x 3 where N is equal to the size of dpArray
    '                   and the 3 elements represent the bid/mid/ask price
    m_name = name
    
    If LBound(dfArray, 1) <> 0 _
    Or LBound(dpArray, 1) <> 0 _
    Or LBound(fcArray, 1) <> 0 _
    Or LBound(fcArray, 2) <> 0 Then
        Err.Raise vbObjectError + 12345, "gnw.Network::Initialise", "Zero-based arrays expected"
    End If
    If UBound(dfArray, 1) <> UBound(dpArray, 1) Then
        Err.Raise vbObjectError + 12345, "gnw.Network::Initialise", "array sizes of dfArray and dpArray must match"
    End If
    If UBound(fcArray, 1) <> UBound(dpArray, 1) _
    Or UBound(fcArray, 2) <> 2 Then
        Err.Raise vbObjectError + 12345, "gnw.Network::Initialise", "fcArray size mismatch"
    End If
    m_dfArray = dfArray
    m_dpArray = dpArray
    m_fcArray = fcArray
    
    m_nStps = UBound(m_dpArray, 1) + 1
    m_nPnts = m_nStps + 1
    
    Dim lb As Long, ub As Long
    
    m_nStrgs = 0
    ' belts & braces approach as in some cases
    ' just using the 'On Error' error trapping
    ' still failed to trap error from LBound
    ' or UBound call on an empty array!
    If Not IsEmpty(strgArray) Then
        On Error GoTo EmptyStrgInput
            lb = LBound(strgArray, 1)
            ub = UBound(strgArray, 1)
        On Error GoTo 0
        If lb <> 0 Then
            Err.Raise vbObjectError + 12345, "gnw.Network::Initialise", "Zero-based storage array expected (strgArray)"
        End If
        m_nStrgs = ub - lb + 1
    End If
EmptyStrgInput:

    m_nSplrs = 0
    If Not IsEmpty(splrArray) Then
        On Error GoTo EmptySplrInput
            lb = LBound(splrArray, 1)
            ub = UBound(splrArray, 1)
        On Error GoTo 0
        If lb <> 0 Then
            Err.Raise vbObjectError + 12345, "gnw.Network::Initialise", "Zero-based supplier array expected (splrArray)"
        End If
        m_nSplrs = ub - lb + 1
    End If
EmptySplrInput:

    m_nPrds = 0
    If Not IsEmpty(prdArray) Then
        On Error GoTo EmptyPrdInput
            lb = LBound(prdArray, 1)
            ub = UBound(prdArray, 1)
        On Error GoTo 0
        If lb <> 0 Then
            Err.Raise vbObjectError + 12345, "gnw.Network::Initialise", "Zero-based product array expected (prdArray)"
        End If
        m_nPrds = ub - lb + 1
    End If
EmptyPrdInput:

    m_nTrns = 0
    If Not IsEmpty(trnArray) Then
        On Error GoTo EmptyTrnInput
            lb = LBound(trnArray, 1)
            ub = UBound(trnArray, 1)
        On Error GoTo 0
        If lb <> 0 Then
            Err.Raise vbObjectError + 12345, "gnw.Network::Initialise", "Zero-based tranche array expected (trnArray)"
        End If
        m_nTrns = ub - lb + 1
    End If
EmptyTrnInput:
        
    m_nDsps = 0
    If Not IsEmpty(dspArray) Then
        On Error GoTo EmptyDspInput
            lb = LBound(dspArray, 1)
            ub = UBound(dspArray, 1)
        On Error GoTo 0
        If lb <> 0 Then
            Err.Raise vbObjectError + 12345, "gnw.Network::Initialise", "Zero-based tranche array expected (dspArray)"
        End If
        m_nDsps = ub - lb + 1
    End If
EmptyDspInput:

    m_nFrms = 0
    If Not IsEmpty(frmArray) Then
        On Error GoTo EmptyFrmInput
            lb = LBound(frmArray, 1)
            ub = UBound(frmArray, 1)
        On Error GoTo 0
        If lb <> 0 Then
            Err.Raise vbObjectError + 12345, "gnw.Network::Initialise", "Zero-based tranche array expected (frmArray)"
        End If
        m_nFrms = ub - lb + 1
    End If
EmptyFrmInput:
    
    ClearStorageList
    ClearSupplierList
    ClearProductList
    ClearTrancheList
    ClearDispatchProductList
    ClearFirmProfileList
    
    m_strgArray = strgArray
    m_splrArray = splrArray
    m_prdArray = prdArray
    m_trnArray = trnArray
    m_dspArray = dspArray
    m_frmArray = frmArray
    
    Dim niTupleArray As Variant
    niTupleArray = AsNamedItemArrayData(shortForm)
    m_gnwObj.set_all_data niTupleArray
End Sub
        
Public Sub SetSolver(niSolverTupleArray As Variant)
    Call m_gnwObj.set_solver(niSolverTupleArray)
End Sub

        
Public Function Optimise() As Integer
    ' returns: solver status
    Dim success As Boolean
    success = m_gnwObj.solve()
    Optimise = m_gnwObj.get_solver_status()
    If success Then
        m_objective = m_gnwObj.get_objective_value()
        m_mtm = m_gnwObj.get_mark_to_market_value()
    End If
End Function

Public Property Get Objective() As Double
    Objective = m_objective
End Property

Public Property Get MtMValue() As Double
    MtMValue = m_mtm
End Property

Public Function GetResults(strName As String) As Variant
    
    GetResults = Empty
    Select Case Trim$(LCase$(strName))
    Case "storage"
        GetResults = m_gnwObj.get_storage_results()
    Case "supplier"
        GetResults = m_gnwObj.get_supplier_results()
    Case "product"
        GetResults = m_gnwObj.get_product_results()
    Case "tranche"
        GetResults = m_gnwObj.get_tranche_results()
    Case "dispatch_product"
        GetResults = m_gnwObj.get_dispatch_product_results()
    Case "firm_profile"
        GetResults = m_gnwObj.get_firm_profile_results()
    End Select

End Function


Private Function AsNamedItemArrayData(Optional shortNamedItemForm As Boolean = False) As Variant
    Dim niHdlr As New gnw.NamedItemHdlr
    Dim idx As Long
    
    Dim niStrgArray() As gnw.NamedItem
    Dim strgNameArray() As String
    If m_nStrgs > 0 Then
        ReDim niStrgArray(0 To m_nStrgs - 1)
        ReDim strgNameArray(0 To m_nStrgs - 1)
        For idx = 0 To m_nStrgs - 1
            Set niStrgArray(idx) = m_strgArray(idx).AsNamedItem()
            strgNameArray(idx) = m_strgArray(idx).name
        Next idx
    End If
    Dim niStrgDict As gnw.NamedItem
    Set niStrgDict = niHdlr.Create("STRG_DICT_LIST", "array", Array("NI"), niStrgArray)
    
    Dim niSplrArray() As gnw.NamedItem
    Dim splrNameArray() As String
    If m_nSplrs > 0 Then
        ReDim niSplrArray(0 To m_nSplrs - 1)
        ReDim splrNameArray(0 To m_nSplrs - 1)
        For idx = 0 To m_nSplrs - 1
            Set niSplrArray(idx) = m_splrArray(idx).AsNamedItem()
            splrNameArray(idx) = m_splrArray(idx).name
        Next idx
    End If
    Dim niSplrDict As gnw.NamedItem
    Set niSplrDict = niHdlr.Create("SPLR_DICT_LIST", "array", Array("NI"), niSplrArray)
    
    Dim niPrdArray() As gnw.NamedItem
    Dim prdNameArray() As String
    If m_nPrds > 0 Then
        ReDim niPrdArray(0 To m_nPrds - 1)
        ReDim prdNameArray(0 To m_nPrds - 1)
        For idx = 0 To m_nPrds - 1
            Set niPrdArray(idx) = m_prdArray(idx).AsNamedItem()
            prdNameArray(idx) = m_prdArray(idx).name
        Next idx
    End If
    Dim niPrdDict As gnw.NamedItem
    Set niPrdDict = niHdlr.Create("PRD_DICT_LIST", "array", Array("NI"), niPrdArray)
    
    Dim niTrnArray() As gnw.NamedItem
    Dim trnNameArray() As String
    If m_nTrns > 0 Then
        ReDim niTrnArray(0 To m_nTrns - 1)
        ReDim trnNameArray(0 To m_nTrns - 1)
        For idx = 0 To m_nTrns - 1
            Set niTrnArray(idx) = m_trnArray(idx).AsNamedItem()
            trnNameArray(idx) = m_trnArray(idx).name
        Next idx
    End If
    Dim niTrnDict As gnw.NamedItem
    Set niTrnDict = niHdlr.Create("TRN_DICT_LIST", "array", Array("NI"), niTrnArray)

    Dim niDspArray() As gnw.NamedItem
    Dim dspNameArray() As String
    If m_nDsps > 0 Then
        ReDim niDspArray(0 To m_nDsps - 1)
        ReDim dspNameArray(0 To m_nDsps - 1)
        For idx = 0 To m_nDsps - 1
            Set niDspArray(idx) = m_dspArray(idx).AsNamedItem()
            dspNameArray(idx) = m_dspArray(idx).name
        Next idx
    End If
    Dim niDspDict As gnw.NamedItem
    Set niDspDict = niHdlr.Create("DSP_DICT_LIST", "array", Array("NI"), niDspArray)

    Dim niFrmArray() As gnw.NamedItem
    Dim frmNameArray() As String
    If m_nFrms > 0 Then
        ReDim niFrmArray(0 To m_nFrms - 1)
        ReDim frmNameArray(0 To m_nFrms - 1)
        For idx = 0 To m_nFrms - 1
            Set niFrmArray(idx) = m_frmArray(idx).AsNamedItem()
            frmNameArray(idx) = m_frmArray(idx).name
        Next idx
    End If
    Dim niFrmDict As gnw.NamedItem
    Set niFrmDict = niHdlr.Create("FRM_DICT_LIST", "array", Array("NI"), niFrmArray)

    
    Dim niGnrlDict As gnw.NamedItem
    Set niGnrlDict = _
        niHdlr.Create("GNRL_DICT", "array", Array("NI"), _
            Array( _
                niHdlr.Create("nSteps", "int", m_nStps), _
                niHdlr.Create("nPoints", "int", m_nPnts), _
                niHdlr.Create("dT", "float", 24#), _
                niHdlr.Create("nStrgs", "int", m_nStrgs), _
                niHdlr.Create("nSplrs", "int", m_nSplrs), _
                niHdlr.Create("nStdPrds", "int", m_nPrds), _
                niHdlr.Create("nTrdTrns", "int", m_nTrns), _
                niHdlr.Create("nDspPrds", "int", m_nDsps), _
                niHdlr.Create("nFrmPrfls", "int", m_nFrms), _
                niHdlr.Create("INFINITY", "float", 1E+16), _
                niHdlr.Create("STRG_NAMES", "array", Array("str"), strgNameArray), _
                niHdlr.Create("SPLR_NAMES", "array", Array("str"), splrNameArray), _
                niHdlr.Create("STDPRD_NAMES", "array", Array("str"), prdNameArray), _
                niHdlr.Create("TRDTRN_NAMES", "array", Array("str"), trnNameArray), _
                niHdlr.Create("DSPPRD_NAMES", "array", Array("str"), dspNameArray), _
                niHdlr.Create("FRMPRFL_NAMES", "array", Array("str"), frmNameArray)))
                
    Dim gnwMrkt As New gnw.Market
    gnwMrkt.Initialise m_dfArray, m_dpArray, m_fcArray
    
    Dim niMrktDict As gnw.NamedItem
    Set niMrktDict = gnwMrkt.AsNamedItem()
    
    AsNamedItemArrayData = Array( _
        niHdlr.AsArrayData(niGnrlDict, shortNamedItemForm), _
        niHdlr.AsArrayData(niMrktDict, shortNamedItemForm), _
        niHdlr.AsArrayData(niStrgDict, shortNamedItemForm), _
        niHdlr.AsArrayData(niSplrDict, shortNamedItemForm), _
        niHdlr.AsArrayData(niPrdDict, shortNamedItemForm), _
        niHdlr.AsArrayData(niTrnDict, shortNamedItemForm), _
        niHdlr.AsArrayData(niDspDict, shortNamedItemForm), _
        niHdlr.AsArrayData(niFrmDict, shortNamedItemForm))

    Set niHdlr = Nothing
    
    Set niGnrlDict = Nothing
    Set niMrktDict = Nothing
    Set niStrgDict = Nothing
    Set niSplrDict = Nothing
    Set niPrdDict = Nothing
    Set niTrnDict = Nothing
    Set niDspDict = Nothing
    Set niFrmDict = Nothing
End Function

Public Function GetEntity(name As String, instance_name As String) As Object
    Set GetEntity = m_gnwObj.get_entity(name, instance_name)
End Function

Public Function GetStorage(name As String) As Object
    Set GetStorage = m_gnwObj.get_storage(name)
End Function

Public Function GetSupplier(name As String) As Object
    Set GetSupplier = m_gnwObj.get_supplier(name)
End Function

Public Function GetProduct(name As String) As Object
    Set GetProduct = m_gnwObj.get_product(name)
End Function

Public Function GetTranche(name As String) As Object
    Set GetTranche = m_gnwObj.get_tranche(name)
End Function

Public Function GetDispatchProduct(name As String) As Object
    Set GetDispatchProduct = m_gnwObj.get_dispatch_product(name)
End Function

Public Function GetFirmProfile(name As String) As Object
    Set GetFirmProfile = m_gnwObj.get_firm_profile(name)
End Function

Private Sub ClearStorageList()
    Dim idx As Long, lb As Long, ub As Long
    
    If Not IsEmpty(m_strgArray) Then
        On Error GoTo ErrorTrap
            lb = LBound(m_strgArray, 1)
            ub = UBound(m_strgArray, 1)
        On Error GoTo 0
        If ub < lb Then GoTo ErrorTrap
        For idx = lb To ub
            Set m_strgArray(idx) = Nothing
        Next idx
        Erase m_strgArray
    End If
ErrorTrap:
End Sub

Private Sub ClearSupplierList()
    Dim idx As Long, lb As Long, ub As Long
    
    If Not IsEmpty(m_splrArray) Then
        On Error GoTo ErrorTrap
            lb = LBound(m_splrArray, 1)
            ub = UBound(m_splrArray, 1)
        On Error GoTo 0
        If ub < lb Then GoTo ErrorTrap
        For idx = lb To ub
            Set m_splrArray(idx) = Nothing
        Next idx
        Erase m_splrArray
    End If
ErrorTrap:
End Sub

Private Sub ClearProductList()
    Dim idx As Long, lb As Long, ub As Long
    
    If Not IsEmpty(m_prdArray) Then
        On Error GoTo ErrorTrap
            lb = LBound(m_prdArray, 1)
            ub = UBound(m_prdArray, 1)
        On Error GoTo 0
        If ub < lb Then GoTo ErrorTrap
        For idx = lb To ub
            Set m_prdArray(idx) = Nothing
        Next idx
        Erase m_prdArray
    End If
ErrorTrap:
End Sub

Private Sub ClearTrancheList()
    Dim idx As Long, lb As Long, ub As Long
    
    If Not IsEmpty(m_trnArray) Then
        On Error GoTo ErrorTrap
            lb = LBound(m_trnArray, 1)
            ub = UBound(m_trnArray, 1)
        On Error GoTo 0
        If ub < lb Then GoTo ErrorTrap
        For idx = lb To ub
            Set m_trnArray(idx) = Nothing
        Next idx
        Erase m_trnArray
    End If
ErrorTrap:
End Sub

Private Sub ClearDispatchProductList()
    Dim idx As Long, lb As Long, ub As Long
    
    If Not IsEmpty(m_dspArray) Then
        On Error GoTo ErrorTrap
            lb = LBound(m_dspArray, 1)
            ub = UBound(m_dspArray, 1)
        On Error GoTo 0
        If ub < lb Then GoTo ErrorTrap
        For idx = lb To ub
            Set m_dspArray(idx) = Nothing
        Next idx
        Erase m_dspArray
    End If
ErrorTrap:
End Sub

Private Sub ClearFirmProfileList()
    Dim idx As Long, lb As Long, ub As Long
    
    If Not IsEmpty(m_frmArray) Then
        On Error GoTo ErrorTrap
            lb = LBound(m_frmArray, 1)
            ub = UBound(m_frmArray, 1)
        On Error GoTo 0
        If ub < lb Then GoTo ErrorTrap
        For idx = lb To ub
            Set m_frmArray(idx) = Nothing
        Next idx
        Erase m_frmArray
    End If
ErrorTrap:
End Sub


