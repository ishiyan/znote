'# Year = UserInput.Integer = 2008
'# Month = UserInput.Integer = 1
'# Day = UserInput.Integer = 1
'# Leave the Hour, Minute, Second values set to 0 for MIDAS.
'# Hour = UserInput.Integer = 0
'# Minute = UserInput.Integer = 0
'# Second = UserInput.integer = 0
Static StartDate As Date
Static CumPrice As Double
Static CumVolume As Double
If isFirstBar Then
        StartDate = New Date(Year,Month,Day,Hour,Minute,Second)
        CumPrice = 0
        CumVolume = 0
End If
If CurrentDate >= StartDate Then
        CumPrice += Price.Last * Volume
        CumVolume += Volume
        Plot = CumPrice / CumVolume
Else
        Plot = Single.NaN
End If
