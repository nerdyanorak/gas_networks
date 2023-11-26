Attribute VB_Name = "modWriteInputData"
Option Explicit
Option Base 1

Private Const ModuleVersion As String = "0pt2"


Sub writeAllData()
    Dim quoting As Boolean
    Dim idxHint As Boolean
    If Worksheets("General").Range(["Base"]) = 0 Then
        quoting = False
        idxHint = False
    Else
        quoting = True
        idxHint = True
    End If
    
    Worksheets("General").writeData quotingFlag:=quoting, idxHintFlag:=idxHint
    Worksheets("Network").writeData quotingFlag:=quoting, idxHintFlag:=idxHint
    Worksheets("Storage").writeData quotingFlag:=quoting, idxHintFlag:=idxHint
    Worksheets("Supplier").writeData quotingFlag:=quoting, idxHintFlag:=idxHint
    Worksheets("FirmProfile").writeData quotingFlag:=quoting, idxHintFlag:=idxHint
    Worksheets("Market").writeData quotingFlag:=quoting, idxHintFlag:=idxHint
    Worksheets("DisPatchProduct").writeData quotingFlag:=quoting, idxHintFlag:=idxHint
    Worksheets("Product").writeData quotingFlag:=quoting, idxHintFlag:=idxHint
'    Worksheets("StdPrdDef").writeData quotingFlag:=quoting, idxHintFlag:=idxHint
    Worksheets("TrdTrnDef").writeData quotingFlag:=quoting, idxHintFlag:=idxHint
End Sub


Sub writeDataType1(wsMe As Worksheet, refValsAddr As String, Optional quotingFlag As Boolean = False, Optional idxHintFlag As Boolean = False)
    Dim refRange As Range
    Dim numRows As Long
    Dim rowIdx As Long
    Dim colIdx As Long
    Dim valName As String
    Dim valType As String
    Dim valData As Variant
    Dim valRefAddr As Variant
    Dim valRefRows As Variant
    Dim valRefCols As Variant
    Dim valRefFileName As String
    Dim valRefDataRange As Range
    Dim fileSysObj As Object
    Dim coeffDescrFileName As String
    Dim coeffDescrFileObj As Object
    Dim fileObj As Object
    Dim pos As Double
    Dim ws As Worksheet
    Dim wsName As String
    Dim addr As String
    
    Set refRange = wsMe.Range(refValsAddr)
    numRows = refRange.End(xlDown).Row - refRange.Row + 1
    
    Set fileSysObj = CreateObject("Scripting.FileSystemObject")
    
    coeffDescrFileName = Worksheets("General").Range(["CoeffDescrFile"]).Value
    Set coeffDescrFileObj = fileSysObj.OpenTextFile(coeffDescrFileName, 8, True)
    
    For rowIdx = 1 To numRows
        valName = refRange(rowIdx, 1).Value
        valType = refRange(rowIdx, 2).Value
        
        valData = refRange(rowIdx, 3).Value
        
        valRefAddr = refRange(rowIdx, 3)
        valRefRows = refRange(rowIdx, 4)
        valRefCols = refRange(rowIdx, 5)
        
        Set fileObj = fileSysObj.OpenTextFile(refRange(rowIdx, 0).Value, 8, True)
        
        If valType <> "array" Then
            Call gnw_addin.xprsWriteValue(coeffDescrFileObj, fileObj, valName, valType, valData, , quotingFlag, idxHintFlag)
        Else
            pos = WorksheetFunction.Search("!", CStr(valRefAddr))
            wsName = TrimChar(Left(valRefAddr, pos - 1), "'")
            addr = Mid(valRefAddr, pos + 1)
            
            Set ws = Worksheets(wsName)
            
            ReDim valData(1 To valRefCols) As String
            For colIdx = 1 To valRefCols
                valData(colIdx) = refRange(rowIdx, 5 + colIdx).Value
            Next colIdx
            Set valRefDataRange = ws.Range(ws.Range(addr).Offset(0, 0), ws.Range(addr).Offset(valRefRows - 1, valRefCols - 1))
            Call gnw_addin.xprsWriteValue(coeffDescrFileObj, fileObj, valName, valType, valData, valRefDataRange, quotingFlag, idxHintFlag)
        End If
        fileObj.WriteLine
        
        fileObj.Close
        Set fileObj = Nothing
    Next rowIdx
    
    coeffDescrFileObj.Close
    Set coeffDescrFileObj = Nothing
    
    Set fileSysObj = Nothing
End Sub

Sub writeDataType2(wsMe As Worksheet, _
        typeAddrRef As String, _
        nameAddrRef As String, _
        valsAddrRef As String, _
        Optional quotingFlag As Boolean = False, _
        Optional idxHintFlag As Boolean = False)
    Dim refTypeRange As Range
    Dim refNameRange As Range
    Dim refValsRange As Range
    
    Dim numRows As Long
    Dim rowIdx As Long
    Dim numCols As Long
    Dim colIdx As Long
    Dim valName As String
    Dim valType As String
    Dim val As Variant
    Dim fileSysObj As Object
    Dim coeffDescrFileName As String
    Dim coeffDescrFileObj As Object
    Dim fileObj As Object
    
    Set refTypeRange = wsMe.Range(typeAddrRef)
    Set refNameRange = wsMe.Range(nameAddrRef)
    Set refValsRange = wsMe.Range(valsAddrRef)
    
    numRows = refValsRange.End(xlDown).Row - refValsRange.Row + 1
    numCols = refValsRange.End(xlToRight).Column - refValsRange.Column + 1
    
    Set fileSysObj = CreateObject("Scripting.FileSystemObject")
    
    coeffDescrFileName = Worksheets("General").Range(["CoeffDescrFile"]).Value
    Set coeffDescrFileObj = fileSysObj.OpenTextFile(coeffDescrFileName, 8, True)
    
    For rowIdx = 1 To numRows
        Set fileObj = fileSysObj.OpenTextFile(refValsRange(rowIdx, 0).Value, 8, True)
        
        For colIdx = 1 To numCols
            valName = refNameRange(1, colIdx).Value
            valType = refTypeRange(1, colIdx).Value
            val = refValsRange(rowIdx, colIdx)
        
            Call gnw_addin.xprsWriteValue(coeffDescrFileObj, fileObj, valName, valType, val, , quotingFlag, idxHintFlag)
            fileObj.WriteLine
        Next colIdx
        
        fileObj.Close
        Set fileObj = Nothing
    Next rowIdx
    
    coeffDescrFileObj.Close
    Set coeffDescrFileObj = Nothing
    
    Set fileSysObj = Nothing
End Sub

Function TrimChar(str As String, char As String) As Variant
    TrimChar = str
    While Left(TrimChar, 1) = char
        TrimChar = Right(TrimChar, Len(TrimChar) - 1)
    Wend
    While Right(TrimChar, 1) = char
        TrimChar = Left(TrimChar, Len(TrimChar) - 1)
    Wend
End Function
