VERSION 1.0 CLASS
BEGIN
  MultiUse = -1  'True
  Persistable = 0  'NotPersistable
  DataBindingBehavior = 0  'vbNone
  DataSourceBehavior  = 0  'vbNone
  MTSTransactionMode  = 0  'NotAnMTSObject
END
Attribute VB_Name = "Bounds"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = True
Attribute VB_PredeclaredId = False
Attribute VB_Exposed = True
'#  $Id: clsBounds.cls 680 2009-04-29 16:35:09Z re04179 $
'#  $URL: http://subversion.rwe.com/svn/s_and_v_projects/GasNetworks/trunk/app/gnw/vb/gnw_dll/clsBounds.cls $
'#  $Revision: 680 $
'#  $Date: 2009-04-29 18:35:09 +0200 (Wed, 29 Apr 2009) $
'#  $Author: re04179 $
Option Explicit
Option Base 0
Private Const ModuleVersion As String = "0pt1"

Private m_lBnd As Variant
Private m_uBnd As Variant

Private Sub Class_Initialize()
    Me.Clear
End Sub

Public Property Let LBnd(val As Variant)
    m_lBnd = val
End Property
Public Property Get LBnd() As Variant
    LBnd = m_lBnd
End Property


Public Property Let UBnd(val As Variant)
    m_uBnd = val
End Property
Public Property Get UBnd() As Variant
    UBnd = m_uBnd
End Property


Public Sub SetBounds(loBnd As Variant, upBnd As Variant)
    Me.LBnd = loBnd
    Me.UBnd = upBnd
End Sub
Public Property Get AsPair() As Variant()
    AsPair = Array(m_lBnd, m_uBnd)
End Property

Public Sub Clear()
    Me.ClearLBnd
    Me.ClearUBnd
End Sub

Public Sub ClearLBnd()
    m_lBnd = Empty
End Sub
Public Sub ClearUBnd()
    m_uBnd = Empty
End Sub

