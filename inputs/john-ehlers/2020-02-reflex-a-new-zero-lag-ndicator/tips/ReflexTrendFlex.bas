'REFLEX: A NEW ZERO-LAG INDICATOR
'Author: John F. Ehlers
'Coded by: Richard Denning 12/15/19
'TradersEdgeSystems.com

Function EHLERS_REFLEX(Length)
    Dim Slope As BarArray
    Dim theSum As BarArray
    Dim count As BarArray
    Dim a1 As BarArray
    Dim b1 As BarArray
    Dim c1 As BarArray
    Dim c2 As BarArray
    Dim c3 As BarArray
    Dim Filt As BarArray
    Dim MS As BarArray
    Dim Reflex As BarArray

    If BarNumber=FirstBar Then
        'Length = 20
        Slope = 0
        theSum = 0
        count = 0
        a1 = 0
        b1 = 0
        c1 = 0
        c2 = 0
        c3 = 0
        Filt = 0
        MS = 0
        Reflex = 0
    End If

    a1 = Exp(-1.414*3.14159 / (.5*Length))
    b1 = 2*a1*TStation_Cosine(1.414*180 / (.5*Length))
    c2 = b1
    c3 = -a1*a1
    c1 = 1 - c2 - c3
    Filt = c1*(Close + Close[1]) / 2 + c2*Filt[1] + c3*Filt[2]
'Length is assumed cycle period
    Slope = (Filt[Length] - Filt) / Length
'Sum the differences
    theSum = 0
    For count = 1 To Length
        theSum = theSum + (Filt + count*Slope) - Filt[count]
    Next
    theSum = theSum / Length
'Normalize in terms of Standard Deviations
    MS = .04*theSum*theSum + .96*MS[1]
    If MS <> 0 Then
        Reflex = theSum / Sqr(MS)
    End If
    EHLERS_REFLEX = Reflex
End Function
'--------------------------------------------------------------
Function EHLERS_TRENDFLEX(Length)
    Dim theSum As BarArray
    Dim count As BarArray
    Dim a1 As BarArray
    Dim b1 As BarArray
    Dim c1 As BarArray
    Dim c2 As BarArray
    Dim c3 As BarArray
    Dim Filt As BarArray
    Dim MS As BarArray
    Dim Trendflex As BarArray

    If BarNumber=FirstBar Then
        'Length = 20
        theSum = 0
        count = 0
        a1 = 0
        b1 = 0
        c1 = 0
        c2 = 0
        c3 = 0
        Filt = 0
        MS = 0
        Trendflex = 0
    End If
'Gently smooth the data in a SuperSmoother
    a1 = Exp(-1.414*3.14159 / (.5*Length))
    b1 = 2*a1*TStation_Cosine(1.414*180 / (.5*Length))
    c2 = b1
    c3 = -a1*a1
    c1 = 1 - c2 - c3
    Filt = c1*(Close + Close[1]) / 2 + c2*Filt[1] + c3*Filt[2]
'Sum the differences
    theSum = 0
    For count = 1 To Length
        theSum = theSum + Filt - Filt[count]
    Next
    theSum = theSum / Length
'Normalize in terms of Standard Deviations
    MS = .04*theSum*theSum + .96*MS[1]
    If MS <> 0 Then
        Trendflex = theSum / Sqr(MS)
    End If
 EHLERS_TRENDFLEX = Trendflex
End Function
'--------------------------------------------------------------
'Indicator plot for REFLEX:
Sub REFLEX_IND(length)
Dim Reflex As BarArray
Reflex = EHLERS_REFLEX(20)
Plot1(Reflex)
Plot2(0)
End Sub
'---------------------------------------------------------------
'Indicaotr plot for TRENDFLEX:
Sub TRENDFLEX_IND(length)
Dim Trendflex As BarArray
Trendflex = EHLERS_TRENDFLEX(20)
Plot1(Trendflex)
Plot2(0)
End Sub
'--------------------------------------------------------------
Function TSTATION_COSINE(TSdegrees)
TSTATION_COSINE = Cos(DegToRad(TSdegrees))
End Function
'--------------------------------------------------------------
