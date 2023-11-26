VERSION 1.0 CLASS
BEGIN
  MultiUse = -1  'True
  Persistable = 0  'NotPersistable
  DataBindingBehavior = 0  'vbNone
  DataSourceBehavior  = 0  'vbNone
  MTSTransactionMode  = 0  'NotAnMTSObject
END
Attribute VB_Name = "CCnstrTypeEnum"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = True
Attribute VB_PredeclaredId = False
Attribute VB_Exposed = True
'#  $Id: clsCnstrTypeEnum.cls 1860 2009-09-07 12:09:18Z re04179 $
'#  $URL: http://subversion.rwe.com/svn/s_and_v_projects/GasNetworks/trunk/app/gnw/vb/gnw_dll/clsCnstrTypeEnum.cls $
'#  $Revision: 1860 $
'#  $Date: 2009-09-07 14:09:18 +0200 (Mon, 07 Sep 2009) $
'#  $Author: re04179 $
Option Explicit
Option Base 0
Private Const ModuleVersion As String = "0pt1"

Public Enum eCnstrType
    eCnstrTypePosPct = 1            ' 2 ^ 0
    eCnstrTypeAccPeriod = 2         ' 2 ^ 1
    eCnstrTypeMupBndPct = 4         ' 2 ^ 2
    eCnstrTypeCfwBndPct = 8         ' 2 ^ 3
    eCnstrType_NA_4 = 16            ' 2 ^ 4
    eCnstrType_NA_5 = 32            ' 2 ^ 5
    eCnstrTypeLevPct = 64           ' 2 ^ 6
    eCnstrTypeInjCapPct = 128       ' 2 ^ 7
    eCnstrTypeRelCapPct = 256       ' 2 ^ 8
    eCnstrTypeInjVolPct = 512       ' 2 ^ 9
    eCnstrTypeRelVolPct = 1024      ' 2 ^ 10
    eCnstrType_NA_11 = 2048         ' 2 ^ 11
    eCnstrType_NA_12 = 4096         ' 2 ^ 12
    eCnstrType_NA_13 = 8192         ' 2 ^ 13
    eCnstrType_NA_14 = 16384        ' 2 ^ 14
    eCnstrType_NA_15 = 32768        ' 2 ^ 15
End Enum

