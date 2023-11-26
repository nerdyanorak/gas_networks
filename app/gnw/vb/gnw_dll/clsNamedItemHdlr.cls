VERSION 1.0 CLASS
BEGIN
  MultiUse = -1  'True
  Persistable = 0  'NotPersistable
  DataBindingBehavior = 0  'vbNone
  DataSourceBehavior  = 0  'vbNone
  MTSTransactionMode  = 0  'NotAnMTSObject
END
Attribute VB_Name = "NamedItemHdlr"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = True
Attribute VB_PredeclaredId = False
Attribute VB_Exposed = True
'#  $Id: clsNamedItemHdlr.cls 1998 2009-09-15 08:12:04Z re04179 $
'#  $URL: http://subversion.rwe.com/svn/s_and_v_projects/GasNetworks/trunk/app/gnw/vb/gnw_dll/clsNamedItemHdlr.cls $
'#  $Revision: 1998 $
'#  $Date: 2009-09-15 10:12:04 +0200 (Tue, 15 Sep 2009) $
'#  $Author: re04179 $
Option Explicit
Option Base 0
Private Const ModuleVersion As String = "0pt1"

Public Function Create( _
    valKey As String, _
    valType As String, _
    valData As Variant, _
    Optional arrData As Variant) As NamedItem
    ' Creates a NamedItem.
    ' valKey: key or the name of the NamedItem
    ' valType: is one of the type string given in gnw.NamedItem.ValidTypes()
    '   (except 'NI') or the string 'array'.
    ' valData: If valType is 'array' then the actual
    '   type specification is given in parameter valData and the
    '   data is given in optional parameter arrData. Otherwise,
    '   valData holds the atomic data item of type as given in valType
    '   (arrData is not used)
    ' arrData: is a 1-d or 2-d array if parameter valType is 'array'.
    '   The type information is given in parameter valData.
    '   For a 1-d data array valType can be either a string from
    '   gnw.NamedItems.ValidTypes() (except 'NI'), specifying that
    '   data in arrData is homogenous of given type, or an
    '   variant array of strings of gnw.NamedItems.ValidTypes()
    '   (excpet 'NI') of the same shape and size as arrData,
    '   specifying that data is in-homogenous and of given types.
    '
    ' Return: gnw.NamedItem
    
    Dim ni As NamedItem
    Set ni = Nothing
    
    If valType = "array" Then
        Set ni = CreateArray(valKey, valData, arrData)
    Else
        If IsEmpty(valData) Then
            Set ni = CreateScalar(valKey, valType, valData)
        Else
        Select Case valType
            Case "str", "NI"
                Set ni = CreateScalar(valKey, valType, valData)
            Case "float"
                Set ni = CreateScalar(valKey, valType, CDbl(valData))
            Case "bool"
                Set ni = CreateScalar(valKey, valType, CBool(valData))
            Case "int"
                Set ni = CreateScalar(valKey, valType, CLng(valData))
            Case Else
                Err.Raise vbObjectError + 1001, "NamedItemHdlr::Create", "#Unknown valType '" + valType + "'!"
        End Select
        End If
    End If
    
    Set Create = ni
End Function


Public Function AsArrayData(niData As Variant, Optional shortForm As Boolean = False) As Variant
    ' Transforms element(s) given in parameter niData
    ' into gnw.NamedItem.AsArrayData() format.
    ' niData: is either a gnw.NamedItem or a 1-d or a
    '   d-2 Variant array of NamedItem. In this case
    '   AsArrayData calls itself recursively on
    '   the elements given in niData and returns
    '   an Variant array of NamedItems in
    '   AsArrayData format, having the same array
    '   structure as the input data.
    ' shortForm: flag indicating whether keywords
    '   'key', 'attr', 'dims', 'sizes', 'types' and 'data'
    '   are included in array data representation
    ' (not shortForm) or not (shortForm
    '
    ' Returns: [1/2-d Variant array of] gnw.NamedItem.AsArrayData(shortForm)
    '
    Dim lb1 As Long, ub1 As Long
    Dim lb2 As Long, ub2 As Long
    Dim rowIdx As Long, colIdx As Long
    Dim actualDims As Integer
    Dim tmpData As Variant
    Dim niDataType As VbVarType
    
    actualDims = 0
    
    lb1 = 0
    ub1 = 0
    lb2 = 0
    ub2 = 0
Dim1Label:
    On Error GoTo Hdlr1DimLabel
    lb1 = LBound(niData, 1)
    ub1 = UBound(niData, 1)
    actualDims = actualDims + 1
    GoTo Dim2Label
    
Hdlr1DimLabel:
    lb1 = 0
    ub1 = 0
    GoTo ContinueLabel


Dim2Label:
    On Error GoTo Hdlr2Dimlabel
    lb2 = LBound(niData, 2)
    ub2 = UBound(niData, 2)
    actualDims = actualDims + 1
    GoTo ContinueLabel
    
Hdlr2Dimlabel:
    lb2 = 0
    ub2 = 0
    GoTo ContinueLabel


ContinueLabel:
    On Error GoTo 0

    Dim niTupleArray As Variant
    Select Case actualDims
        Case 0
            niTupleArray = niData.AsArrayData(shortForm)
        Case 1
            ReDim niTupleArray(lb1 To ub1)
            For rowIdx = lb1 To ub1
                niTupleArray(rowIdx) = Me.AsArrayData(niData(rowIdx), shortForm)
            Next rowIdx
        Case 2
            ReDim niTupleArray(lb1 To ub1, lb2 To ub2)
            For rowIdx = lb1 To ub1
                For colIdx = lb2 To ub2
                    niTupleArray(rowIdx, colIdx) = Me.AsArrayData(niData(rowIdx, colIdx), shortForm)
                Next colIdx
            Next rowIdx
    End Select
    
    AsArrayData = niTupleArray
End Function

Private Function CreateScalar( _
    aKey As String, _
    aType As String, _
    aValue As Variant) As NamedItem
    
    Set CreateScalar = CreateNamedItem(aKey, 0, Array(), aType, aValue)
End Function

Private Function CreateEmptyArray(valName As String, valType As Variant, arrData As Variant) As gnw.NamedItem
    Dim ni As gnw.NamedItem
    Select Case getVarArrayNumDims(valType)
    Case 1
        Set ni = Create1dArray(valName, 0, valType, Empty)
    Case 2
        Set ni = Create2dArray(valName, 0, 0, valType, Empty)
    Case Else
    End Select

    Set CreateEmptyArray = ni
End Function

Private Function CreateDataArray(valName As String, valType As Variant, arrData As Variant) As gnw.NamedItem
    Dim ni As NamedItem

    Dim varTypeVal As Integer
    varTypeVal = VarType(arrData)
    
    Dim lb1 As Long, ub1 As Long
    Dim lb2 As Long, ub2 As Long
    Dim numRows As Long
    Dim numCols As Long
    If Not IsObject(arrData) And varTypeVal >= vbArray Then
        lb1 = 0
        ub1 = 0
        lb2 = 0
        ub2 = 0
        numRows = 0
        numCols = 0
        
ArrayDataDim1:
        On Error GoTo ArrayDataEnd
        lb1 = LBound(arrData, 1)
        ub1 = UBound(arrData, 1)
        numRows = ub1 - lb1 + 1
        numCols = 1

ArrayDataDim2:
        On Error GoTo ArrayDataEnd
        lb2 = LBound(arrData, 2)
        ub2 = UBound(arrData, 2)
        numCols = ub2 - lb2 + 1

ArrayDataEnd:
    Else
        lb1 = 1
        lb2 = 1
        ub1 = arrData.Rows.Count
        ub2 = arrData.Columns.Count
        
        numRows = ub1 - lb1 + 1
        numCols = ub2 - lb2 + 1
    End If

    If numCols > 1 Then
        Dim lb As Long, ub As Long
        lb = LBound(valType, 1)
        ub = UBound(valType, 1)
        
        Dim numTypes As Long
        numTypes = ub - lb + 1
        
        Dim valType2d As Variant
        ReDim valType2d(lb1 To lb1, lb2 To lb2 + numTypes - 1)
        Dim idx As Long
        For idx = lb2 To lb2 + numTypes - 1
            valType2d(lb1, idx) = valType(lb + idx - lb2)
        Next idx
        
        Set ni = Create2dArray(valName, numRows, numCols, valType2d, arrData)
    Else
        Set ni = Create1dArray(valName, numRows, valType, arrData)
    End If
    
    Set CreateDataArray = ni
End Function

Private Function CreateArray(valName As String, valType As Variant, arrData As Variant) As NamedItem
    Dim ni As NamedItem
    If IsEmpty(arrData) Then
        Set ni = CreateEmptyArray(valName, valType, arrData)
    Else
        Set ni = CreateDataArray(valName, valType, arrData)
    End If
    Set CreateArray = ni
End Function

Private Function Create1dArray( _
    aKey As String, _
    aSize As Long, _
    aTypeArray As Variant, _
    a1dDataArray As Variant) As NamedItem
    
    Dim lb As Long
    lb = LBound(aTypeArray, 1)
    Dim arrSize As Variant
    ReDim arrSize(lb To lb)
    arrSize(lb) = aSize
    Set Create1dArray = CreateNamedItem(aKey, 1, arrSize, aTypeArray, a1dDataArray)
End Function
    
Private Function Create2dArray( _
    aKey As String, _
    numRows As Long, _
    numCols As Long, _
    aTypeArray As Variant, _
    a2dDataArray As Variant) As NamedItem
    
    Dim lb As Long
    lb = LBound(aTypeArray, 1)
    Dim arrSize As Variant
    ReDim arrSize(lb To lb + 1)
    arrSize(lb + 0) = numRows
    arrSize(lb + 1) = numCols
    Set Create2dArray = CreateNamedItem(aKey, 2, arrSize, aTypeArray, a2dDataArray)
End Function

Private Function CreateNamedItem( _
    Optional theKey As String = "", _
    Optional numDimensions As Integer = 0, _
    Optional theSizes As Variant, _
    Optional theTypes As Variant, _
    Optional theData As Variant) As NamedItem
    
    Set CreateNamedItem = New NamedItem
    CreateNamedItem.Key = theKey
    CreateNamedItem.dims = numDimensions
    CreateNamedItem.sizes = theSizes
    CreateNamedItem.types = theTypes
    CreateNamedItem.data = theData
End Function

