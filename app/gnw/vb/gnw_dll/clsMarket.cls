VERSION 1.0 CLASS
BEGIN
  MultiUse = -1  'True
  Persistable = 0  'NotPersistable
  DataBindingBehavior = 0  'vbNone
  DataSourceBehavior  = 0  'vbNone
  MTSTransactionMode  = 0  'NotAnMTSObject
END
Attribute VB_Name = "Market"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = True
Attribute VB_PredeclaredId = False
Attribute VB_Exposed = True
'#  $Id: clsMarket.cls 1860 2009-09-07 12:09:18Z re04179 $
'#  $URL: http://subversion.rwe.com/svn/s_and_v_projects/GasNetworks/trunk/app/gnw/vb/gnw_dll/clsMarket.cls $
'#  $Revision: 1860 $
'#  $Date: 2009-09-07 14:09:18 +0200 (Mon, 07 Sep 2009) $
'#  $Author: re04179 $
Option Explicit
Option Base 0
Private Const ModuleVersion As String = "0pt1"

Private m_dfArray() As Double               ' array of size m_gnrlNStps holding discount factors at
                                            ' which cashflows arising from dispatch/trade actions
                                            ' relating to equivalent dispatch period are discounted
Private m_dpArray() As Double               ' array of size m_gnrlNStps of dispatch periods holding
                                            ' the length of each dispatch period in hours [h] (mandatory)
Private m_fcArray() As Double               ' 2-d array of m_gnrlNStps x 3 elements of double holding
                                            ' the bid/mid/ask price of underlying asset for corresponding
                                            ' dispatch period in currency units per energy unit [EUR/MWh]
                                            ' (EUR and MWh, respectively, serve here as concrete
                                            ' place holders)


Public Sub Initialise( _
        dfArray() As Double, _
        dpArray() As Double, _
        fcArray() As Double)
        
    m_dfArray = dfArray
    m_dpArray = dpArray
    m_fcArray = fcArray
End Sub
    
Public Function AsNamedItem() As gnw.NamedItem
    Dim niHdlr As New gnw.NamedItemHdlr
    
    Dim niDISCOUNT_FACTOR As gnw.NamedItem
    Dim niDISPATCH_PERIOD As gnw.NamedItem
    Dim niFWD_CURVE As gnw.NamedItem
    
    Set niDISCOUNT_FACTOR = niHdlr.Create("DISCOUNT_FACTOR", "array", Array("float"), m_dfArray)
    Set niDISPATCH_PERIOD = niHdlr.Create("DISPATCH_PERIOD", "array", Array("float"), m_dpArray)
    Set niFWD_CURVE = niHdlr.Create("FWD_CURVE", "array", Array("float"), m_fcArray)
    
    Set AsNamedItem = _
        niHdlr.Create("MRKT_DICT", "array", Array("NI"), _
            Array( _
                niDISCOUNT_FACTOR, _
                niDISPATCH_PERIOD, _
                niFWD_CURVE))

    Set niHdlr = Nothing
End Function

