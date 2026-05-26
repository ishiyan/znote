Function Script_CreateSignal(Prices())
 
  Dim Signal 'This is the value you are going to calculate
  Dim Ehlers
  PriceCtr = PriceCtr + 1
  Redim Preserve PriceHistory(PriceCtr)
  PriceHistory(PriceCtr) = Prices(2)
  Ehlers = Dakota.EhlersInstTrend(PriceHistory, ParameterValue(1)) +
           Dakota.EhlersHP(PriceHistory, ParameterValue(2))
  if PriorEhlers = 0 then
    PriorEhlers = Ehlers
  end if
  Signal = PriorEhlers - Ehlers
  PriorEhlers = Ehlers
  Script_CreateSignal = Signal
  Exit Function
End Function
