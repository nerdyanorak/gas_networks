Attribute VB_Name = "modWriteResultData"
Option Explicit
Option Base 1

Private Const ModuleVersion As String = "0pt2"


Sub writeResultsTransposed(rslt As Variant, sheetName As String, refCell As String)
    Dim ws As Worksheet
    Set ws = Worksheets(sheetName)
    Dim rng As Range
    Set rng = ws.Range(refCell)
    
    clearContents ws, rng
    
    Dim rdx As Long
    Dim cdx As Long
    
    Dim lb1 As Long
    Dim ub1 As Long
    lb1 = LBound(rslt, 1)
    ub1 = UBound(rslt, 1)
    Dim nCols As Long
    nCols = ub1 - lb1 + 1
    
    Dim lb2 As Long
    Dim ub2 As Long
    lb2 = LBound(rslt, 2)
    ub2 = UBound(rslt, 2)
    Dim nRows As Long
    nRows = ub2 - lb2 + 1
    
    ReDim rsltT(1 To nRows, 1 To nCols) As Variant
    
    For cdx = 0 To nCols - 1
        For rdx = 0 To nRows - 1
            ' Transpose output
            rsltT(rdx + 1, cdx + 1) = rslt(cdx, rdx)
        Next rdx
    Next cdx
    Worksheets(sheetName).Range(rng, rng.Offset(nRows - 1, nCols - 1)) = rsltT
    
End Sub


Sub writeResults(rslt As Variant, sheetName As String, refCell As String)
    Dim ws As Worksheet
    Set ws = Worksheets(sheetName)
    Dim rng As Range
    Set rng = ws.Range(refCell)
    
    clearContents ws, rng
    
    Dim rdx As Long
    Dim cdx As Long
    
    Dim lb1 As Long
    Dim ub1 As Long
    Dim lb2 As Long
    Dim ub2 As Long
    lb1 = LBound(rslt, 1)
    ub1 = UBound(rslt, 1)
    lb2 = LBound(rslt, 2)
    ub2 = UBound(rslt, 2)
    Dim nRows As Long
    Dim nCols As Long
    nRows = ub1 - lb1 + 1
    nCols = ub2 - lb2 + 1
    
'    For rdx = 0 To nRows - 1
'        For cdx = 0 To nCols - 1
'            rng.Offset(rdx, cdx).Value = rslt(rdx, cdx)
'        Next cdx
'    Next rdx

    Worksheets(sheetName).Range(rng, rng.Offset(nRows - 1, nCols - 1)) = rslt
    
End Sub


Sub clearContents(ws As Worksheet, rng As Range)
    Dim activeWS As Worksheet
    Set activeWS = Application.ActiveSheet
    
    ws.Activate
    rng.Select
    Range(Selection, Selection.End(xlDown)).Select
    Range(Selection, Selection.End(xlToRight)).Select
    Selection.clearContents
    activeWS.Activate
    
End Sub

