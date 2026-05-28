BASIC code for median-average adaptive filter
for use in NeuroShell Trader

Dim i&, Length&
Dim alpha#, FiltPrev#, Value1#, Value2#, Value2prev#, Value3#
Dim Smooth() As Double
 
  ReDim Smooth(0 To cnt-1)  'Create intermediate arrays
  ReDim sortarray(0 To MAXLENGTH-1) As Double
  For i = 3 To cnt - 1
    Smooth(i) = (@Price[i] + 2 * @Price[i-1] + 2 * @Price[i-2] + @Price[i-3]) / 6
    Length = MAXLENGTH '39
    Value3 = .2
    If i >= Length + 2 Then
      'First good bar requires some initialization of previous values
      If i = Length + 2 Then FiltPrev = Smooth(i-1): Value2prev = Smooth(i-1)
      While Value3 > Threshold
        alpha = 2 / (Length + 1)
        Value1 = Median(Smooth(), i, Length)
        Value2 = alpha * Smooth(i) + (1 - alpha) * Value2prev
        If Value1 <> 0 Then Value3 = Abs(Value1 - Value2) / Value1
        Length = Length - 2
      Wend
      If Length < 3 Then Length = 3
      alpha = 2 / (Length + 1)
      @Filt[i] = alpha * Smooth(i) + (1 - alpha) * FiltPrev
      FiltPrev = @Filt[i]
      Value2prev = Value2
    End If
  Next
 
  Erase Smooth  'Delete arrays
  Erase sortarray