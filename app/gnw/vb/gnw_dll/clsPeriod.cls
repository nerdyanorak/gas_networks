VERSION 1.0 CLASS
BEGIN
  MultiUse = -1  'True
  Persistable = 0  'NotPersistable
  DataBindingBehavior = 0  'vbNone
  DataSourceBehavior  = 0  'vbNone
  MTSTransactionMode  = 0  'NotAnMTSObject
END
Attribute VB_Name = "Period"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = True
Attribute VB_PredeclaredId = False
Attribute VB_Exposed = True
'#  $Id: clsPeriod.cls 680 2009-04-29 16:35:09Z re04179 $
'#  $URL: http://subversion.rwe.com/svn/s_and_v_projects/GasNetworks/trunk/app/gnw/vb/gnw_dll/clsPeriod.cls $
'#  $Revision: 680 $
'#  $Date: 2009-04-29 18:35:09 +0200 (Wed, 29 Apr 2009) $
'#  $Author: re04179 $
Option Explicit
Option Base 0
Private Const ModuleVersion As String = "0pt1"

Private m_sIdx As Long
Private m_eIdx As Long

Private Sub Class_Initialize()
    m_sIdx = -1
    m_eIdx = -1
End Sub

Public Property Let StartIdx(val As Long)
    m_sIdx = val
End Property
Public Property Get StartIdx() As Long
    StartIdx = m_sIdx
End Property

Public Property Let EndIdx(val As Long)
    m_eIdx = val
End Property
Public Property Get EndIdx() As Long
    EndIdx = m_eIdx
End Property

Public Property Get AsPair() As Long()
    AsPair = Array(m_sIdx, m_eIdx)
End Property


Public Sub SetPeriod(ByVal sIdx As Long, ByVal eIdx As Long)
    Me.StartIdx = sIdx
    Me.EndIdx = eIdx
End Sub

