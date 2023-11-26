VERSION 1.0 CLASS
BEGIN
  MultiUse = -1  'True
  Persistable = 0  'NotPersistable
  DataBindingBehavior = 0  'vbNone
  DataSourceBehavior  = 0  'vbNone
  MTSTransactionMode  = 0  'NotAnMTSObject
END
Attribute VB_Name = "FirmProfile"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = True
Attribute VB_PredeclaredId = False
Attribute VB_Exposed = True
'#  $Id: clsFirmProfile.cls 2405 2009-10-11 19:35:05Z re04179 $
'#  $URL: http://subversion.rwe.com/svn/s_and_v_projects/GasNetworks/trunk/app/gnw/vb/gnw_dll/clsFirmProfile.cls $
'#  $Revision: 2405 $
'#  $Date: 2009-10-11 21:35:05 +0200 (Sun, 11 Oct 2009) $
'#  $Author: re04179 $
Option Explicit
Option Base 0
Private Const ModuleVersion As String = "0pt1"


Private m_name As String                            ' unique product identifier (mandatory)
Private m_sellbuy As gnw.SellBuyEnum                ' sell or buy flag (mandatory)
Private m_currentPosition As Variant                ' array of size nStps of double values of
                                                    ' current position in [MW] (long pos > 0, short pos < 0)
Private m_discountFactor As Variant                 ' optional array of size nStps of double values
                                                    ' representing the discount factors applicable
                                                    ' to cashflows arising from gas volumes
                                                    ' transacted during the DISPATCH_PERIODs

Public Property Get name() As String
    name = m_name
End Property

Public Sub Initialise( _
        name As String, _
        sellbuy As gnw.SellBuyEnum, _
        Optional currentPosition As Variant, _
        Optional discountFactor As Variant)
            
    m_name = name
    m_sellbuy = sellbuy
    m_currentPosition = currentPosition
    m_discountFactor = discountFactor
            
End Sub
        

Public Sub InitialiseFromInputType(data As gnw.FirmProfileInputType)

    Call Me.Initialise( _
        data.name, _
        data.sellbuy, _
        data.currentPosition, _
        data.discountFactor)
End Sub

Public Function AsNamedItem() As gnw.NamedItem
    Dim niHdlr As New gnw.NamedItemHdlr
    
    Dim niName As gnw.NamedItem
    Dim niSB As gnw.NamedItem
    Dim niCURRENT_POS As gnw.NamedItem
    Dim niDISCOUNT_FACTOR As gnw.NamedItem
    
    Set niName = niHdlr.Create("NAME", "str", m_name)
    Set niSB = niHdlr.Create("SB", "int", m_sellbuy)
    Set niCURRENT_POS = niHdlr.Create("CURRENT_POS_CURVE", "array", Array("float"), m_currentPosition)
    Set niDISCOUNT_FACTOR = niHdlr.Create("DISCOUNT_FACTOR", "array", Array("float"), m_discountFactor)
    
    Set AsNamedItem = _
        niHdlr.Create(m_name, "array", Array("NI"), _
            Array( _
                niName, _
                niSB, _
                niCURRENT_POS, _
                niDISCOUNT_FACTOR))
                                            
    Set niHdlr = Nothing
End Function

