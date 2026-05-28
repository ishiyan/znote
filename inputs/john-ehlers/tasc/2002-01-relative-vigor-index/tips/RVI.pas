var RVIPANE, RVISER, RVISIG, BAR: integer;
{ Plot RVI on the Chart }
RVIPane := CreatePane( 100, true, true );
RVISer := RVISeries( 10 );
PlotSeries( RVISer, RVIPane, #Navy, #Thick );
DrawLabel( 'RVI( 20 )', RVIPane );
{ Create Signal Line using Finite Impulse Response Function }
RVISig := FIRSeries( RVISer, '1,2,2,1' );
PlotSeries( RVISig, RVIPane, #Black, #Thin );
{ A Simple 1 Position Trading System Based on RVI/Signal Line }
InstallBreakevenStop( 3 );
for Bar := 15 to BarCount - 1 do
begin
 ApplyAutoStops( Bar );
 if not LastPositionActive then
 begin
  if RVI( Bar - 1, 10 ) < -0.4 then
   if CrossOver( Bar, RVISer, RVISig ) then
    BuyAtMarket( Bar + 1, 'RVI Buy' );
 end
 else
 begin
  if RVI( Bar - 1, 10 ) > 0 then
   if CrossUnder( Bar, RVISer, RVISig ) then
    SellAtMarket( Bar + 1, LastPosition, 'RVI Sell' );
 end;
end;