var BAR: integer;

{$I 'InstTrendline'}

SetColorScheme( #Lime, #Red, #Olive, #Black, 021, #Silver );

PlotSeries( InstTrendlineSeries( #Close ), 0, 763, #Thick );

for Bar := 80 to BarCount - 1 do
 if PriceClose( Bar ) > InstTrendLine( Bar, #Close ) then
  SetBarColor( Bar, 494 )
 else
  SetBarColor( Bar, 944 );
