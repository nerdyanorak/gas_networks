VERSION 1.0 CLASS
BEGIN
  MultiUse = -1  'True
  Persistable = 0  'NotPersistable
  DataBindingBehavior = 0  'vbNone
  DataSourceBehavior  = 0  'vbNone
  MTSTransactionMode  = 0  'NotAnMTSObject
END
Attribute VB_Name = "CEntityTypeEnum"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = True
Attribute VB_PredeclaredId = False
Attribute VB_Exposed = True
'#  $Id: clsEntityTypeEnum.cls 2000 2009-09-15 08:17:32Z re04179 $
'#  $URL: http://subversion.rwe.com/svn/s_and_v_projects/GasNetworks/trunk/app/gnw/vb/gnw_dll/clsEntityTypeEnum.cls $
'#  $Revision: 2000 $
'#  $Date: 2009-09-15 10:17:32 +0200 (Tue, 15 Sep 2009) $
'#  $Author: re04179 $
Option Explicit
Option Base 0
Private Const ModuleVersion As String = "0pt1"

Public Enum eEntityType
    eEntityTypeStrorage = 1
    eEntityTypeSupplier = 2
    eEntityTypeProduct = 3
    eEntityTypeTranche = 4
    eEntityTypeDispatchProduct = 5
    eEntityTypeFirmProfile = 6
End Enum


Public Function GetEntityInstanceName(entity_type As Integer) As Variant
    Select Case entity_type
        Case gnw.eEntityType.eEntityTypeStrorage
            GetEntityInstanceName = "storage"
        Case gnw.eEntityType.eEntityTypeSupplier
            GetEntityInstanceName = "supplier"
        Case gnw.eEntityType.eEntityTypeProduct
            GetEntityInstanceName = "product"
        Case gnw.eEntityType.eEntityTypeTranche
            GetEntityInstanceName = "tranche"
        Case gnw.eEntityType.eEntityTypeDispatchProduct
            GetEntityInstanceName = "dispatch_product"
        Case gnw.eEntityType.eEntityTypeFirmProfile
            GetEntityInstanceName = "firm_profile"
        Case Else
            GetEntityInstanceName = Empty
        End Select
End Function
