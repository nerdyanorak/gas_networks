VERSION 1.0 CLASS
BEGIN
  MultiUse = -1  'True
  Persistable = 0  'NotPersistable
  DataBindingBehavior = 0  'vbNone
  DataSourceBehavior  = 0  'vbNone
  MTSTransactionMode  = 0  'NotAnMTSObject
END
Attribute VB_Name = "Tranche"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = True
Attribute VB_PredeclaredId = False
Attribute VB_Exposed = True
'#  $Id: clsTranche.cls 2000 2009-09-15 08:17:32Z re04179 $
'#  $URL: http://subversion.rwe.com/svn/s_and_v_projects/GasNetworks/trunk/app/gnw/vb/gnw_dll/clsTranche.cls $
'#  $Revision: 2000 $
'#  $Date: 2009-09-15 10:17:32 +0200 (Tue, 15 Sep 2009) $
'#  $Author: re04179 $
Option Explicit
Option Base 0
Private Const ModuleVersion As String = "0pt2"

Private m_name As String                            ' unique tranche identifier (mandatory)
Private m_sellbuy As gnw.SellBuyEnum                ' sell or buy flag (mandatory)
Private m_bidAskAdj As Double                       ' bid or ask price adjustment to mid price (mandatory)
                                                    ' if m_sellbuy = 1 (sell) then adjustment will be
                                                    ' subtracted from corresponding standard product's
                                                    ' mid price, added otherwise.
Private m_deliveryPeriodStart As Long               ' value represents index into m_dpArray.
Private m_deliveryPeriodEnd As Long                 ' value represents index into m_dpArray.
Private m_capacityLimitMin As Variant               ' value represents the minimal trade size in [MW] for
                                                    ' given trade tranche
Private m_capacityLimitMax As Variant               ' value represents the maximal trade size in [MW] for
                                                    ' given trade tranche
Private m_discountFactor As Variant                 ' optional array of size nStps of double values
                                                    ' representing the discount factors applicable
                                                    ' to cashflows arising from gas volumes
                                                    ' transacted during the DISPATCH_PERIODs,
                                                    ' empty otherwise

Public Property Get name() As String
    name = m_name
End Property

Public Sub Initialise( _
        name As String, _
        sellbuy As gnw.SellBuyEnum, _
        bidAskAdj As Double, _
        deliveryPeriodStart As Long, _
        deliveryPeriodEnd As Long, _
        Optional capacityLimitMin As Variant, _
        Optional capacityLimitMax As Variant, _
        Optional discountFactor As Variant)
        
    m_name = name
    m_sellbuy = sellbuy
    m_bidAskAdj = bidAskAdj
    m_deliveryPeriodStart = deliveryPeriodStart
    m_deliveryPeriodEnd = deliveryPeriodEnd
    m_capacityLimitMin = capacityLimitMin
    m_capacityLimitMax = capacityLimitMax
    m_discountFactor = discountFactor
    
End Sub

Public Sub InitialiseFromInputType(data As gnw.TrancheInputType)
    
    Call Me.Initialise( _
        data.name, _
        data.sellbuy, _
        data.bidAskAdj, _
        data.deliveryStart, _
        data.deliveryEnd, _
        data.capacityLimitMin, _
        data.capacityLimitMax, _
        data.discountFactor)
        
End Sub

Public Function AsNamedItem() As gnw.NamedItem
    Dim niHdlr As New gnw.NamedItemHdlr
    
    Dim niName As gnw.NamedItem
    Dim niSB As gnw.NamedItem
    Dim niBID_ASK_ADJ As gnw.NamedItem
    Dim niSTART_IDX As gnw.NamedItem
    Dim niEND_IDX As gnw.NamedItem
    Dim niTRADE_SIZE_MIN As gnw.NamedItem
    Dim niTRADE_SIZE_MAX As gnw.NamedItem
    Dim niDISCOUNT_FACTOR As gnw.NamedItem
    
    Set niName = niHdlr.Create("NAME", "str", m_name)
    Set niSB = niHdlr.Create("SB", "int", m_sellbuy)
    Set niBID_ASK_ADJ = niHdlr.Create("BID_ASK_ADJ", "float", m_bidAskAdj)
    Set niSTART_IDX = niHdlr.Create("START_IDX", "int", m_deliveryPeriodStart)
    Set niEND_IDX = niHdlr.Create("END_IDX", "int", m_deliveryPeriodEnd)
    Set niTRADE_SIZE_MIN = niHdlr.Create("TRADE_SIZE_MIN", "float", m_capacityLimitMin)
    Set niTRADE_SIZE_MAX = niHdlr.Create("TRADE_SIZE_MAX", "float", m_capacityLimitMax)
    Set niDISCOUNT_FACTOR = niHdlr.Create("DISCOUNT_FACTOR", "array", Array("float"), m_discountFactor)
    
    Set AsNamedItem = niHdlr.Create(m_name, "array", Array("NI"), _
        Array( _
            niName, _
            niSB, _
            niBID_ASK_ADJ, _
            niSTART_IDX, _
            niEND_IDX, _
            niTRADE_SIZE_MIN, _
            niTRADE_SIZE_MAX, _
            niDISCOUNT_FACTOR))

    Set niHdlr = Nothing
End Function

