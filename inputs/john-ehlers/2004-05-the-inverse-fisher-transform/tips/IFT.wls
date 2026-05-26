{$I 'CyberCycle'}
{$I 'InverseFisher'}
var
  Bar, p, hRSI, hRSIx, hIF_RSI, RSIPane,
  hIF_CC, CCPane, hCCPane, hCC, hCCD: integer;
{ ---- Setup indicators ---- }
hCC := DivideSeriesValue( AddSeries( #High, #Low ), 2 );
hCC := CyberCycleSeries( hCC, 0.07 );
hCCD := OffsetSeries( hCC, -1 ); // delay 1 bar
hIF_CC := InverseFisherSeries( hCC );
hRSI := RSISeries( #Close, 5 );
hRSIx := SubtractSeriesValue( WMASeries( hRSI, 9 ), 50 );
hRSIx := MultiplySeriesValue( hRSIx, 0.1 );
hIF_RSI := InverseFisherSeries( hRSIx );
{ ---- Plot control ---- }
RSIPane  := CreatePane( 100, false, true );
hCCPane := CreatePane( 75, false, true );
CCPane := CreatePane( 75, false, true );
PlotSeriesLabel( hCCD, hCCPane, #Blue, #Thick, 'hCCD=hCC delayed' );
PlotSeriesLabel( hCC, hCCPane, #Teal, #Thick, 'hCC=CyberCycle((H+L)/2,0.07)' );
PlotSeriesLabel( hIF_CC, CCPane, #Red, #Thick, 'hIF_CC=InvFisher(hCC)' );
PlotSeriesLabel( hIF_RSI, RSIPane, #Red, #Thick, 'hIF_RSI=IF(RSI(5))' );
HideVolume;
{ Inverse Fisher RSI System }
for Bar := 40 to BarCount - 1 do
  if LastPositionActive then
  begin
    p := LastPosition;
    if CrossUnderValue( Bar, hIF_RSI, 0.5 )
    or CrossUnderValue( Bar, hIF_RSI, -0.5 ) then
      SellAtMarket( Bar + 1, p, '' );
  end
  else if CrossOverValue( Bar, hIF_RSI, -0.5 ) then
      BuyAtMarket( Bar + 1, '' );
