VERSION 1.0 CLASS
BEGIN
  MultiUse = -1  'True
  Persistable = 0  'NotPersistable
  DataBindingBehavior = 0  'vbNone
  DataSourceBehavior  = 0  'vbNone
  MTSTransactionMode  = 0  'NotAnMTSObject
END
Attribute VB_Name = "NetworkMIP"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = True
Attribute VB_PredeclaredId = False
Attribute VB_Exposed = True
'#  $Id: clsNetworkMIP.cls 6857 2010-04-16 09:39:02Z re04179 $
'#  $URL: http://subversion.rwe.com/svn/s_and_v_projects/GasNetworks/trunk/app/gnw/vb/gnw_dll/clsNetworkMIP.cls $
'#  $Revision: 6857 $
'#  $Date: 2010-04-16 11:39:02 +0200 (Fri, 16 Apr 2010) $
'#  $Author: re04179 $
Option Explicit
Option Base 0

Private Const ModuleVersion As String = "0pt2"

Private m_niHdlr As gnw.NamedItemHdlr

Private m_prblm_name As String
Private m_ntwrk As gnw.Network
Private m_strg_list() As gnw.Storage
Private m_splr_list() As gnw.Supplier
Private m_prd_list() As gnw.Product
Private m_trn_list() As gnw.Tranche
Private m_dsp_list() As gnw.DispatchProduct
Private m_frm_list() As gnw.FirmProfile

Private Sub Class_Initialize()
    Set m_niHdlr = New gnw.NamedItemHdlr
    Set m_ntwrk = New gnw.Network
End Sub

Private Sub Class_Terminate()
    Set m_niHdlr = Nothing
    Set m_ntwrk = Nothing
    ClearStorageList
    ClearSupplierList
    ClearProductList
    ClearTrancheList
    ClearDispatchProductList
    ClearFirmProfileList
End Sub

Public Sub Initialise( _
        prblm_name As String, _
        ntwrk_name As String, _
        dispatch_period() As Double, _
        fwd_curve() As Double, _
        discount_factor() As Double, _
        strg_input_list() As gnw.StorageInputType, _
        splr_input_list() As gnw.SupplierInputType, _
        prd_input_list() As gnw.ProductInputType, _
        trn_input_list() As gnw.TrancheInputType, _
        dsp_input_list() As gnw.DispatchProductInputType, _
        frm_input_list() As gnw.FirmProfileInputType, _
        Optional shortNamedItemForm As Boolean = False)

    Dim idx As Long
    Dim lb As Long, ub As Long
    
    ClearStorageList
    If Not IsEmpty(strg_input_list) Then
        On Error GoTo EmptyStrgInput
            lb = LBound(strg_input_list, 1)
            ub = UBound(strg_input_list, 1)
        On Error GoTo 0
        If ub < lb Then GoTo EmptyStrgInput
        ReDim m_strg_list(ub - lb) As gnw.Storage
        For idx = 0 To ub - lb
            Set m_strg_list(idx) = New gnw.Storage
            Call m_strg_list(idx).InitialiseFromInputType(strg_input_list(lb + idx))
        Next idx
    End If
EmptyStrgInput:

    ClearSupplierList
    If Not IsEmpty(splr_input_list) Then
        On Error GoTo EmptySplrInput
            lb = LBound(splr_input_list, 1)
            ub = UBound(splr_input_list, 1)
        On Error GoTo 0
        If ub < lb Then GoTo EmptySplrInput
        ReDim m_splr_list(ub - lb) As gnw.Supplier
        For idx = 0 To ub - lb
            Set m_splr_list(idx) = New gnw.Supplier
            Call m_splr_list(idx).InitialiseFromInputType(splr_input_list(lb + idx))
        Next idx
    End If
EmptySplrInput:

    ClearProductList
    If Not IsEmpty(prd_input_list) Then
        On Error GoTo EmptyPrdInput
            lb = LBound(prd_input_list, 1)
            ub = UBound(prd_input_list, 1)
        On Error GoTo 0
        If ub < lb Then GoTo EmptyPrdInput
        ReDim m_prd_list(ub - lb) As gnw.Product
        For idx = 0 To ub - lb
            Set m_prd_list(idx) = New gnw.Product
            Call m_prd_list(idx).InitialiseFromInputType(prd_input_list(lb + idx))
        Next idx
    End If
EmptyPrdInput:

    ClearTrancheList
    If Not IsEmpty(trn_input_list) Then
        On Error GoTo EmptyTrnInput
            lb = LBound(trn_input_list, 1)
            ub = UBound(trn_input_list, 1)
        On Error GoTo 0
        If ub < lb Then GoTo EmptyTrnInput
        ReDim m_trn_list(ub - lb) As gnw.Tranche
        For idx = 0 To ub - lb
            Set m_trn_list(idx) = New gnw.Tranche
            Call m_trn_list(idx).InitialiseFromInputType(trn_input_list(lb + idx))
        Next idx
    End If
EmptyTrnInput:

    ClearDispatchProductList
    If Not IsEmpty(dsp_input_list) Then
        On Error GoTo EmptyDspInput
            lb = LBound(dsp_input_list, 1)
            ub = UBound(dsp_input_list, 1)
        On Error GoTo 0
        If ub < lb Then GoTo EmptyDspInput
        ReDim m_dsp_list(ub - lb) As gnw.DispatchProduct
        For idx = 0 To ub - lb
            Set m_dsp_list(idx) = New gnw.DispatchProduct
            Call m_dsp_list(idx).InitialiseFromInputType(dsp_input_list(lb + idx))
        Next idx
    End If
EmptyDspInput:

    ClearFirmProfileList
    If Not IsEmpty(frm_input_list) Then
        On Error GoTo EmptyFrmInput
            lb = LBound(frm_input_list, 1)
            ub = UBound(frm_input_list, 1)
        On Error GoTo 0
        If ub < lb Then GoTo EmptyFrmInput
        ReDim m_frm_list(ub - lb) As gnw.FirmProfile
        For idx = 0 To ub - lb
            Set m_frm_list(idx) = New gnw.FirmProfile
            Call m_frm_list(idx).InitialiseFromInputType(frm_input_list(lb + idx))
        Next idx
    End If
EmptyFrmInput:

    m_prblm_name = prblm_name
    Call m_ntwrk.Initialise(ntwrk_name, _
                    m_strg_list, m_splr_list, m_prd_list, m_trn_list, m_dsp_list, m_frm_list, _
                    discount_factor, _
                    dispatch_period, _
                    fwd_curve, _
                    shortNamedItemForm)
End Sub


Public Sub SetSolver( _
        Optional url As String = "http://s060a9230:8080/csgb-xpress/services/XpressExecutionServer?wsdl", _
        Optional mip_rel_cutoff As Double = 0.0001, _
        Optional mip_rel_stop As Double = 0.005, _
        Optional time_limit As Long = 0, _
        Optional shortNamedItemForm As Boolean = False)
        
    Dim niSolverTupleArray As Variant
    
'        self.solver_dict = {'name' : 'XPRESS_REMOTE_CLIENT',
'                            'attr' : {'MIPRELCUTOFF' : 1.0e-4,
'                                      'MIPRELSTOP' : 0.005,
'                                      'TIMELIMIT' : 0,
'                                      'URL' : "http://s060a9230:8080/csgb-xpress/services/XpressExecutionServer?wsdl"}}
    Dim solver_name As String
    Dim url_attr As String
    Dim mip_rel_cutoff_attr As Double
    Dim mip_rel_stop_attr As Double
    Dim time_limit_attr As Double
    
    solver_name = "XPRESS_REMOTE_CLIENT"
    url_attr = url
    mip_rel_cutoff_attr = mip_rel_cutoff
    mip_rel_stop_attr = mip_rel_stop
    time_limit_attr = time_limit
    
    Dim niName As gnw.NamedItem
    Set niName = m_niHdlr.Create("name", "str", solver_name)
    
    Dim niMipRelCutoffAttr As gnw.NamedItem
    Dim niMipRelStopAttr As gnw.NamedItem
    Dim niTimeLimitAttr As gnw.NamedItem
    Dim niUrlAttr As gnw.NamedItem
    
    Set niMipRelCutoffAttr = m_niHdlr.Create("MIPRELCUTOFF", "float", mip_rel_cutoff_attr)
    Set niMipRelStopAttr = m_niHdlr.Create("MIPRELSTOP", "float", mip_rel_stop_attr)
    Set niTimeLimitAttr = m_niHdlr.Create("TIMELIMIT", "float", time_limit_attr)
    Set niUrlAttr = m_niHdlr.Create("URL", "str", url_attr)
    
    Dim niAttrArray As Variant
    niAttrArray = Array(niMipRelCutoffAttr, _
                        niMipRelStopAttr, _
                        niUrlAttr)
                        
    Dim niAttr As gnw.NamedItem
    Set niAttr = m_niHdlr.Create("attr", "array", Array("NI"), niAttrArray)
                        
    niSolverTupleArray = Array(m_niHdlr.AsArrayData(niName, shortNamedItemForm), m_niHdlr.AsArrayData(niAttr, shortNamedItemForm))
        
    Call m_ntwrk.SetSolver(niSolverTupleArray)
        
    Set niName = Nothing
    Set niAttr = Nothing
End Sub

Public Sub SetSolver2( _
        Optional name As String = "XPRESS_REMOTE_CLIENT", _
        Optional attr As Variant, _
        Optional shortNamedItemForm As Boolean = False)
'   attr_names: array of size n holding names of attributes like 'MIPRELSTOP' and 'URL'
'   attr_types: array of size n holding the types of the attributes like 'float', 'str', 'int', 'bool'
'   attr_types: array of size n holding the values of the attributes corresponding to attr_types
'
'        self.solver_dict = {'name' : 'XPRESS_REMOTE_CLIENT',
'                            'attr' : {'MIPRELCUTOFF' : 1.0e-4,
'                                      'MIPRELSTOP' : 0.005,
'                                      'TIMELIMIT' : 0,
'                                      'URL' : "http://s060a9230:8080/csgb-xpress/services/XpressExecutionServer?wsdl"}}

    Dim niName As gnw.NamedItem
    Set niName = m_niHdlr.Create("name", "str", name)

    Dim niAttr As gnw.NamedItem
    Set niAttr = m_niHdlr.Create("attr", "array", Array("NI"), Array())

    Dim niSolverTupleArray As Variant
    niSolverTupleArray = Array(m_niHdlr.AsArrayData(niName, shortNamedItemForm), m_niHdlr.AsArrayData(niAttr, shortNamedItemForm))

On Error GoTo NoAttributes
    Dim lb1 As Long, ub1 As Long
    lb1 = LBound(attr, 1)
    ub1 = UBound(attr, 1)
On Error GoTo 0
    
    Dim niAttrArray() As gnw.NamedItem
    ReDim niAttrArray(ub1 - lb1)
    Dim idx As Long
    For idx = 0 To ub1 - lb1
        Set niAttrArray(idx) = m_niHdlr.Create(CStr(attr(lb1 + idx, 0)), CStr(attr(lb1 + idx, 1)), attr(lb1 + idx, 2))
    Next idx
    
    Set niAttr = m_niHdlr.Create("attr", "array", Array("NI"), niAttrArray)
                        
    niSolverTupleArray = Array(m_niHdlr.AsArrayData(niName, shortNamedItemForm), m_niHdlr.AsArrayData(niAttr, shortNamedItemForm))
NoAttributes:
On Error GoTo 0

    Call m_ntwrk.SetSolver(niSolverTupleArray)
    
    Set niName = Nothing
    Set niAttr = Nothing
End Sub

Public Function Optimise() As Integer
    Optimise = m_ntwrk.Optimise()
End Function

Public Function GetObjective() As Double
    GetObjective = m_ntwrk.Objective
End Function

Public Function GetMtMValue() As Double
    GetMtMValue = m_ntwrk.MtMValue
End Function

Public Function GetGeneralResults() As Variant
    GetGeneralResults = m_ntwrk.GetResults("general")
End Function
Public Function GetMarketResults() As Variant
    GetMarketResults = m_ntwrk.GetResults("market")
End Function
Public Function GetStorageResults() As Variant
    GetStorageResults = m_ntwrk.GetResults("storage")
End Function
Public Function GetSupplierResults() As Variant
    GetSupplierResults = m_ntwrk.GetResults("supplier")
End Function
Public Function GetProductResults() As Variant
    GetProductResults = m_ntwrk.GetResults("product")
End Function
Public Function GetTrancheResults() As Variant
    GetTrancheResults = m_ntwrk.GetResults("tranche")
End Function
Public Function GetDispatchProductResults() As Variant
    GetDispatchProductResults = m_ntwrk.GetResults("dispatch_product")
End Function
Public Function GetFirmProfileResults() As Variant
    GetFirmProfileResults = m_ntwrk.GetResults("firm_profile")
End Function

Public Function GetEntity(name As String, entity_type As Integer) As Object
    Set GetEntity = Nothing
    Dim instance_name As String
    
    Dim etObj As New gnw.CEntityTypeEnum
    instance_name = etObj.GetEntityInstanceName(entity_type)
    Set etObj = Nothing
    
    Set GetEntity = m_ntwrk.GetEntity(name, instance_name)
End Function


Public Function GetStorage(name As String) As Object
    Set GetStorage = m_ntwrk.GetStorage(name)
End Function

Public Function GetSupplier(name As String) As Object
    Set GetSupplier = m_ntwrk.GetSupplier(name)
End Function

Public Function GetProduct(name As String) As Object
    Set GetProduct = m_ntwrk.GetProduct(name)
End Function

Public Function GetTranche(name As String) As Object
    Set GetTranche = m_ntwrk.GetTranche(name)
End Function

Public Function GetDispatchProduct(name As String) As Object
    Set GetDispatchProduct = m_ntwrk.GetDispatchProduct(name)
End Function

Public Function GetFirmProfile(name As String) As Object
    Set GetFirmProfile = m_ntwrk.GetFirmProfile(name)
End Function


Private Sub ClearStorageList()
    Dim idx As Long, lb As Long, ub As Long
    
    If Not IsEmpty(m_strg_list) Then
        On Error GoTo ErrorTrap
            lb = LBound(m_strg_list, 1)
            ub = UBound(m_strg_list, 1)
        On Error GoTo 0
        If ub < lb Then GoTo ErrorTrap
        For idx = lb To ub
            Set m_strg_list(idx) = Nothing
        Next idx
        Erase m_strg_list
    End If
ErrorTrap:
End Sub

Private Sub ClearSupplierList()
    Dim idx As Long, lb As Long, ub As Long
    
    If Not IsEmpty(m_splr_list) Then
        On Error GoTo ErrorTrap
            lb = LBound(m_splr_list, 1)
            ub = UBound(m_splr_list, 1)
        On Error GoTo 0
        If ub < lb Then GoTo ErrorTrap
        For idx = lb To ub
            Set m_splr_list(idx) = Nothing
        Next idx
        Erase m_splr_list
    End If
ErrorTrap:
End Sub

Private Sub ClearProductList()
    Dim idx As Long, lb As Long, ub As Long
    
    If Not IsEmpty(m_prd_list) Then
        On Error GoTo ErrorTrap
            lb = LBound(m_prd_list, 1)
            ub = UBound(m_prd_list, 1)
        On Error GoTo 0
        If ub < lb Then GoTo ErrorTrap
        For idx = lb To ub
            Set m_prd_list(idx) = Nothing
        Next idx
        Erase m_prd_list
    End If
ErrorTrap:
End Sub

Private Sub ClearTrancheList()
    Dim idx As Long, lb As Long, ub As Long
    
    If Not IsEmpty(m_trn_list) Then
        On Error GoTo ErrorTrap
            lb = LBound(m_trn_list, 1)
            ub = UBound(m_trn_list, 1)
        On Error GoTo 0
        If ub < lb Then GoTo ErrorTrap
        For idx = lb To ub
            Set m_trn_list(idx) = Nothing
        Next idx
        Erase m_trn_list
    End If
ErrorTrap:
End Sub

Private Sub ClearDispatchProductList()
    Dim idx As Long, lb As Long, ub As Long
    
    If Not IsEmpty(m_dsp_list) Then
        On Error GoTo ErrorTrap
            lb = LBound(m_dsp_list, 1)
            ub = UBound(m_dsp_list, 1)
        On Error GoTo 0
        If ub < lb Then GoTo ErrorTrap
        For idx = lb To ub
            Set m_dsp_list(idx) = Nothing
        Next idx
        Erase m_dsp_list
    End If
ErrorTrap:
End Sub

Private Sub ClearFirmProfileList()
    Dim idx As Long, lb As Long, ub As Long
    
    If Not IsEmpty(m_frm_list) Then
        On Error GoTo ErrorTrap
            lb = LBound(m_frm_list, 1)
            ub = UBound(m_frm_list, 1)
        On Error GoTo 0
        If ub < lb Then GoTo ErrorTrap
        For idx = lb To ub
            Set m_frm_list(idx) = Nothing
        Next idx
        Erase m_frm_list
    End If
ErrorTrap:
End Sub

