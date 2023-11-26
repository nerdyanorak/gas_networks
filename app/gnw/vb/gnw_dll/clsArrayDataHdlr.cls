VERSION 1.0 CLASS
BEGIN
  MultiUse = -1  'True
  Persistable = 0  'NotPersistable
  DataBindingBehavior = 0  'vbNone
  DataSourceBehavior  = 0  'vbNone
  MTSTransactionMode  = 0  'NotAnMTSObject
END
Attribute VB_Name = "ArrayDataHdlr"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = True
Attribute VB_PredeclaredId = False
Attribute VB_Exposed = True
'#  $Id: clsArrayDataHdlr.cls 1860 2009-09-07 12:09:18Z re04179 $
'#  $URL: http://subversion.rwe.com/svn/s_and_v_projects/GasNetworks/trunk/app/gnw/vb/gnw_dll/clsArrayDataHdlr.cls $
'#  $Revision: 1860 $
'#  $Date: 2009-09-07 14:09:18 +0200 (Mon, 07 Sep 2009) $
'#  $Author: re04179 $
Option Explicit
Option Base 0
Private Const ModuleVersion As String = "0pt1"

Private m_niHdlr As gnw.NamedItemHdlr

Private Sub Class_Initialize()
    Set m_niHdlr = New gnw.NamedItemHdlr
End Sub

Private Sub Class_Terminate()
    Set m_niHdlr = Nothing
End Sub

Function GetTuple(keys() As Variant, niArrayData() As Variant) As gnw.NamedItem

    Dim key As String
    Dim rem_keys() As Variant
    
    Dim niData As gnw.NamedItem
    If Not IsEmpty(keys) Then
        key = keys(LBound(keys))
        rem_keys = Empty
        If UBound(keys) - LBound(keys) > 0 Then
            ReDim rem_keys(0 To UBound(keys) - LBound(keys) - 1)
            For idx = LBound(keys) + 1 To UBound(keys)
                rem_keys(idx - LBound(keys) - 1) = keys(idx)
            Next idx
        End If
    
        For idx = LBound(niArrayData) To UBound(niArrayData)
            If key = niArrayData(idx, 1) Then
                
            End If
        Next idx
    
    End If
    
        
    
End Function
