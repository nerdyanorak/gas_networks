Attribute VB_Name = "modUtils"
Option Explicit

Private Const ModuleVersion As String = "0pt1pt0"


Function ArraySize(anArray, Optional dimension As Integer = 1) As Long
    If IsEmptyArray(anArray, dimension) Then
        ArraySize = 0
    Else
        ArraySize = UBound(anArray, dimension) - LBound(anArray, dimension) + 1
    End If
End Function

Function IsEmptyArray(anArray, Optional dimension As Integer = 1) As Boolean
    Dim lb As Long, ub As Long
    
    On Error GoTo ErrorHdlr
    lb = LBound(anArray, dimension)
    ub = UBound(anArray, dimension)
    
    IsEmptyArray = (ub - lb + 1) > 0
Exit Function
ErrorHdlr:
    On Error GoTo 0
    IsEmptyArray = False
End Function
