'# Cumulative
'# Period = UserInput.Integer = 20
'# Delta = UserInput.Single = 0.5
'# Fraction = UserInput.Single = 0.1
Static gamma As Single
Static alpha As Single
Static beta As Single
Static BP(2,2) As Single
Static Offset(2) As Integer
Static Trend As Single
Static Peak(1) As Single
Static Valley(1) As Single
Static AvgPeak As Single
Static AvgValley As Single
If isFirstBar Then
	beta = Math.Cos((360 / Period) * Math.PI / 180)
	gamma = 1 / Math.Cos((720 * delta / Period) * Math.PI / 180)
	alpha = gamma - ((gamma * gamma - 1) ^ .5)
	BP(2, 0) = 0
	BP(1, 0) = 0
	BP(0, 0) = 0
	BP(2, 1) = 0
	BP(1, 1) = 0
	BP(0, 1) = 0
	BP(2, 2) = 0
	BP(1, 2) = 0
	BP(0, 2) = 0
	Offset(0) = 2 * Period
	Offset(1) = Math.Max(Offset(0) + 1, 50)
	Offset(2) = Offset(0) + 2
	Trend = 0
	Peak(0) = 0
	Peak(1) = 0
	Valley(0) = 0
	Valley(1) = 0
	AvgPeak = 0
	AvgValley = 0
End If
If CurrentIndex >= 2 Then
	BP(2, 0) = BP(1, 0)
	BP(1, 0) = BP(0, 0)
	BP(0, 0) = .5 * (1 - alpha) * (Price.High + Price.Low _
		- Price.High(2) - Price.Low(2)) / 2 _
		+ beta * (1 + alpha) * BP(1, 0) - alpha * BP(2, 0)
	Trend += BP(0, 0) / Offset(0)
	If BP(1, 0) > BP(0, 0) AndAlso BP(1, 0) > BP(2, 0) Then Peak(0) = BP(1, 0)
	AvgPeak += Peak(0) / 50
	If BP(1, 0) < BP(0, 0) AndAlso BP(1, 0) < BP(2, 0) Then Valley(0) = BP(1, 0)
	AvgValley += Valley(0) / 50
	If CurrentIndex >= Offset(2) Then
		BP(2, 1) = BP(1, 1)
		BP(1, 1) = BP(0, 1)
		BP(0, 1) = .5 * (1 - alpha) * (Price.High(Offset(0)) + Price.Low(Offset(0)) _
			- Price.High(Offset(2)) - Price.Low(Offset(2))) / 2 _
			+ beta * (1 + alpha) * BP(1, 1) - alpha * BP(2, 1)
		Trend -= BP(0, 1) / Offset(0)
	End If
	If CurrentIndex >= 52 Then
		BP(2, 2) = BP(1, 2)
		BP(1, 2) = BP(0, 2)
		BP(0, 2) = .5 * (1 - alpha) * (Price.High(50) + Price.Low(50) _
			- Price.High(52) - Price.Low(52)) / 2 _
			+ beta * (1 + alpha) * BP(1, 2) - alpha * BP(2, 2)
		If BP(1, 2) > BP(0, 2) AndAlso BP(1, 2) > BP(2, 2) Then Peak(1) = BP(1, 2)
		AvgPeak -= Peak(0) / 50
		If BP(1, 2) < BP(0, 2) AndAlso BP(1, 2) < BP(2, 2) Then Valley(1) = BP(1, 2)
		AvgValley -= Valley(0) / 50
	End If
End If
If CurrentIndex >= Offset(1) Then
	OpenValue = Trend
	HighValue = Fraction * AvgPeak
	LowValue = Fraction * AvgValley
	Plot = Trend
Else
	OpenValue = Single.NaN
	HighValue = Single.NaN
	LowValue = Single.NaN
	Plot = Single.NaN
End If
