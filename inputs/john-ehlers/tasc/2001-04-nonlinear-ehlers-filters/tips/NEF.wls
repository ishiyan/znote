{ Create a Price Series to hold Absolute 5 day momentum }
AbsMom5 := CreateSeries();

{ Populate the Price Series }
for Bar := 6 to BarCount() - 1 do
        SetSeriesValue( Bar, AbsMom5, Abs( PriceAverage( Bar ) - PriceAverage(
Bar - 5 ) ) );

{ Obtain 5 day Abs Momentum multipled by Average Price }
PriceTimesMomentum5 := MultiplySeries( PriceAverage(), AbsMom5 );

{ Create Price Series to hold Ehlers Filter }
EhlersFilter := CreateSeries();

{ Populate Ehlers Filter Price Series }
for Bar := 25 to BarCount() - 1 do
begin
        xSumPM := Sum( Bar, PriceTimesMomentum5, 15 );
        xSumM := Sum( Bar, AbsMom5, 15 );
        SetSeriesValue( Bar, EhlersFilter, xSumPM / xSumM );
end;

{ Plot it }
PlotSeries( EhlersFilter, 0, #Teal, 2 );
DrawText( �Ehlers Filter', 0, 4, 34, #Teal, 8 );