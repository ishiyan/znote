WealthScript code:
{$I 'CyclicComponent'}
var Bar: integer;
var CCPane: integer = CreatePane(100, false, false);
var CC: integer = CyclicComponentSeries(#Average, 20);
var ITL: integer = InstantaneousTrendLineSeries(#Average, 20);
var ITL1: integer = OffsetSeries(ITL, 2);
PlotSeriesLabel(ITL, 0, #Blue, #Thin, 'Instant Trend Line (Average,20)');
PlotSeriesLabel(ITL1, 0, #Red, #Thin, 'Instant Trend Line delayed by 2 (Average,20)');
PlotSeriesLabel(CC, CCPane, #Red, #Thin, 'Cyclical component (Average,20)');
HideVolume;
for Bar := 20 to BarCount - 1 do
begin
  if not LastPositionActive then
  begin
  If CrossOver(Bar, ITL1, ITL) then BuyAtMarket(Bar + 1, 'Uptrend signal');
  end
  else
  begin
  If CrossUnder(Bar, ITL1, ITL) then SellAtMarket(Bar + 1, LastPosition, 'Downtrend signal');
  end;
end;
