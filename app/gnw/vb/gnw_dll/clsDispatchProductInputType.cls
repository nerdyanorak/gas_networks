VERSION 1.0 CLASS
BEGIN
  MultiUse = -1  'True
  Persistable = 0  'NotPersistable
  DataBindingBehavior = 0  'vbNone
  DataSourceBehavior  = 0  'vbNone
  MTSTransactionMode  = 0  'NotAnMTSObject
END
Attribute VB_Name = "CDispatchProductInputType"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = True
Attribute VB_PredeclaredId = False
Attribute VB_Exposed = True
'#  $Id: clsDispatchProductInputType.cls 2000 2009-09-15 08:17:32Z re04179 $
'#  $URL: http://subversion.rwe.com/svn/s_and_v_projects/GasNetworks/trunk/app/gnw/vb/gnw_dll/clsDispatchProductInputType.cls $
'#  $Revision: 2000 $
'#  $Date: 2009-09-15 10:17:32 +0200 (Tue, 15 Sep 2009) $
'#  $Author: re04179 $
Option Explicit
Option Base 0
Private Const ModuleVersion As String = "0pt1"

' Helper structure for dispatch prouducts
Public Type DispatchProductInputType
    name As String                                  ' unique product identifier (mandatory)
    sellbuy As gnw.SellBuyEnum                      ' sell or buy flag (mandatory)
    price As Variant                                ' array of size nStps of double values of
                                                    ' bid or ask prices (mandatory) depending on
                                                    ' sellbuy flag value
    midPrice As Variant                             ' array of size nStps of double values of
                                                    ' mid prices (mandatory)
    currentPosition As Variant                      ' optional array of size nStps of double values of
                                                    ' current position in [MW], empty otherwise
    discountFactor As Variant                       ' optional array of size nStps of double values
                                                    ' representing the discount factors applicable
                                                    ' to cashflows arising from gas volumes
                                                    ' transacted during the DISPATCH_PERIODs,
                                                    ' empty otherwise
End Type

