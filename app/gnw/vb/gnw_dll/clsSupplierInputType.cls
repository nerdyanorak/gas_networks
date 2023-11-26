VERSION 1.0 CLASS
BEGIN
  MultiUse = -1  'True
  Persistable = 0  'NotPersistable
  DataBindingBehavior = 0  'vbNone
  DataSourceBehavior  = 0  'vbNone
  MTSTransactionMode  = 0  'NotAnMTSObject
END
Attribute VB_Name = "CSupplierInputType"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = True
Attribute VB_PredeclaredId = False
Attribute VB_Exposed = True
'#  $Id: clsSupplierInputType.cls 2404 2009-10-11 19:33:29Z re04179 $
'#  $URL: http://subversion.rwe.com/svn/s_and_v_projects/GasNetworks/trunk/app/gnw/vb/gnw_dll/clsSupplierInputType.cls $
'#  $Revision: 2404 $
'#  $Date: 2009-10-11 21:33:29 +0200 (Sun, 11 Oct 2009) $
'#  $Author: re04179 $
Option Explicit
Option Base 0
Private Const ModuleVersion As String = "0pt3"

' Helper structure for suppliers
Public Type SupplierInputType
    name As String                              ' unique product identifier (mandatory)
    sellbuy As gnw.SellBuyEnum                  ' sell or buy flag (mandatory)
    acq As Double                               ' nominal Annual Contract Quantity in [MWh]
    constraintCoeff As Variant                  ' array of constraint definitions. Each element
                                                ' holds start idx (int), final idx (int), bound value (float),
                                                ' bound type (int) and constraint type (str)
    contractPrice As Variant                    ' array of double holding a contract price per dispatch period.
    hasShortfallPenalty As Boolean              ' whether or not shortfall penalty feature applies
    hasMakeUp As Boolean                        ' whether or not make-up gas feature applies
    hasMakeUpExpiry As Boolean                  ' whether or not expiry feature of make-up gas feature applies
    makeUpNumExpiryPeriods As Integer           ' number of expiry periods in case make-up gas expiry
                                                ' feature applies
    makeUpCreatePriceRate As Double             ' Rate to be applied to average contract price
                                                ' for gas paid for but not taken
    makeUpUseupPriceRate As Double              ' Rate to be applied to average contract price for
                                                ' gas taken as make-up.
    hasCarryForward As Boolean                  ' whether or not carry forward gas feature applies
    hasCarryForwardExpiry As Boolean            ' whether or not expiry feature of carry forward gas feature applies
    carryForwardNumExpiryPeriods As Integer     ' number of expiry periods in case carry forward gas
                                                ' expiry feature applies
    hasIAS39 As Boolean                         ' whether or not IAS 39 accounting related features apply
    
    shortfallPenaltyCurveType As String         ' currently only 'backstep'
    shortfallPenaltyCurve As Variant            ' 2-dim array with M rows and 2 columns with the first value
                                                ' representing the shortfall percentage w.r.t. to the daily
                                                ' minimum quantity value
                                                ' and the second value representing the price penality as
                                                ' a percentage respect to the contract rice.
    makeUpInitialBalance As Variant             ' if hasMakeUp and not hasMakeUpExpiry then
                                                ' holds a float value representing the initial balance of
                                                ' make-up gas at the start of the optimisation period.
                                                ' if hasMakeUp and hasMakeUpExpiry then
                                                ' holds an array of size makeUpNumExpiryPeriods (= N)
                                                ' representing the initial balance of make-up gas at the
                                                ' start of the optimisation period expiring at the end
                                                ' of make-up accounting periods ([gas] years) 1, 2, ..., N,
                                                ' respectively.
    carryForwardInitialBalance As Variant       ' if hasCarryForward and not hasCarryForwardExpiry then
                                                ' holds a float value representing the initial balance of
                                                ' carry forward gas at the start of the optimisation period.
                                                ' if hasCarryForward and hasCarryForwardExpiry then
                                                ' holds an array of size carryForwardNumExpiryPeriods (= N)
                                                ' representing the initial balance of carry forward gas at the
                                                ' start of the optimisation period expiring at the end
                                                ' of carry forward accounting periods ([gas] years) 1, 2, ..., N,
                                                ' respectively.
    accPeriodAvgContractPrice As Variant        ' potentially empty variant or 1-d array of numeric values
                                                ' of average contract prices corresponding to the first N
                                                ' accounting periods of the problem. N may be less than the
                                                ' actual number of accounting periods.
    discountFactor As Variant                   ' optional array of double holding a discount factor per dispatch period.
                                                ' Consecutive dispatch periods may have the same discount factor
                                                ' signifying that cashflows arising from such dispatches are
                                                ' settled on the same date.
End Type

