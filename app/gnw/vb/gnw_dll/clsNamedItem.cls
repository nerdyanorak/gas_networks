VERSION 1.0 CLASS
BEGIN
  MultiUse = -1  'True
  Persistable = 0  'NotPersistable
  DataBindingBehavior = 0  'vbNone
  DataSourceBehavior  = 0  'vbNone
  MTSTransactionMode  = 0  'NotAnMTSObject
END
Attribute VB_Name = "NamedItem"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = True
Attribute VB_PredeclaredId = False
Attribute VB_Exposed = True
'#  $Id: clsNamedItem.cls 6679 2010-04-09 07:34:57Z re04179 $
'#  $URL: http://subversion.rwe.com/svn/s_and_v_projects/GasNetworks/trunk/app/gnw/vb/gnw_dll/clsNamedItem.cls $
'#  $Revision: 6679 $
'#  $Date: 2010-04-09 09:34:57 +0200 (Fri, 09 Apr 2010) $
'#  $Author: re04179 $
Option Explicit
Option Base 0
Private Const ModuleVersion As String = "0pt1"

Private pKey As String          ' serves as dictionary key
Private pDims As Integer        ' 0: 0-d array (scalar), 1: 1-d array, 2: 2-d array
Private pSizes As Variant       ' extent of each dimension, array of size pDims
Private pTypes As Variant       ' types of values in data
                                ' supported types are: 'str', 'float', 'int', 'bool', 'NI'
                                ' where 'NI' is an element of type NamedItem (recursive)
                                ' for pDims > 0, pTypes is a Variant array holding type strings,
                                ' otherwise pTypes is a Variant/String holding the type directly.
' The structure of pTypes can be as follows:
' pDims:    Structure:          Size:                   Comment:
'   0       Variant of type
'           String              N/A
'   1       1d Variant array
'           of type String      (1,)                    - homogenous types for all
'                                                       elements in pData
'                               (pSizes(0),)            - individual type for each
'                                                       element in pData
'   2       2d Variant array
'           of type String      (1,1)                   - homogenous types for all
'                                                       elements in pData
'                               (1,pSizes(1))           - homogenous types for each
'                                                       column vector in pData
'                               (pSizes(0),1)           - homogenous types for each
'                                                       row vector in pData
'                               (pSizes(0),pSizes(1))   - individual types for
'                                                       each element in pData

Private pData As Variant        ' holds the data matching the dimensionality, the sizes and types
                                ' as defined by pDims, pSizes and pTypes, respectively
' It is the NamedItemFactory's responsibility to check that these conditions
' are adhered to when creating items of type NamedItem
Private pValidTypes As Variant


Private Sub Class_Initialize()
    pValidTypes = Array("str", "float", "int", "bool", "NI")
End Sub

Private Sub Class_Terminate()
    Clear
End Sub

Public Property Let Key(val As String)
    ' Serves as dictionary key
    pKey = val
End Property
Public Property Let dims(val As Integer)
    ' 0: 0-d array (scalar), 1: 1-d array, 2: 2-d array
    pDims = val
End Property
Public Property Let sizes(val As Variant)
    ' Set extent of each dimension
    ' If Dims = 0 then unused,
    ' otherwise array of size Dims holding
    ' the extents in each dimension of
    ' Data array
    pSizes = val
End Property
Public Property Let types(val As Variant)
    ' Types of values in Data
    ' Supported types are: 'str', 'float', 'int', 'bool', 'NI',
    ' where 'NI' is an element of type NamedItem (recursive).
    ' For Dims > 0, Types is a Variant array holding type strings,
    ' otherwise pTypes is a Variant/String holding the type directly.
    ' The structure of pTypes can be as follows:
    ' Dims:     Structure:          Size:                   Comment:
    '   0       Variant of type
    '           String              N/A
    '   1       1d Variant array
    '           of type String      (1,)                    - homogenous types for all
    '                                                       elements in pData
    '                               (pSizes(0),)            - individual type for each
    '                                                       element in pData
    '   2       2d Variant array
    '           of type String      (1,1)                   - homogenous types for all
    '                                                       elements in pData
    '                               (1,pSizes(1))           - homogenous types for each
    '                                                       column vector in pData
    '                               (pSizes(0),1)           - homogenous types for each
    '                                                       row vector in pData
    '                               (pSizes(0),pSizes(1))   - individual types for
    '                                                       each element in pData
    pTypes = val
End Property
Public Property Let data(val As Variant)
    ' Holds the data matching the dimensionality, the sizes and types
    ' as defined by Dims, Sizes and Types, respectively
    pData = val
    AdjustArray
End Property


Public Property Get Key() As String
    Key = pKey
End Property
Public Property Get dims() As Integer
    dims = pDims
End Property
Public Property Get sizes() As Variant
    sizes = pSizes
End Property
Public Property Get types() As Variant
    types = pTypes
End Property
Public Property Get data() As Variant
    data = pData
End Property
Public Property Get ValidTypes() As Variant
    ' Returns array of strings representing
    ' the valid values for Types
    ValidTypes = pValidTypes
End Property

Public Function AsArrayData(Optional shortForm As Boolean = False) As Variant
    ' Returns Variant/Variant() structure
    ' of given NamedItem in the form of
    '   Array( Key, Array( Dims, Sizes, Types ), Data), if shortForm
    '   Array( 'key', Key, 'attr', Array( 'dims', Dims, 'sizes', Sizes, 'types', Types ), 'data', Data ),
    '       otherwise
    '
    ' If Data itself holds (an array of) NamedItem element(s)
    ' then function is recursively, applied.
    
    Dim tmpData As Variant
    Dim niHdlr As New gnw.NamedItemHdlr
    
    tmpData = Empty
    Select Case Me.dims
        Case 0
            If Me.types = "NI" Then
                tmpData = niHdlr.AsArrayData(Me.data, shortForm)
            Else
                tmpData = Me.data
            End If
        Case 1
            Dim lb As Long, ub As Long, idx As Long
            lb = LBound(Me.types, 1)
            ub = UBound(Me.types, 1)
            
            If Me.sizes(lb) > 0 Then
                Dim homogenousTypes As Boolean
                homogenousTypes = (ub - lb + 1) = 1
                If homogenousTypes Then
                    If Me.types(lb) <> "NI" Then
                        tmpData = Me.data
                    Else
                        ReDim tmpData(lb To lb + Me.sizes(lb) - 1)
                        For idx = lb To lb + Me.sizes(lb) - 1
                            tmpData(idx) = niHdlr.AsArrayData(Me.data(idx), shortForm)
                        Next idx
                    End If
                Else
                    ReDim tmpData(lb To lb + Me.sizes(lb) - 1)
                    For idx = lb To lb + Me.sizes(lb) - 1
                        If Me.types(idx) = "NI" Then
                            tmpData(idx) = niHdlr.AsArrayData(Me.data(idx), shortForm)
                        Else
                            tmpData(idx) = Me.data(idx)
                        End If
                    Next idx
                End If
            End If
        Case 2
            Dim lb1 As Long, ub1 As Long, rowIdx As Long
            Dim lb2 As Long, ub2 As Long, colIdx As Long
            
            lb1 = LBound(Me.types, 1)
            ub1 = UBound(Me.types, 1)
            lb2 = LBound(Me.types, 2)
            ub2 = UBound(Me.types, 2)
            
            Dim homogenousColTypes As Boolean
            homogenousColTypes = (ub1 - lb1 + 1) = 1
            Dim homogenousRowTypes As Boolean
            homogenousRowTypes = (ub2 - lb2 + 1) = 1
            
            If Me.sizes(lb1) > 0 And Me.sizes(lb1 + 1) > 0 Then
                If homogenousColTypes And homogenousRowTypes Then
                    If Me.types(lb1, lb2) <> "NI" Then
                        tmpData = Me.data
                    Else
                        ReDim tmpData(lb1 To lb1 + Me.sizes(lb1) - 1, lb1 To lb1 + Me.sizes(lb1 + 1) - 1)
                        For rowIdx = lb1 To lb1 + Me.sizes(lb1) - 1
                            For colIdx = lb1 To lb1 + Me.sizes(lb1 + 1) - 1
                                tmpData(rowIdx, colIdx) = niHdlr.AsArrayData(Me.data(rowIdx, colIdx), shortForm)
                            Next colIdx
                        Next rowIdx
                    End If
                ElseIf homogenousColTypes Then
                    ReDim tmpData(lb1 To lb1 + Me.sizes(lb1) - 1, lb1 To lb1 + Me.sizes(lb1 + 1) - 1)
                    For colIdx = lb1 To lb1 + Me.sizes(lb1 + 1) - 1
                        If Me.types(lb1, colIdx) = "NI" Then
                            For rowIdx = lb1 To lb1 + Me.sizes(lb1) - 1
                                tmpData(rowIdx, colIdx) = niHdlr.AsArrayData(Me.data(rowIdx, colIdx), shortForm)
                            Next rowIdx
                        Else
                            For rowIdx = lb1 To lb1 + Me.sizes(lb1) - 1
                                tmpData(rowIdx, colIdx) = Me.data(rowIdx, colIdx)
                            Next rowIdx
                        End If
                    Next colIdx
                ElseIf homogenousRowTypes Then
                    ReDim tmpData(lb1 To lb1 + Me.sizes(lb1) - 1, lb1 To lb1 + Me.sizes(lb1 + 1) - 1)
                    For rowIdx = lb1 To lb1 + Me.sizes(lb1) - 1
                        If Me.types(rowIdx, lb1) = "NI" Then
                            For colIdx = lb1 To lb1 + Me.sizes(lb1 + 1) - 1
                                tmpData(rowIdx, colIdx) = niHdlr.AsArrayData(Me.data(rowIdx, colIdx), shortForm)
                            Next colIdx
                        Else
                            For colIdx = lb1 To lb1 + Me.sizes(lb1 + 1) - 1
                                tmpData(rowIdx, colIdx) = Me.data(rowIdx, colIdx)
                            Next colIdx
                        End If
                    Next rowIdx
                Else
                    ReDim tmpData(lb1 To lb1 + Me.sizes(lb1) - 1, lb1 To lb1 + Me.sizes(lb1 + 1) - 1)
                    For rowIdx = lb1 To lb1 + Me.sizes(lb1) - 1
                        For colIdx = lb1 To lb1 + Me.sizes(lb1 + 1) - 1
                            If Me.types(rowIdx, colIdx) = "NI" Then
                                tmpData(rowIdx, colIdx) = niHdlr.AsArrayData(Me.data(rowIdx, colIdx), shortForm)
                            Else
                                tmpData(rowIdx, colIdx) = Me.data(rowIdx, colIdx)
                            End If
                        Next colIdx
                    Next rowIdx
                End If
            End If
    End Select
    
    If shortForm Then
        AsArrayData = Array(Me.Key, _
                            Array(Me.dims, Me.sizes, Me.types), _
                            tmpData)
    Else
        AsArrayData = Array("key", Me.Key, _
                            "attr", Array("dims", Me.dims, _
                                          "sizes", Me.sizes, _
                                          "types", Me.types), _
                            "data", tmpData)
    End If
    Set niHdlr = Nothing
End Function

Private Sub AdjustArray()
    ' This function figures out
    ' what dimensionality and the extents in each
    ' dimensions actually is/are and
    ' increases/decreases the dimensionality of
    ' Data if there is a mismatch with the
    ' dimensionalty held in Dims.
    ' Note: If there is a need to decrease
    ' the dimensionality of Data, information
    ' may get lost.
    
    Dim lb1 As Long, ub1 As Long
    Dim lb2 As Long, ub2 As Long
    Dim rowIdx As Long, colIdx As Long
    Dim actualDims As Integer
    Dim tmpData As Variant
    
    actualDims = 0
    
    lb1 = 0
    ub1 = 0
    lb2 = 0
    ub2 = 0
Dim1Label:
    On Error GoTo Hdlr1DimLabel
    lb1 = LBound(Me.data, 1)
    ub1 = UBound(Me.data, 1)
    actualDims = actualDims + 1
    GoTo Dim2Label
    
Hdlr1DimLabel:
    lb1 = 0
    ub1 = 0
    GoTo ContinueLabel


Dim2Label:
    On Error GoTo Hdlr2Dimlabel
    lb2 = LBound(Me.data, 2)
    ub2 = UBound(Me.data, 2)
    actualDims = actualDims + 1
    GoTo ContinueLabel

Hdlr2Dimlabel:
    lb2 = 0
    ub2 = 0
    GoTo ContinueLabel


ContinueLabel:
    On Error GoTo 0
    Select Case Me.dims
        Case 0
            Select Case actualDims
                Case 0
                    tmpData = data
                Case 1
                    tmpData = data(lb1)
                Case 2
                    tmpData = data(lb1, lb2)
            End Select
        Case 1
            Select Case actualDims
                Case 0
                    tmpData = Array(data)
                Case 1
                    tmpData = data
                Case 2
                    ReDim tmpData(lb1 To ub1)
                    For rowIdx = lb1 To ub1
                        tmpData(rowIdx) = data(rowIdx, lb2)
                    Next rowIdx
            End Select
        Case 2
            Select Case actualDims
                Case 0
                    tmpData = Array(Array(data))
                Case 1
                    tmpData = Array(data)
                Case 2
                    tmpData = data
            End Select
    End Select
    pData = tmpData      ' Must have assignement to pData (member variable)
                            ' not Data (property let), otherwise infinite recursion!
End Sub

Private Sub Clear()
    Select Case Me.dims
        Case 0
            If Me.types = "NI" Then
                Set Me.data = Nothing
            End If
        Case 1
            Dim lb As Long, ub As Long, idx As Long
            lb = LBound(Me.types, 1)
            ub = UBound(Me.types, 1)
            
            If Me.sizes(lb) > 0 Then
                Dim homogenousTypes As Boolean
                homogenousTypes = (ub - lb + 1) = 1
                If homogenousTypes Then
                    If Me.types(lb) = "NI" Then
                        For idx = lb To lb + Me.sizes(lb) - 1
                            Set Me.data(idx) = Nothing
                        Next idx
                    End If
                Else
                    For idx = lb To lb + Me.sizes(lb) - 1
                        If Me.types(idx) = "NI" Then
                            Set Me.data(idx) = Nothing
                        End If
                    Next idx
                End If
            End If
        Case 2
            Dim lb1 As Long, ub1 As Long, rowIdx As Long
            Dim lb2 As Long, ub2 As Long, colIdx As Long
            
            lb1 = LBound(Me.types, 1)
            ub1 = UBound(Me.types, 1)
            lb2 = LBound(Me.types, 2)
            ub2 = UBound(Me.types, 2)
            
            Dim homogenousColTypes As Boolean
            homogenousColTypes = (ub1 - lb1 + 1) = 1
            Dim homogenousRowTypes As Boolean
            homogenousRowTypes = (ub2 - lb2 + 1) = 1
            
            If Me.sizes(lb1) > 0 And Me.sizes(lb1 + 1) > 0 Then
                If homogenousColTypes And homogenousRowTypes Then
                    If Me.types(lb1, lb2) = "NI" Then
                        For rowIdx = lb1 To lb1 + Me.sizes(lb1) - 1
                            For colIdx = lb1 To lb1 + Me.sizes(lb1 + 1) - 1
                                Set Me.data(rowIdx, colIdx) = Nothing
                            Next colIdx
                        Next rowIdx
                    End If
                ElseIf homogenousColTypes Then
                    For colIdx = lb1 To lb1 + Me.sizes(lb1 + 1) - 1
                        If Me.types(lb1, colIdx) = "NI" Then
                            For rowIdx = lb1 To lb1 + Me.sizes(lb1) - 1
                                Set Me.data(rowIdx, colIdx) = Nothing
                            Next rowIdx
                        End If
                    Next colIdx
                ElseIf homogenousRowTypes Then
                    For rowIdx = lb1 To lb1 + Me.sizes(lb1) - 1
                        If Me.types(rowIdx, lb1) = "NI" Then
                            For colIdx = lb1 To lb1 + Me.sizes(lb1 + 1) - 1
                                Set Me.data(rowIdx, colIdx) = Nothing
                            Next colIdx
                        End If
                    Next rowIdx
                Else
                    For rowIdx = lb1 To lb1 + Me.sizes(lb1) - 1
                        For colIdx = lb1 To lb1 + Me.sizes(lb1 + 1) - 1
                            If Me.types(rowIdx, colIdx) = "NI" Then
                                Set Me.data(rowIdx, colIdx) = Nothing
                            End If
                        Next colIdx
                    Next rowIdx
                End If
            End If
    End Select
End Sub
