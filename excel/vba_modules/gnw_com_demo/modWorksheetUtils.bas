Attribute VB_Name = "modWorksheetUtils"
Option Explicit

Function GetVolumeCorrection( _
        startDate As Date, _
        periodStart As Date, periodFinal As Date, _
        periodType As String, boundType As String, _
        mthWrkShtName As String, mthLookupAddress As String, _
        gyWrkShtName As String, gyLookupAddress As String, _
        Optional mthFirmCol As Integer = 2, _
        Optional gyDeltaMUPCol As Integer = 2, _
        Optional gyMUPBalCol As Integer = 3, _
        Optional gyDeltaCFWCol As Integer = 4, _
        Optional gyCFWBalCol As Integer = 5, _
        Optional gyFirmCol As Integer = 6) As Double
    
    Dim rng As Range
    
    GetVolumeCorrection = 0#
    Select Case periodType
    Case "M"
        Dim monthDate As Long
        monthDate = CLng(DateSerial(Year(periodStart), Month(periodStart), 1))
        
        Set rng = Worksheets(mthWrkShtName).Range(mthLookupAddress)
        GetVolumeCorrection = WorksheetFunction.VLookup(monthDate, rng, mthFirmCol, False)
    Case "GY"
        Dim yearOffset As Integer
        yearOffset = 0
        If 1 <= Month(periodStart) And Month(periodStart) <= 9 Then
            yearOffset = -1
        End If
        Dim yearDate As Long
        yearDate = CLng(DateSerial(Year(periodStart) + yearOffset, 10, 1))
        
        Set rng = Worksheets(gyWrkShtName).Range(gyLookupAddress)
        If Len(boundType) > 3 Then
            Select Case UCase(Left(boundType, 2))
            Case "MU"
                GetVolumeCorrection = 0
            Case "CF"
                GetVolumeCorrection = 0
            End Select
        Else
            GetVolumeCorrection = WorksheetFunction.VLookup(yearDate, rng, gyFirmCol, False)
        End If
    End Select
End Function


