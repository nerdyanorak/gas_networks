VERSION 1.0 CLASS
BEGIN
  MultiUse = -1  'True
  Persistable = 0  'NotPersistable
  DataBindingBehavior = 0  'vbNone
  DataSourceBehavior  = 0  'vbNone
  MTSTransactionMode  = 0  'NotAnMTSObject
END
Attribute VB_Name = "CTranchInputType"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = True
Attribute VB_PredeclaredId = False
Attribute VB_Exposed = True
'#  $Id: clsTranchInputType.cls 2000 2009-09-15 08:17:32Z re04179 $
'#  $URL: http://subversion.rwe.com/svn/s_and_v_projects/GasNetworks/trunk/app/gnw/vb/gnw_dll/clsTranchInputType.cls $
'#  $Revision: 2000 $
'#  $Date: 2009-09-15 10:17:32 +0200 (Tue, 15 Sep 2009) $
'#  $Author: re04179 $
Option Explicit
Option Base 0
Private Const ModuleVersion As String = "0pt2"

' Helper structure for tranches
Public Type TrancheInputType
    name As String                                  ' unique tranche identifer (mandatory)
    sellbuy As gnw.SellBuyEnum                      ' sell or buy flag (mandatory)
    bidAskAdj As Double                             ' bid or ask price adjustment to mid price (mandatory)
                                                    ' if m_sellbuy = 1 (sell) then adjustment will be
                                                    ' subtracted from corresponding standard product's
                                                    ' mid price, added otherwise.
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

