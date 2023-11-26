VERSION 1.0 CLASS
BEGIN
  MultiUse = -1  'True
  Persistable = 0  'NotPersistable
  DataBindingBehavior = 0  'vbNone
  DataSourceBehavior  = 0  'vbNone
  MTSTransactionMode  = 0  'NotAnMTSObject
END
Attribute VB_Name = "CProductInputType"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = True
Attribute VB_PredeclaredId = False
Attribute VB_Exposed = True
'#  $Id: clsProductInputType.cls 2000 2009-09-15 08:17:32Z re04179 $
'#  $URL: http://subversion.rwe.com/svn/s_and_v_projects/GasNetworks/trunk/app/gnw/vb/gnw_dll/clsProductInputType.cls $
'#  $Revision: 2000 $
'#  $Date: 2009-09-15 10:17:32 +0200 (Tue, 15 Sep 2009) $
'#  $Author: re04179 $
Option Explicit
Option Base 0
Private Const ModuleVersion As String = "0pt3"

' Helper structure for products
Public Type ProductInputType
    name As String                                  ' unique product identifier (mandatory)
    sellbuy As gnw.SellBuyEnum                      ' sell or buy flag (mandatory)
    midPrice As Double                              ' mid price (mandatory)
    clipSize As Variant                             ' clip size, if Empty or equal to 0 no clip size
                                                    ' constraints apply, otherwise clip size in [MW]
    currentPosition As Double                       ' current position in [MW] (long pos > 0, short pos < 0)
    deliveryStart As Long                           ' index into dispatchPeriod vector.
    deliveryEnd As Long                             ' index into dispatchPeriod vector.
    capacityLimitMin As Variant                     ' minimal trade size in [MW] for given standard product.
                                                    ' May be set to 'Empty'
    capacityLimitMax As Variant                     ' maximal trade size in [MW] for given standard product.
                                                    ' May be set to 'Empty'
    discountFactor As Variant                       ' optional array of size nStps of double values
                                                    ' representing the discount factors applicable
                                                    ' to cashflows arising from gas volumes
                                                    ' transacted during the DISPATCH_PERIODs,
                                                    ' empty otherwise
End Type

