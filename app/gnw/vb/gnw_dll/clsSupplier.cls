VERSION 1.0 CLASS
BEGIN
  MultiUse = -1  'True
  Persistable = 0  'NotPersistable
  DataBindingBehavior = 0  'vbNone
  DataSourceBehavior  = 0  'vbNone
  MTSTransactionMode  = 0  'NotAnMTSObject
END
Attribute VB_Name = "Supplier"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = True
Attribute VB_PredeclaredId = False
Attribute VB_Exposed = True
'#  $Id: clsSupplier.cls 2404 2009-10-11 19:33:29Z re04179 $
'#  $URL: http://subversion.rwe.com/svn/s_and_v_projects/GasNetworks/trunk/app/gnw/vb/gnw_dll/clsSupplier.cls $
'#  $Revision: 2404 $
'#  $Date: 2009-10-11 21:33:29 +0200 (Sun, 11 Oct 2009) $
'#  $Author: re04179 $
Option Explicit
Option Base 0
Private Const ModuleVersion As String = "0pt3"


Private m_name As String                            ' unique product identifier (mandatory)
Private m_sellbuy As gnw.SellBuyEnum                ' sell or buy flag (mandatory)
Private m_acq As Double                             ' nominal Annual Contract Quantity in [MWh]
Private m_constraintCoeff As Variant                ' array of constraint definitions. Each element
                                                    ' holds start idx (int), final idx (int), bound value (float),
                                                    ' bound type (int) and constraint type (str)
Private m_contractPrice As Variant                  ' array of double holding a contract price per dispatch period.
Private m_hasShortfallPenalty As Boolean

Private m_hasMakeUp As Boolean
Private m_hasMakeUpExpiry As Boolean
Private m_makeUpNumExpiryPeriods As Integer
Private m_makeUpCreatePriceRate As Double
Private m_makeUpUseupPriceRate As Double

Private m_hasCarryForward As Boolean
Private m_hasCarryForwardExpiry As Boolean
Private m_carryForwardNumExpiryPeriods As Integer

Private m_hasIAS39 As Boolean

Private m_shortfallPenaltyCurveType As String
Private m_shortfallPenaltyCurve As Variant

Private m_makeUpInitialBalance As Variant

Private m_carryForwardInitialBalance As Variant

Private m_accPeriodAvgContractPrice As Variant      ' potentially empty variant or 1-d array of numeric values
                                                    ' of average contract prices corresponding to the first N
                                                    ' accounting periods of the problem. N may be less than the
                                                    ' actual number of accounting periods.

Private m_discountFactor As Variant                 ' optional array of double holding a discount factor per dispatch period.
                                                    ' Consecutive dispatch periods may have the same discount factor
                                                    ' signifying that cashflows arising from such dispatches are
                                                    ' settled on the same date.

Public Property Get name() As String
    name = m_name
End Property

Public Sub Initialise( _
        name As String, _
        sellbuy As gnw.SellBuyEnum, _
        constraintCoeff As Variant, _
        contractPrice As Variant, _
        Optional acq As Double = 1#, _
        Optional hasShortfallPenalty As Boolean = False, _
        Optional hasMakeUp As Boolean = False, _
        Optional hasMakeUpExpiry As Boolean = False, _
        Optional makeUpNumExpiryPeriods As Integer = 0, _
        Optional makeUpCreatePriceRate As Double = 1#, _
        Optional makeUpUseupPriceRate As Double = 0#, _
        Optional hasCarryForward As Boolean = False, _
        Optional hasCarryForwardExpiry As Boolean = False, _
        Optional carryForwardNumExpiryPeriods As Integer = 0, _
        Optional hasIAS39 As Boolean = False, _
        Optional shortfallPenaltyCurveType As String = "backstep", _
        Optional shortfallPenaltyCurve As Variant, _
        Optional makeUpInitialBalance As Variant, _
        Optional carryForwardInitialBalance As Variant, _
        Optional accPeriodAvgContractPrice As Variant, _
        Optional discountFactor As Variant)
        
    m_name = name
    m_sellbuy = sellbuy
    m_constraintCoeff = constraintCoeff
    m_contractPrice = contractPrice
    m_acq = acq
    
    m_hasShortfallPenalty = hasShortfallPenalty
    
    m_hasMakeUp = hasMakeUp
    m_hasMakeUpExpiry = hasMakeUpExpiry
    m_makeUpNumExpiryPeriods = makeUpNumExpiryPeriods
    m_makeUpCreatePriceRate = makeUpCreatePriceRate
    m_makeUpUseupPriceRate = makeUpUseupPriceRate
    
    m_hasCarryForward = hasCarryForward
    m_hasCarryForwardExpiry = hasCarryForwardExpiry
    m_carryForwardNumExpiryPeriods = carryForwardNumExpiryPeriods
    
    m_hasIAS39 = hasIAS39
    
    m_shortfallPenaltyCurveType = shortfallPenaltyCurveType
    m_shortfallPenaltyCurve = shortfallPenaltyCurve
    
    m_makeUpInitialBalance = makeUpInitialBalance
    
    m_carryForwardInitialBalance = carryForwardInitialBalance
    
    m_accPeriodAvgContractPrice = accPeriodAvgContractPrice
    
    m_discountFactor = discountFactor

End Sub

Public Sub InitialiseFromInputType(data As gnw.SupplierInputType)
    
    Call Me.Initialise( _
        data.name, _
        data.sellbuy, _
        data.constraintCoeff, _
        data.contractPrice, _
        data.acq, _
        data.hasShortfallPenalty, _
        data.hasMakeUp, _
        data.hasMakeUpExpiry, _
        data.makeUpNumExpiryPeriods, _
        data.makeUpCreatePriceRate, _
        data.makeUpUseupPriceRate, _
        data.hasCarryForward, _
        data.hasCarryForwardExpiry, _
        data.carryForwardNumExpiryPeriods, _
        data.hasIAS39, _
        data.shortfallPenaltyCurveType, _
        data.shortfallPenaltyCurve, _
        data.makeUpInitialBalance, _
        data.carryForwardInitialBalance, _
        data.accPeriodAvgContractPrice, _
        data.discountFactor)
End Sub

Public Function AsNamedItem() As gnw.NamedItem
    Dim niHdlr As New gnw.NamedItemHdlr
    
    Dim niName As gnw.NamedItem
    Dim niSB As gnw.NamedItem
    Dim niCONSTRAINT_COEFF As gnw.NamedItem
    Dim niCONTRACT_PRICE_CURVE As gnw.NamedItem
    Dim niACQ As gnw.NamedItem
    Dim niHAS_SHORTFALL_PENALTY As gnw.NamedItem
    Dim niHAS_MAKEUP As gnw.NamedItem
    Dim niHAS_MAKEUP_EXPIRY As gnw.NamedItem
    Dim niMAKEUP_NUM_EXPIRY_PERIODS As gnw.NamedItem
    Dim niMAKEUP_CREATE_PRICE_RATE As gnw.NamedItem
    Dim niMAKEUP_USEUP_PRICE_RATE As gnw.NamedItem
    Dim niHAS_CARRYFORWARD As gnw.NamedItem
    Dim niHAS_CARRYFORWARD_EXPIRY As gnw.NamedItem
    Dim niCARRYFORWARD_NUM_EXPIRY_PERIODS As gnw.NamedItem
    Dim niHAS_IAS39 As gnw.NamedItem
    Dim niSHORTFALL_PENALTY_CURVE_TYPE As gnw.NamedItem
    Dim niSHORTFALL_PENALTY_CURVE As gnw.NamedItem
    Dim niMAKEUP_INITIAL_BALANCE As gnw.NamedItem
    Dim niCARRYFORWARD_INITIAL_BALANCE As gnw.NamedItem
    Dim niACC_PERIOD_AVG_CONTRACT_PRICE As gnw.NamedItem
    Dim niDISCOUNT_FACTOR As gnw.NamedItem
    
    Set niName = niHdlr.Create("NAME", "str", m_name)
    Set niSB = niHdlr.Create("SB", "int", m_sellbuy)
    Set niCONSTRAINT_COEFF = niHdlr.Create("CONSTRAINT_COEFF", "array", Array("int", "int", "float", "int", "int"), m_constraintCoeff)
    Set niCONTRACT_PRICE_CURVE = niHdlr.Create("CONTRACT_PRICE_CURVE", "array", Array("float"), m_contractPrice)
    Set niACQ = niHdlr.Create("ACQ", "float", m_acq)
    Set niHAS_SHORTFALL_PENALTY = niHdlr.Create("HAS_SHORTFALL_PENALTY", "bool", m_hasShortfallPenalty)
    Set niHAS_MAKEUP = niHdlr.Create("HAS_MAKEUP", "bool", m_hasMakeUp)
    Set niHAS_MAKEUP_EXPIRY = niHdlr.Create("HAS_MAKEUP_EXPIRY", "bool", m_hasMakeUpExpiry)
    Set niMAKEUP_NUM_EXPIRY_PERIODS = niHdlr.Create("MAKEUP_NUM_EXPIRY_PERIODS", "int", m_makeUpNumExpiryPeriods)
    Set niMAKEUP_CREATE_PRICE_RATE = niHdlr.Create("MAEKUP_CREATE_PRICE_RATE", "float", m_makeUpCreatePriceRate)
    Set niMAKEUP_USEUP_PRICE_RATE = niHdlr.Create("MAKEUP_USEUP_PRICE_RATE", "float", m_makeUpUseupPriceRate)
    Set niHAS_CARRYFORWARD = niHdlr.Create("HAS_CARRYFORWARD", "bool", m_hasCarryForward)
    Set niHAS_CARRYFORWARD_EXPIRY = niHdlr.Create("HAS_CARRYFORWARD_EXPIRY", "bool", m_hasCarryForwardExpiry)
    Set niCARRYFORWARD_NUM_EXPIRY_PERIODS = niHdlr.Create("CARRYFORWARD_NUM_EXPIRY_PERIODS", "int", m_carryForwardNumExpiryPeriods)
    Set niHAS_IAS39 = niHdlr.Create("HAS_IAS39", "bool", m_hasIAS39)
    Set niSHORTFALL_PENALTY_CURVE_TYPE = niHdlr.Create("SHORTFALL_PENALTY_CURVE_TYPE", "str", m_shortfallPenaltyCurveType)
    If m_hasShortfallPenalty Then
        Set niSHORTFALL_PENALTY_CURVE = niHdlr.Create("SHORTFALL_PENALTY_CURVE", "array", Array("float", "float"), m_shortfallPenaltyCurve)
    Else
        Dim dummy(0 To 1, 0 To 1) As Variant
        dummy(0, 0) = 0#
        dummy(0, 1) = 0#
        dummy(1, 0) = 1#
        dummy(1, 1) = 0#
        Set niSHORTFALL_PENALTY_CURVE = niHdlr.Create("SHORTFALL_PENALTY_CURVE", "array", Array("float"), dummy)
    End If
    If m_hasMakeUp Then
        If m_hasMakeUpExpiry Then
            Set niMAKEUP_INITIAL_BALANCE = niHdlr.Create("MAKEUP_INITIAL_BALANCE", "array", Array("float"), m_makeUpInitialBalance)
        Else
            Set niMAKEUP_INITIAL_BALANCE = niHdlr.Create("MAKEUP_INITIAL_BALANCE", "float", m_makeUpInitialBalance)
        End If
    Else
        Set niMAKEUP_INITIAL_BALANCE = niHdlr.Create("MAKEUP_INITIAL_BALANCE", "float", 0#)
    End If
    If m_hasCarryForward Then
        If m_hasCarryForwardExpiry Then
            Set niCARRYFORWARD_INITIAL_BALANCE = niHdlr.Create("CARRYFORWARD_INITIAL_BALANCE", "array", Array("float"), m_carryForwardInitialBalance)
        Else
            Set niCARRYFORWARD_INITIAL_BALANCE = niHdlr.Create("CARRYFORWARD_INITIAL_BALANCE", "float", m_carryForwardInitialBalance)
        End If
    Else
        Set niCARRYFORWARD_INITIAL_BALANCE = niHdlr.Create("CARRYFORWARD_INITIAL_BALANCE", "float", 0#)
    End If
    Set niACC_PERIOD_AVG_CONTRACT_PRICE = niHdlr.Create("ACC_PERIOD_AVG_CONTRACT_PRICE", "array", Array("float"), m_accPeriodAvgContractPrice)
    Set niDISCOUNT_FACTOR = niHdlr.Create("DISCOUNT_FACTOR", "array", Array("float"), m_discountFactor)

    Set AsNamedItem = niHdlr.Create(m_name, "array", Array("NI"), _
        Array( _
            niName, _
            niSB, _
            niACQ, _
            niHAS_SHORTFALL_PENALTY, niSHORTFALL_PENALTY_CURVE_TYPE, niSHORTFALL_PENALTY_CURVE, _
            niHAS_MAKEUP, niHAS_MAKEUP_EXPIRY, niMAKEUP_NUM_EXPIRY_PERIODS, _
                niMAKEUP_CREATE_PRICE_RATE, niMAKEUP_USEUP_PRICE_RATE, _
                niMAKEUP_INITIAL_BALANCE, _
            niHAS_CARRYFORWARD, niHAS_CARRYFORWARD_EXPIRY, niCARRYFORWARD_NUM_EXPIRY_PERIODS, _
                niCARRYFORWARD_INITIAL_BALANCE, _
            niACC_PERIOD_AVG_CONTRACT_PRICE, _
            niHAS_IAS39, _
            niCONSTRAINT_COEFF, _
            niCONTRACT_PRICE_CURVE, _
            niDISCOUNT_FACTOR))

    Set niHdlr = Nothing
End Function

