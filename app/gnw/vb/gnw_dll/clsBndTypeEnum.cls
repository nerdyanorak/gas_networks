VERSION 1.0 CLASS
BEGIN
  MultiUse = -1  'True
  Persistable = 0  'NotPersistable
  DataBindingBehavior = 0  'vbNone
  DataSourceBehavior  = 0  'vbNone
  MTSTransactionMode  = 0  'NotAnMTSObject
END
Attribute VB_Name = "CBndTypeEnum"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = True
Attribute VB_PredeclaredId = False
Attribute VB_Exposed = True
'#  $Id: clsBndTypeEnum.cls 1322 2009-07-23 15:14:20Z re04179 $
'#  $URL: http://subversion.rwe.com/svn/s_and_v_projects/GasNetworks/trunk/app/gnw/vb/gnw_dll/clsBndTypeEnum.cls $
'#  $Revision: 1322 $
'#  $Date: 2009-07-23 17:14:20 +0200 (Thu, 23 Jul 2009) $
'#  $Author: re04179 $
Option Explicit
Option Base 0
Private Const ModuleVersion As String = "0pt1"

Public Enum eBndType
    eBndTypeLB = 0
    eBndTypeMIN = 0
    eBndTypeUB = 1
    eBndTypeMAX = 1
    eBndTypeEQ = 2
    eBndTypeFIRM = 2
End Enum

