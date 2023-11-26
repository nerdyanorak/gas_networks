VERSION 1.0 CLASS
BEGIN
  MultiUse = -1  'True
  Persistable = 0  'NotPersistable
  DataBindingBehavior = 0  'vbNone
  DataSourceBehavior  = 0  'vbNone
  MTSTransactionMode  = 0  'NotAnMTSObject
END
Attribute VB_Name = "CStorageInputType"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = True
Attribute VB_PredeclaredId = False
Attribute VB_Exposed = True
'#  $Id: clsStorageInputType.cls 2000 2009-09-15 08:17:32Z re04179 $
'#  $URL: http://subversion.rwe.com/svn/s_and_v_projects/GasNetworks/trunk/app/gnw/vb/gnw_dll/clsStorageInputType.cls $
'#  $Revision: 2000 $
'#  $Date: 2009-09-15 10:17:32 +0200 (Tue, 15 Sep 2009) $
'#  $Author: re04179 $
Option Explicit
Option Base 0
Private Const ModuleVersion As String = "0pt2"

' Helper structure for Storages
Public Type StorageInputType
    name As String
    sellbuy As gnw.SellBuyEnum                      ' sell or buy flag (mandatory)
    injCap As Double                                ' nominal injection capacity in capacity units [MW] (mandatory)
    relCap As Double                                ' nominal release capacity in capacity units [MW] (mandatory)
    wgv As Double                                   ' nominal working gas volume in engery units [MWh] (mandatory)
    startLevPct As Double                           ' storage start level given as a percentage of wgv (mandatory)
    finalLevPct As Variant                          ' storage final level given as a percentage of wgv (optional)
                                                    ' if missing no final level constraints are imposed.
    strictFinalLev As Boolean                       ' whether given storage final level percentage has to be reached
                                                    ' exactly or servers as lower bound only (mandatory, although only
                                                    ' used if finalLevPct is not Empty
    injCost As Variant                              ' array of size nStps of injection cost given as [EUR/MWh]
                                                    ' during corresponding dispatch period (optional, default = 0)
    relCost As Variant                              ' array of size nStps of release cost given as [EUR/MWh]
                                                    ' during corresponding dispatch period (optional, default = 0)
    minLevPct As Variant                            ' array of size nPnts of storage minimum levels given as a
                                                    ' percentage of wgv (optional, default = 0)
                                                    ' Represent the minimum level for the corresponding dispatch period
                                                    ' before any dispatch decision has been taken
    maxLevPct As Variant                            ' array of size nPnts of storage maximum levels given as a
                                                    ' percentage of wgv(optional, default = 1)
                                                    ' Represent the maximum level for the corresponding dispatch period
                                                    ' before any dispatch decision has been taken
    minInjCapPct As Variant                         ' array of size nStps of minimal storage injection capacities
                                                    ' given as a percentage of injCap for corresponding
                                                    ' dispatch period (optional, default = 0).
                                                    ' Set to 0 for dispatch periods where the storage
                                                    ' is not available for dispatch (i.e., before the storage start
                                                    ' date or after the storage end date)
    maxInjCapPct As Variant                         ' array of size nStps of maximal storage injection capacities
                                                    ' given as a percentage of injCap for corresponding
                                                    ' dispatch period (optional, default = 1).
                                                    ' Set to 0 for dispatch periods where the storage
                                                    ' is not available for dispatch (i.e., before the storage start
                                                    ' date, after the storage end date or any other period inbetween)
    minRelCapPct As Variant                         ' array of size nStps of minimal storage release capacities
                                                    ' given as a percentage of relCap for corresponding
                                                    ' dispatch period (optional, default = 0).
                                                    ' Set to 0 for dispatch period where the storage
                                                    ' is not available for dispatch (i.e., before the storage start
                                                    ' date or after the storage end date)
    maxRelCapPct As Variant                         ' array of size nStps of maximal storage release capacities
                                                    ' given as a percentage of relCap for corresponding
                                                    ' dispatch period (optional, default = 1).
                                                    ' Set to 0 for dispatch period where the storage
                                                    ' is not available for dispatch (i.e., before the storage start
                                                    ' date, after the storage end date or any other period inbetween)
    minInjVolPct As Variant                         ' 2-dim array with M rows and 3 columns with the first two
                                                    ' values representing indices into the dispatch period array
                                                    ' dispatchPeriod defining first and last dispatch period,
                                                    ' respectively, over which the minimum injection volume
                                                    ' restriction applies given in the third element as a percentage
                                                    ' of wgv (optional)
    maxInjVolPct As Variant                         ' 2-dim array with N rows and 3 columns with the first two
                                                    ' values representing indices into the dispatch period array
                                                    ' dispatchPeriod defining first and last dispatch period,
                                                    ' respectively, over which the maximum injection volume
                                                    ' restriction applies given in the third element as a percentage
                                                    ' of wgv (optional)
    minRelVolPct As Variant                         ' 2-dim array with M rows and 3 columns with the first two
                                                    ' values representing indices into the dispatch period array
                                                    ' dispatchPeriod defining first and last dispatch period,
                                                    ' respectively, over which the minimum release volume
                                                    ' restriction applies given in the third element as a percentage
                                                    ' of wgv (optional)
    maxRelVolPct As Variant                         ' 2-dim array with N rows and 3 columns with the first two
                                                    ' values representing indices into the dispatch period array
                                                    ' dispatchPeriod defining first and last dispatch period,
                                                    ' respectively, over which the maximum release volume
                                                    ' restriction applies given in the third element as a percentage
                                                    ' of wgv (optional)
    hasLevDepInjCapRate As Boolean                  ' flags the use of level dependent injection capacity rate curves
                                                    ' (mandatory)
    levDepInjCapRateCurveType As String             ' only 'backstep' currently available
    levDepInjCapRate As Variant                     ' 2-dim array with M rows and 2 columns with the first value
                                                    ' representing the storage level as percentage of wgv
                                                    ' and the second value representing the injection capacity
                                                    ' rate up to that given level, i.e., back-step interpolation
                                                    ' (optional, default = 1 for all levels)
    hasLevDepRelCapRate As Boolean                  ' flags the use of level dependent release capacity rate curves
                                                    ' (mandatory)
    levDepRelCapRateCurveType As String             ' only 'backstep' currently available
    levDepRelCapRate As Variant                     ' 2-dim array with N rows and 2 columns with the first value
                                                    ' representing the storage level as percentage of wgv
                                                    ' and the second value representing the release capacity
                                                    ' rate up to that give level, i.e., back-step interpolation
                                                    ' (optional, default = 1 for all levels)
    discountFactor As Variant                       ' optional array of size nStps of double values
                                                    ' representing the discount factors applicable
                                                    ' to cashflows arising from gas volumes
                                                    ' transacted during the DISPATCH_PERIODs,
                                                    ' empty otherwise
End Type

