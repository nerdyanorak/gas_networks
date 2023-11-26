Attribute VB_Name = "modNamedItemArray"
Option Explicit
Option Base 1
Private Const ModuleVersion As String = "0pt1pt0"

Public Function NamedItemArrayType1(refCell As String, worksheetName As String) As Variant
    Dim refRange As Range
    Dim numRows As Long
    Dim rowIdx As Long
    
    Dim valName As String
    Dim valType As String
    Dim valData As Variant

    Dim valRefAddr As Variant
    Dim valRefRows As Variant
    Dim valRefCols As Variant

    Dim niHdlr As New gnw.NamedItemHdlr
    Dim niArray() As Variant
    
    Set refRange = Worksheets(worksheetName).Range(refCell)
    numRows = refRange.End(xlDown).Row - refRange.Row + 1
    
    ReDim niArray(1 To numRows)
    
    For rowIdx = 1 To numRows
        valName = refRange(rowIdx, 1).Value
        valType = refRange(rowIdx, 2).Value
        
        valData = refRange(rowIdx, 3).Value
        
        valRefAddr = refRange(rowIdx, 3)
        valRefRows = refRange(rowIdx, 4)
        valRefCols = refRange(rowIdx, 5)
        
        
        If valType <> "array" Then
            Set niArray(rowIdx) = niHdlr.Create(valName, valType, valData)
        Else
            Dim pos As Integer
            Dim wsName As String
            Dim addr As String
            Dim ws As Worksheet
            Dim colIdx As Long
            Dim valRefDataRange As Range

            pos = WorksheetFunction.Search("!", CStr(valRefAddr))
            wsName = Left(valRefAddr, pos - 1)
            addr = Mid(valRefAddr, pos + 1)
            
            Set ws = Worksheets(wsName)
            
            ReDim valData(1 To valRefCols) As String
            For colIdx = 1 To valRefCols
                valData(colIdx) = refRange(rowIdx, 5 + colIdx).Value
            Next colIdx
            
            Set valRefDataRange = ws.Range(ws.Range(addr).Offset(0, 0), ws.Range(addr).Offset(valRefRows - 1, valRefCols - 1))
            Set niArray(rowIdx) = niHdlr.Create(valName, valType, valData, valRefDataRange)
        End If
    Next rowIdx

    NamedItemArrayType1 = niArray
End Function

Public Function NamedItemArrayType1b(refCell As String, worksheetName As String, numBlocks As Integer, numEntriesPerBlock As Integer) As Variant
    Dim refRange As Range
    Dim numRows As Long
    Dim blockIdx As Long
    Dim entryIdx As Long
    Dim blockName As String
    
    Dim rowIdx As Long
    
    Dim valName As String
    Dim valType As String
    Dim valData As Variant

    Dim valRefAddr As Variant
    Dim valRefRows As Variant
    Dim valRefCols As Variant

    Dim niHdlr As New gnw.NamedItemHdlr
    Dim niBlockArray() As Variant
    Dim niEntriesArray() As Variant
    
    Set refRange = Worksheets(worksheetName).Range(refCell)
    numRows = refRange.End(xlDown).Row - refRange.Row + 1
        
    If numBlocks * numEntriesPerBlock <> numRows Then
        Err.Raise vbObjectError + 1101, "::NamedItemArrayType1b", "#numBlocks*numEntriesPerBlock does not match numRows implied by refCell!"
    End If
    
    ReDim niBlockArray(1 To numBlocks)
    For blockIdx = 1 To numBlocks
        ReDim niEntriesArray(1 To numEntriesPerBlock)
        For entryIdx = 1 To numEntriesPerBlock
            rowIdx = (blockIdx - 1) * numEntriesPerBlock + entryIdx
            
            valName = refRange(rowIdx, 1).Value
            valType = refRange(rowIdx, 2).Value
            
            valData = refRange(rowIdx, 3).Value
            
            valRefAddr = refRange(rowIdx, 3)
            valRefRows = refRange(rowIdx, 4)
            valRefCols = refRange(rowIdx, 5)
            
            ' It is assumed that the first element in
            ' each block holds the name for the block
            ' in the valData element
            If entryIdx = 1 Then
                blockName = valData
            End If
            
            If valType <> "array" Then
                Set niEntriesArray(entryIdx) = niHdlr.Create(valName, valType, valData)
            Else
                Dim pos As Integer
                Dim wsName As String
                Dim addr As String
                Dim ws As Worksheet
                Dim colIdx As Long
                Dim valRefDataRange As Range
    
                pos = WorksheetFunction.Search("!", CStr(valRefAddr))
                wsName = Left(valRefAddr, pos - 1)
                addr = Mid(valRefAddr, pos + 1)
                
                Set ws = Worksheets(wsName)
                
                ReDim valData(1 To valRefCols) As String
                For colIdx = 1 To valRefCols
                    valData(colIdx) = refRange(rowIdx, 5 + colIdx).Value
                Next colIdx
                
                Set valRefDataRange = ws.Range(ws.Range(addr).Offset(0, 0), ws.Range(addr).Offset(valRefRows - 1, valRefCols - 1))
                Set niEntriesArray(entryIdx) = niHdlr.Create(valName, valType, valData, valRefDataRange)
            End If
        Next entryIdx
        Set niBlockArray(blockIdx) = niHdlr.Create(blockName, "array", Array("NI"), niEntriesArray)
    Next blockIdx
    
    NamedItemArrayType1b = niBlockArray
End Function

Public Function NamedItemArrayType2(refNameCell As String, refTypeCell As String, refValCell As String, worksheetName As String) As Variant

    Dim refNameRange As Range
    Dim refTypeRange As Range
    Dim refValRange As Range
    
    Dim numRows As Long
    Dim rowIdx As Long
    Dim numCols As Long
    Dim colIdx As Long
    
    Dim valName As String
    Dim valType As String
    Dim varVal As Variant
    
    Dim niHdlr As New gnw.NamedItemHdlr
    Dim niArray() As Variant
    Dim niSubArray() As Variant
    
    Set refNameRange = Worksheets(worksheetName).Range(refNameCell)
    Set refTypeRange = Worksheets(worksheetName).Range(refTypeCell)
    Set refValRange = Worksheets(worksheetName).Range(refValCell)
    
    numRows = refValRange.End(xlDown).Row - refValRange.Row + 1
    numCols = refValRange.End(xlToRight).Column - refValRange.Column + 1
    
    ReDim niArray(1 To numRows)
    
    For rowIdx = 1 To numRows
        ReDim niSubArray(1 To numCols)
        For colIdx = 1 To numCols
            valName = refNameRange(1, colIdx).Value
            valType = refTypeRange(1, colIdx).Value
            varVal = refValRange(rowIdx, colIdx).Value
        
            Set niSubArray(colIdx) = niHdlr.Create(valName, valType, varVal)
        Next colIdx
        Set niArray(rowIdx) = niHdlr.Create(refValRange(rowIdx, 1).Value, "array", Array("NI"), niSubArray)
    Next rowIdx
    
    NamedItemArrayType2 = niArray
End Function

