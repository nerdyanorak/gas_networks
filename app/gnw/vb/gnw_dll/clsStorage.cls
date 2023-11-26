VERSION 1.0 CLASS
BEGIN
  MultiUse = -1  'True
  Persistable = 0  'NotPersistable
  DataBindingBehavior = 0  'vbNone
  DataSourceBehavior  = 0  'vbNone
  MTSTransactionMode  = 0  'NotAnMTSObject
END
Attribute VB_Name = "Storage"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = True
Attribute VB_PredeclaredId = False
Attribute VB_Exposed = True
'#  $Id: clsStorage.cls 2000 2009-09-15 08:17:32Z re04179 $
'#  $URL: http://subversion.rwe.com/svn/s_and_v_projects/GasNetworks/trunk/app/gnw/vb/gnw_dll/clsStorage.cls $
'#  $Revision: 2000 $
'#  $Date: 2009-09-15 10:17:32 +0200 (Tue, 15 Sep 2009) $
'#  $Author: re04179 $
Option Explicit
Option Base 0
Private Const ModuleVersion As String = "0pt2"

Private m_name As String                            ' unique storage identifier (mandatory)
Private m_sellbuy As gnw.SellBuyEnum                ' sell or buy flag (mandatory)
Private m_injCap As Double                          ' nominal injection capacity in capacity units [MW] (mandatory)
Private m_relCap As Double                          ' nominal release capacity in capacity units [MW] (mandatory)
Private m_wgv As Double                             ' nominal working gas volume in engery units [MWh] (mandatory)
Private m_startLevPct As Double                     ' storage start level given as a percentage of m_WGV (mandatory)
Private m_finalLevPct As Variant                    ' storage final level given as a percentage of m_WGV (optional)
                                                    ' if missing no final level constraints are imposed.
Private m_strictFinalLev As Boolean                 ' whether given storage final level percentage has to be reached
                                                    ' exactly or servers as lower bound only (mandatory, although only
                                                    ' used if m_FinalLevPct is not Empty
Private m_injCost As Variant                        ' array of size m_gnrlNStps of injection cost given as [EUR/MWh]
                                                    ' during corresponding dispatch period (optional, default = 0)
Private m_relCost As Variant                        ' array of size m_gnrlNStps of release cost given as [EUR/MWh]
                                                    ' during corresponding dispatch period (optional, default = 0)
Private m_hasLevDepInjCapRateCurve As Boolean       ' flags the use of level dependent injection capacity rate curves
                                                    ' (mandatory)
Private m_levDepInjCapRateCurveType As String       ' only 'backstep' so far
Private m_levDepInjCapRateCurve As Variant          ' 2-dim array with M rows and 2 columns with the first value
                                                    ' representing the storage level as percentage of m_WGV
                                                    ' and the second value representing the injection capacity
                                                    ' rate up to that given level, i.e., back-step interpolation
                                                    ' (optional, default = 1 for all levels)
Private m_hasLevDepRelCapRateCurve As Boolean       ' flags the use of level dependent release capacity rate curves
                                                    ' (mandatory)
Private m_levDepRelCapRateCurveType As String       ' only 'backstep' so far
Private m_levDepRelCapRateCurve As Variant          ' 2-dim array with N rows and 2 columns with the first value
                                                    ' representing the storage level as percentage of m_WGV
                                                    ' and the second value representing the release capacity
                                                    ' rate up to that give level, i.e., back-step interpolation
                                                    ' (optional, default = 1 for all levels)
Private m_constraintCoeff As Variant                ' 2-dim constraint coefficient array with M rows and 5 columns
                                                    ' of types [int, int, float, int, int] representing:
                                                    '   - start period index into dispatch period array (zero based),
                                                    '   - final period index into dispatch period array (zero based),
                                                    '   - boundary value,
                                                    '   - boundary type (one of gnw.eBndType, e.g., eBndTypeLB,
                                                    '       eBndTypeUB, eBndTypeEQ),
                                                    '   - constraint type mask (bitwise and combination of elements
                                                    '       out of gnw.eCnstrType).
                                                    ' At the moment the following inputs are expected in form of a
                                                    ' constraint coefficient array:
                                                    '   - {min,max}LevPct       (nSteps + 1)-array
                                                    '   - {min,max}InjCapPct    nSteps-array
                                                    '   - {min,max}RelCapPct    nSteps-array
                                                    '   - {min,max}InjVolPct    (m x 3)-array
                                                    '   - {min,max}RelVolPct    (m x 3)-array
Private m_discountFactor As Variant                 ' optional array of size nStps of double values
                                                    ' representing the discount factors applicable
                                                    ' to cashflows arising from gas volumes
                                                    ' transacted during the DISPATCH_PERIODs,
                                                    ' empty otherwise
                                            
                                            
                                            

Public Property Get name() As String
    name = m_name
End Property


Public Sub Initialise( _
        strgName As String, _
        sellbuy As gnw.SellBuyEnum, _
        Optional injCap As Double = 1#, _
        Optional relCap As Double = 1#, _
        Optional wgv As Double = 1#, _
        Optional startLevPct As Double = 0#, _
        Optional finalLevPct As Variant, _
        Optional strictFinalLev As Boolean = False, _
        Optional injCost As Variant, Optional relCost As Variant, _
        Optional minLevPct As Variant, Optional maxLevPct As Variant, _
        Optional minInjCapPct As Variant, Optional maxInjCapPct As Variant, _
        Optional minRelCapPct As Variant, Optional maxRelCapPct As Variant, _
        Optional minInjVolPct As Variant, Optional maxInjVolPct As Variant, _
        Optional minRelVolPct As Variant, Optional maxRelVolPct As Variant, _
        Optional hasLevDepInjCapRateCurve As Boolean = False, _
        Optional levDepInjCapRateCurveType As String = "backstep", _
        Optional levDepInjCapRateCurve As Variant, _
        Optional hasLevDepRelCapRateCurve As Boolean = False, _
        Optional levDepRelCapRateCurveType As String = "backstep", _
        Optional levDepRelCapRateCurve As Variant, _
        Optional discountFactor As Variant)

    m_name = strgName
    m_sellbuy = sellbuy
    
    m_injCap = injCap
    m_relCap = relCap
    m_wgv = wgv
    m_startLevPct = startLevPct
    m_finalLevPct = finalLevPct
    m_strictFinalLev = strictFinalLev

    m_injCost = injCost
    m_relCost = relCost

    m_constraintCoeff = Empty
    If Not (IsMissing(minLevPct) Or IsEmpty(minLevPct)) Then
        m_constraintCoeff = SetConstraintCoeff1D(m_constraintCoeff, minLevPct, gnw.eBndType.eBndTypeLB, gnw.eCnstrType.eCnstrTypeLevPct)
    End If
    If Not (IsMissing(maxLevPct) Or IsEmpty(maxLevPct)) Then
        m_constraintCoeff = SetConstraintCoeff1D(m_constraintCoeff, maxLevPct, gnw.eBndType.eBndTypeUB, gnw.eCnstrType.eCnstrTypeLevPct)
    End If

    If Not (IsMissing(minInjCapPct) Or IsEmpty(minInjCapPct)) Then
        m_constraintCoeff = SetConstraintCoeff1D(m_constraintCoeff, minInjCapPct, gnw.eBndType.eBndTypeLB, gnw.eCnstrType.eCnstrTypeInjCapPct)
    End If
    If Not (IsMissing(maxInjCapPct) Or IsEmpty(maxInjCapPct)) Then
        m_constraintCoeff = SetConstraintCoeff1D(m_constraintCoeff, maxInjCapPct, gnw.eBndType.eBndTypeUB, gnw.eCnstrType.eCnstrTypeInjCapPct)
    End If
    
    If Not (IsMissing(minRelCapPct) Or IsEmpty(minRelCapPct)) Then
        m_constraintCoeff = SetConstraintCoeff1D(m_constraintCoeff, minRelCapPct, gnw.eBndType.eBndTypeLB, gnw.eCnstrType.eCnstrTypeRelCapPct)
    End If
    If Not (IsMissing(maxRelCapPct) Or IsEmpty(maxRelCapPct)) Then
        m_constraintCoeff = SetConstraintCoeff1D(m_constraintCoeff, maxRelCapPct, gnw.eBndType.eBndTypeUB, gnw.eCnstrType.eCnstrTypeRelCapPct)
    End If
    
    If Not (IsMissing(minInjVolPct) Or IsEmpty(minInjVolPct)) Then
        m_constraintCoeff = SetConstraintCoeff2D(m_constraintCoeff, minInjVolPct, gnw.eBndType.eBndTypeLB, gnw.eCnstrType.eCnstrTypeInjVolPct)
    End If
    If Not (IsMissing(maxInjVolPct) Or IsEmpty(maxInjVolPct)) Then
        m_constraintCoeff = SetConstraintCoeff2D(m_constraintCoeff, maxInjVolPct, gnw.eBndType.eBndTypeUB, gnw.eCnstrType.eCnstrTypeInjVolPct)
    End If
    
    If Not (IsMissing(minRelVolPct) Or IsEmpty(minRelVolPct)) Then
        m_constraintCoeff = SetConstraintCoeff2D(m_constraintCoeff, minRelVolPct, gnw.eBndType.eBndTypeLB, gnw.eCnstrType.eCnstrTypeRelVolPct)
    End If
    If Not (IsMissing(maxRelVolPct) Or IsEmpty(maxRelVolPct)) Then
        m_constraintCoeff = SetConstraintCoeff2D(m_constraintCoeff, maxRelVolPct, gnw.eBndType.eBndTypeUB, gnw.eCnstrType.eCnstrTypeRelVolPct)
    End If
    
    m_hasLevDepInjCapRateCurve = hasLevDepInjCapRateCurve
    m_levDepInjCapRateCurveType = levDepInjCapRateCurveType
    m_levDepInjCapRateCurve = levDepInjCapRateCurve
    
    m_hasLevDepRelCapRateCurve = hasLevDepRelCapRateCurve
    m_levDepRelCapRateCurveType = levDepRelCapRateCurveType
    m_levDepRelCapRateCurve = levDepRelCapRateCurve
    
    m_discountFactor = discountFactor
    
End Sub

Public Sub InitialiseFromInputType(data As gnw.StorageInputType)
    Call Me.Initialise( _
        data.name, _
        data.sellbuy, _
        data.injCap, data.relCap, data.wgv, _
        data.startLevPct, data.finalLevPct, data.strictFinalLev, _
        data.injCost, data.relCost, _
        data.minLevPct, data.maxLevPct, _
        data.minInjCapPct, data.maxInjCapPct, _
        data.minRelCapPct, data.maxRelCapPct, _
        data.minInjVolPct, data.maxInjVolPct, _
        data.minRelVolPct, data.maxRelVolPct, _
        data.hasLevDepInjCapRate, data.levDepInjCapRateCurveType, data.levDepInjCapRate, _
        data.hasLevDepRelCapRate, data.levDepRelCapRateCurveType, data.levDepRelCapRate, _
        data.discountFactor)
End Sub

Public Function AsNamedItem() As gnw.NamedItem
    Dim niHdlr As New gnw.NamedItemHdlr
    
    Dim niName As gnw.NamedItem
    Dim niSB As gnw.NamedItem
    Dim niINJ_CAP As gnw.NamedItem
    Dim niREL_CAP As gnw.NamedItem
    Dim niWGV As gnw.NamedItem
    Dim niSTART_LEV_PCT As gnw.NamedItem
    Dim niEND_LEV_PCT As gnw.NamedItem
    Dim niSTRICT_END_LEV As gnw.NamedItem
    
    Dim niINJ_COST As gnw.NamedItem
    Dim niREL_COST As gnw.NamedItem
    
    Dim niCONSTRAINT_COEFF As gnw.NamedItem
    
    Dim niHAS_LEV_DEP_INJ_CAP_CURVE As gnw.NamedItem
    Dim niHAS_LEV_DEP_REL_CAP_CURVE As gnw.NamedItem
    Dim niLEV_DEP_INJ_CAP_CURVE As gnw.NamedItem
    Dim niLEV_DEP_REL_CAP_CURVE As gnw.NamedItem
    Dim niLEV_DEP_INJ_CAP_CURVE_TYPE As gnw.NamedItem
    Dim niLEV_DEP_REL_CAP_CURVE_TYPE As gnw.NamedItem
    Dim niDISCOUNT_FACTOR As gnw.NamedItem
    
    Set niName = niHdlr.Create("NAME", "str", m_name)
    Set niSB = niHdlr.Create("SB", "int", m_sellbuy)
    Set niINJ_CAP = niHdlr.Create("INJ_CAP", "float", m_injCap)
    Set niREL_CAP = niHdlr.Create("REL_CAP", "float", m_relCap)
    Set niWGV = niHdlr.Create("WGV", "float", m_wgv)
    Set niSTART_LEV_PCT = niHdlr.Create("START_LEV_PCT", "float", m_startLevPct)
    Set niEND_LEV_PCT = niHdlr.Create("END_LEV_PCT", "float", m_finalLevPct)
    Set niSTRICT_END_LEV = niHdlr.Create("STRICT_END_LEV", "bool", m_strictFinalLev)
    
    Set niINJ_COST = niHdlr.Create("INJ_COST", "array", Array("float"), m_injCost)
    Set niREL_COST = niHdlr.Create("REL_COST", "array", Array("float"), m_relCost)
    
    Set niCONSTRAINT_COEFF = niHdlr.Create("CONSTRAINT_COEFF", "array", Array("int", "int", "float", "int", "int"), m_constraintCoeff)
    
    Set niHAS_LEV_DEP_INJ_CAP_CURVE = niHdlr.Create("HAS_LEV_DEP_INJ_CAP_CURVE", "bool", m_hasLevDepInjCapRateCurve)
    Set niLEV_DEP_INJ_CAP_CURVE_TYPE = niHdlr.Create("LEV_DEP_INJ_CAP_CURVE_TYPE", "str", m_levDepInjCapRateCurveType)
    Set niLEV_DEP_INJ_CAP_CURVE = niHdlr.Create("LEV_DEP_INJ_CAP_CURVE", "array", Array("float"), m_levDepInjCapRateCurve)
    
    Set niHAS_LEV_DEP_REL_CAP_CURVE = niHdlr.Create("HAS_LEV_DEP_REL_CAP_CURVE", "bool", m_hasLevDepRelCapRateCurve)
    Set niLEV_DEP_REL_CAP_CURVE_TYPE = niHdlr.Create("LEV_DEP_REL_CAP_CURVE_TYPE", "str", m_levDepRelCapRateCurveType)
    Set niLEV_DEP_REL_CAP_CURVE = niHdlr.Create("LEV_DEP_REL_CAP_CURVE", "array", Array("float"), m_levDepRelCapRateCurve)
    
    Set niDISCOUNT_FACTOR = niHdlr.Create("DISCOUNT_FACTOR", "array", Array("float"), m_discountFactor)
    
    Set AsNamedItem = niHdlr.Create(m_name, "array", Array("NI"), _
        Array( _
            niName, _
            niSB, _
            niINJ_CAP, niREL_CAP, niWGV, _
            niSTART_LEV_PCT, niEND_LEV_PCT, niSTRICT_END_LEV, _
            niHAS_LEV_DEP_INJ_CAP_CURVE, niLEV_DEP_INJ_CAP_CURVE_TYPE, niLEV_DEP_INJ_CAP_CURVE, _
            niHAS_LEV_DEP_REL_CAP_CURVE, niLEV_DEP_REL_CAP_CURVE_TYPE, niLEV_DEP_REL_CAP_CURVE, _
            niINJ_COST, niREL_COST, _
            niCONSTRAINT_COEFF, _
            niDISCOUNT_FACTOR))
    
    Set niHdlr = Nothing
End Function

Private Function SetConstraintCoeff1D(cnstrCoeff As Variant, varArray1D As Variant, bndType As Integer, cnstrTypeMask As Long) As Variant
    Debug.Assert IsEmpty(cnstrCoeff) Or getVarArrayNumDims(cnstrCoeff) = 2
    Debug.Assert IsEmpty(cnstrCoeff) Or getVarArraySize(cnstrCoeff, 2) = 5
    
    Debug.Assert getVarArrayNumDims(varArray1D) = 1
    
    Dim cnstrCoeffBase1 As Integer
    Dim cnstrCoeffBase2 As Integer
    Dim cnstrCoeffSize1 As Long
    
    If Not IsEmpty(cnstrCoeff) Then
        cnstrCoeffBase1 = getVarArrayBase(cnstrCoeff, 1)
        cnstrCoeffBase2 = getVarArrayBase(cnstrCoeff, 2)
        cnstrCoeffSize1 = getVarArraySize(cnstrCoeff, 1)
    Else
        cnstrCoeffBase1 = 0
        cnstrCoeffBase2 = 0
        cnstrCoeffSize1 = 0
    End If
    
    Dim varArrayBase1 As Integer
    Dim varArraySize1 As Long
    
    varArrayBase1 = getVarArrayBase(varArray1D, 1)
    varArraySize1 = getVarArraySize(varArray1D, 1)

    Dim tmpCnstrCoeff As Variant
    ReDim tmpCnstrCoeff(cnstrCoeffBase1 To cnstrCoeffBase1 + cnstrCoeffSize1 + varArraySize1 - 1, cnstrCoeffBase2 To cnstrCoeffBase2 + 5 - 1)
    
    Dim idx As Long, jdx As Long
    For idx = cnstrCoeffBase1 To cnstrCoeffBase1 + cnstrCoeffSize1 - 1
        For jdx = cnstrCoeffBase2 To cnstrCoeffBase2 + 5 - 1
            tmpCnstrCoeff(idx, jdx) = cnstrCoeff(idx, jdx)
        Next jdx
    Next idx
    
    Dim offset As Long
    For idx = varArrayBase1 To varArraySize1 - 1
        offset = cnstrCoeffBase1 + cnstrCoeffSize1 + (idx - varArrayBase1)
        tmpCnstrCoeff(offset, cnstrCoeffBase2 + 0) = (idx - varArrayBase1)
        tmpCnstrCoeff(offset, cnstrCoeffBase2 + 1) = (idx - varArrayBase1)
        tmpCnstrCoeff(offset, cnstrCoeffBase2 + 2) = varArray1D(idx)
        tmpCnstrCoeff(offset, cnstrCoeffBase2 + 3) = bndType
        tmpCnstrCoeff(offset, cnstrCoeffBase2 + 4) = cnstrTypeMask
    Next idx
    
    SetConstraintCoeff1D = tmpCnstrCoeff
End Function

Private Function SetConstraintCoeff2D(cnstrCoeff As Variant, varArray2D As Variant, bndType As Integer, cnstrTypeMask As Long) As Variant
    Debug.Assert IsEmpty(cnstrCoeff) Or getVarArrayNumDims(cnstrCoeff) = 2
    Debug.Assert IsEmpty(cnstrCoeff) Or getVarArraySize(cnstrCoeff, 2) = 5
    
    Debug.Assert getVarArrayNumDims(varArray2D) = 2
    Debug.Assert getVarArraySize(varArray2D, 2) = 3
    
    
    Dim cnstrCoeffBase1 As Integer
    Dim cnstrCoeffBase2 As Integer
    Dim cnstrCoeffSize1 As Long
    
    If Not IsEmpty(cnstrCoeff) Then
        cnstrCoeffBase1 = getVarArrayBase(cnstrCoeff, 1)
        cnstrCoeffBase2 = getVarArrayBase(cnstrCoeff, 2)
        cnstrCoeffSize1 = getVarArraySize(cnstrCoeff, 1)
    Else
        cnstrCoeffBase1 = 0
        cnstrCoeffBase2 = 0
        cnstrCoeffSize1 = 0
    End If
    
    Dim varArrayBase1 As Integer
    Dim varArrayBase2 As Integer
    Dim varArraySize1 As Long
    
    varArrayBase1 = getVarArrayBase(varArray2D, 1)
    varArrayBase2 = getVarArrayBase(varArray2D, 2)
    varArraySize1 = getVarArraySize(varArray2D, 1)

    Dim tmpCnstrCoeff As Variant
    ReDim tmpCnstrCoeff(cnstrCoeffBase1 To cnstrCoeffBase1 + cnstrCoeffSize1 + varArraySize1 - 1, cnstrCoeffBase2 To cnstrCoeffBase2 + 5 - 1)
    
    Dim idx As Long, jdx As Long
    For idx = cnstrCoeffBase1 To cnstrCoeffBase1 + cnstrCoeffSize1 - 1
        For jdx = cnstrCoeffBase2 To cnstrCoeffBase2 + 5 - 1
            tmpCnstrCoeff(idx, jdx) = cnstrCoeff(idx, jdx)
        Next jdx
    Next idx
    
    Dim offset As Long
    For idx = varArrayBase1 To varArraySize1 - 1
        offset = cnstrCoeffBase1 + cnstrCoeffSize1 + (idx - varArrayBase1)
        tmpCnstrCoeff(offset, cnstrCoeffBase2 + 0) = varArray2D(idx, varArrayBase2 + 0)
        tmpCnstrCoeff(offset, cnstrCoeffBase2 + 1) = varArray2D(idx, varArrayBase2 + 1)
        tmpCnstrCoeff(offset, cnstrCoeffBase2 + 2) = varArray2D(idx, varArrayBase2 + 2)
        tmpCnstrCoeff(offset, cnstrCoeffBase2 + 3) = bndType
        tmpCnstrCoeff(offset, cnstrCoeffBase2 + 4) = cnstrTypeMask
    Next idx

    SetConstraintCoeff2D = tmpCnstrCoeff
End Function

