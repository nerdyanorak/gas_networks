VERSION 1.0 CLASS
BEGIN
  MultiUse = -1  'True
  Persistable = 0  'NotPersistable
  DataBindingBehavior = 0  'vbNone
  DataSourceBehavior  = 0  'vbNone
  MTSTransactionMode  = 0  'NotAnMTSObject
END
Attribute VB_Name = "Product"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = True
Attribute VB_PredeclaredId = False
Attribute VB_Exposed = True
'#  $Id: clsProduct.cls 2000 2009-09-15 08:17:32Z re04179 $
'#  $URL: http://subversion.rwe.com/svn/s_and_v_projects/GasNetworks/trunk/app/gnw/vb/gnw_dll/clsProduct.cls $
'#  $Revision: 2000 $
'#  $Date: 2009-09-15 10:17:32 +0200 (Tue, 15 Sep 2009) $
'#  $Author: re04179 $
Option Explicit
Option Base 0
Private Const ModuleVersion As String = "0pt1"


Private m_name As String                            ' unique product identifier (mandatory)
Private m_sellbuy As gnw.SellBuyEnum                ' sell or buy flag (mandatory)
Private m_midPrice As Double                        ' mid price (mandatory)
Private m_clipSize As Variant                       ' clip size, if Empty or equal to 0 no clip size
                                                    ' constraints apply, otherwise clip size in [MW]
Private m_currentPosition As Double                 ' current position in [MW] (long pos > 0, short pos < 0)

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
        midPrice As Double, _
        deliveryPeriodStart As Long, _
        deliveryPeriodEnd As Long, _
        Optional clipSize As Variant, _
        Optional currentPosition As Double, _
        Optional capacityLimitMin As Variant, _
        Optional capacityLimitMax As Variant, _
        Optional discountFactor As Variant)
        
    m_name = name
    m_sellbuy = sellbuy
    m_midPrice = midPrice
    m_clipSize = clipSize
    m_currentPosition = currentPosition
    m_deliveryPeriodStart = deliveryPeriodStart
    m_deliveryPeriodEnd = deliveryPeriodEnd
    m_capacityLimitMin = capacityLimitMin
    m_capacityLimitMax = capacityLimitMax
    m_discountFactor = discountFactor
    
End Sub

Public Sub InitialiseFromInputType(data As gnw.ProductInputType)
    
    Call Me.Initialise( _
        data.name, _
        data.sellbuy, _
        data.midPrice, _
        data.deliveryStart, _
        data.deliveryEnd, _
        data.clipSize, _
        data.currentPosition, _
        data.capacityLimitMin, _
        data.capacityLimitMax, _
        data.discountFactor)

End Sub

Public Function AsNamedItem() As gnw.NamedItem
    Dim niHdlr As New gnw.NamedItemHdlr
    
    Dim niName As gnw.NamedItem
    Dim niSB As gnw.NamedItem
    Dim niMID_PRICE As gnw.NamedItem
    Dim niCLIP_SIZE As gnw.NamedItem
    Dim niCURRENT_POS As gnw.NamedItem
    Dim niSTART_IDX As gnw.NamedItem
    Dim niEND_IDX As gnw.NamedItem
    Dim niTRADE_SIZE_MIN As gnw.NamedItem
    Dim niTRADE_SIZE_MAX As gnw.NamedItem
    Dim niDISCOUNT_FACTOR As gnw.NamedItem
    
    Set niName = niHdlr.Create("NAME", "str", m_name)
    Set niSB = niHdlr.Create("SB", "int", m_sellbuy)
    Set niMID_PRICE = niHdlr.Create("MID_PRICE", "float", m_midPrice)
    Set niCLIP_SIZE = niHdlr.Create("CLIP_SIZE", "float", m_clipSize)
    Set niCURRENT_POS = niHdlr.Create("CURRENT_POS", "float", m_currentPosition)
    Set niSTART_IDX = niHdlr.Create("START_IDX", "int", m_deliveryPeriodStart)
    Set niEND_IDX = niHdlr.Create("END_IDX", "int", m_deliveryPeriodEnd)
    Set niTRADE_SIZE_MIN = niHdlr.Create("TRADE_SIZE_MIN", "float", m_capacityLimitMin)
    Set niTRADE_SIZE_MAX = niHdlr.Create("TRADE_SIZE_MAX", "float", m_capacityLimitMax)
    Set niDISCOUNT_FACTOR = niHdlr.Create("DISCOUNT_FACTOR", "array", Array("float"), m_discountFactor)
    
    Set AsNamedItem = niHdlr.Create(m_name, "array", Array("NI"), _
        Array( _
            niName, _
            niSB, _
            niMID_PRICE, _
            niCLIP_SIZE, _
            niCURRENT_POS, _
            niSTART_IDX, _
            niEND_IDX, _
            niTRADE_SIZE_MIN, _
            niTRADE_SIZE_MAX, _
            niDISCOUNT_FACTOR))

    Set niHdlr = Nothing
End Function

