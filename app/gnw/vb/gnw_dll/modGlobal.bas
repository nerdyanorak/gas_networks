Attribute VB_Name = "modGlobal"
'#  $Id: modGlobal.bas 1860 2009-09-07 12:09:18Z re04179 $
'#  $URL: http://subversion.rwe.com/svn/s_and_v_projects/GasNetworks/trunk/app/gnw/vb/gnw_dll/modGlobal.bas $
'#  $Revision: 1860 $
'#  $Date: 2009-09-07 14:09:18 +0200 (Mon, 07 Sep 2009) $
'#  $Author: re04179 $
Option Explicit
Option Base 0
Private Const ModuleVersion As String = "0pt1"

Public Function getVarArrayNumDims(varArray As Variant) As Variant
    Dim ub As Long
    Dim dimension As Integer
    dimension = 0
    While True
        dimension = dimension + 1
        On Error GoTo InvalidDimension
            ub = UBound(varArray, dimension)
        On Error GoTo 0
    Wend
    
InvalidDimension:
    getVarArrayNumDims = dimension - 1
End Function

Public Function getVarArrayBase(varArray As Variant, Optional dimension As Integer = 1) As Variant
    Dim lb As Integer
    
    If 1 <= dimension And dimension <= getVarArrayNumDims(varArray) Then
        getVarArrayBase = LBound(varArray, dimension)
    End If

NoArrayFound:
End Function

Public Function getVarArraySize(varArray As Variant, Optional dimension As Integer = 1) As Long
    Dim lb As Long
    Dim ub As Long
    
    If 1 <= dimension And dimension <= getVarArrayNumDims(varArray) Then
        lb = LBound(varArray, dimension)
        ub = UBound(varArray, dimension)
        getVarArraySize = ub - lb + 1
    End If

NoArrayFound:
End Function

Public Function getVarArray1D(size As Long, Optional dfltVal As Variant, Optional base As Long = 0) As Variant
    ReDim getVarArray(base To base + size - 1)
    If Not IsMissing(dfltVal) Then
        Dim idx As Long
        For idx = base To base + size - 1
            getVarArray(idx) = dfltVal
        Next idx
    End If
End Function

