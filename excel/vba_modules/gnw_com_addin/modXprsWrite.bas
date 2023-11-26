Attribute VB_Name = "modXprsWrite"
Option Explicit
Private Const ModuleVersion As String = "0pt1pt0"

Public Sub xprsWriteValue( _
    coeffDescrFileObj, _
    fileObj, _
    valName As String, _
    valType As String, _
    valData As Variant, _
    Optional arrData As Variant, _
    Optional quotingFlag As Boolean = True, _
    Optional idxHintFlag As Boolean = True)
    
    Dim justValue As Boolean
    justValue = False
    
    If valType <> "array" Then
        Call coeffDescrFileObj.WriteLine(valName + " : [ [ 0 ] [ 1 ] [ " + valType + " ] ]")
    End If
    
    Select Case valType
        Case "float"
            Call xprsWriteValueReal(fileObj, valName, CDbl(valData), justValue)
        Case "int"
            Call xprsWriteValueLong(fileObj, valName, CLng(valData), justValue)
        Case "date"
            Call xprsWriteValueDate(fileObj, valName, CDate(valData), justValue)
        Case "str"
            Call xprsWriteValueString(fileObj, valName, CStr(valData), justValue, quotingFlag)
        Case "bool"
            Call xprsWriteValueBool(fileObj, valName, CBool(valData), justValue)
        Case "array"
            Call xprsWriteValueArray(coeffDescrFileObj, fileObj, valName, valData, arrData, quotingFlag, idxHintFlag)
        Case Else
            Call fileObj.Write("#Unknown valType '" + valType + "'!")
    End Select

End Sub

Private Sub xprsWriteValueReal(fileObj, valName As String, valData As Double, Optional justValue As Boolean = False, _
        Optional format As String = "0.00000000")
    If justValue Then
        Call fileObj.Write(WorksheetFunction.Text(valData, format))
    Else
        Call fileObj.Write(valName + " : " + WorksheetFunction.Text(valData, format))
    End If
End Sub

Private Sub xprsWriteValueLong(fileObj, valName As String, valData As Long, Optional justValue As Boolean = False)
    If justValue Then
        Call fileObj.Write(CStr(valData))
    Else
        Call fileObj.Write(valName + " : " + CStr(valData))
    End If
End Sub

Private Sub xprsWriteValueDate(fileObj, valName As String, valData As Date, Optional justValue As Boolean = False)
    If justValue Then
        Call fileObj.Write(WorksheetFunction.Text(valData, "dd/mm/yyyy"))
    Else
        Call fileObj.Write(valName + " : " + WorksheetFunction.Text(valData, "dd/mm/yyyy"))
    End If
End Sub

Private Sub xprsWriteValueString(fileObj, _
        valName As String, _
        ByVal valData As String, _
        Optional justValue As Boolean = False, _
        Optional quoting As Boolean = True)
    If quoting Then
        valData = "'" + valData + "'"
    End If
    If justValue Then
        Call fileObj.Write(valData)
    Else
        Call fileObj.Write(valName + " : " + valData)
    End If
End Sub

Private Sub xprsWriteValueBool(fileObj, valName As String, valData As Boolean, Optional justValue As Boolean = False)
    Dim valueString As String
    If valData Then
        valueString = "true"
    Else
        valueString = "false"
    End If
    If justValue Then
        Call fileObj.Write(valueString)
    Else
        Call fileObj.Write(valName + " : " + valueString)
    End If
End Sub

Private Sub xprsWriteValueArray( _
    coeffDescrFileObj, fileObj, _
    valName As String, _
    valType As Variant, _
    arrData As Variant, _
    Optional quotingFlag As Boolean = False, _
    Optional idxHintFlag As Boolean = True)
    
    Dim lb1 As Long, ub1 As Long
    Dim lb2 As Long, ub2 As Long
    Dim rows As Long, rowIdx As Long
    Dim cols As Long, colIdx As Long
    
    If False Then
        lb1 = LBound(arrData, 1)
        ub1 = UBound(arrData, 1)
        rows = ub1 - lb1 + 1
        lb2 = LBound(arrData, 2)
        ub2 = UBound(arrData, 2)
        cols = ub2 - lb2 + 1
    Else
        rows = arrData.rows.Count
        lb1 = 1
        ub1 = rows
        cols = arrData.Columns.Count
        lb2 = 1
        ub2 = cols
    End If
    
    Call fileObj.Write(valName + " : ")
    Call fileObj.Write("[ ")
    
    Call coeffDescrFileObj.Write(valName + " : [ ")
    If cols > 1 Then
        Call coeffDescrFileObj.Write("[ 2 ] [ " + CStr(cols) + " ] [ ")
    Else
        Call coeffDescrFileObj.Write("[ 1 ] [ " + CStr(cols) + " ] [ ")
    End If
    For colIdx = lb2 To ub2
        Call coeffDescrFileObj.Write(valType(colIdx) + " ")
    Next colIdx
    Call coeffDescrFileObj.WriteLine("] ]")
    
    For rowIdx = lb1 To ub1
        
        If idxHintFlag And cols > 1 Then
            Call fileObj.Write(" (" + CStr(rowIdx) + ") ")
        End If
        
        If cols > 1 Then
            Call fileObj.Write("[ ")
        End If
        For colIdx = lb2 To ub2
            Select Case valType(colIdx)
                Case "float"
                    Call xprsWriteValueReal(fileObj, valName, CDbl(arrData(rowIdx, colIdx)), True)
                Case "int"
                    Call xprsWriteValueLong(fileObj, valName, CLng(arrData(rowIdx, colIdx)), True)
                Case "date"
                    Call xprsWriteValueDate(fileObj, valName, CDate(arrData(rowIdx, colIdx)), True)
                Case "str"
                    Call xprsWriteValueString(fileObj, valName, CStr(arrData(rowIdx, colIdx)), True, quotingFlag)
                Case "bool"
                    Call xprsWriteValueBool(fileObj, valName, CBool(arrData(rowIdx, colIdx)), True)
                Case Else
                    Call fileObj.Write("#Unknown valType '" + valType + "'!")
            End Select
            If colIdx < ub2 Then
                Call fileObj.Write(" ")
            End If
        Next colIdx
        If cols > 1 Then
            Call fileObj.Write(" ]")
        End If
        If rowIdx < ub1 Then
            fileObj.WriteLine
        End If
    Next rowIdx
    Call fileObj.Write(" ]")
End Sub


