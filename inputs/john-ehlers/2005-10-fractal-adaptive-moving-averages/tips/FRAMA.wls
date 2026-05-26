WealthScript Code:
{$I 'FRAMA'}
var Bar, ROCPane: integer;
var F:integer = FRAMASeries(#Close, 20, 4.6);
var R:integer = ROCSeries(F, 5);
PlotSeriesLabel(F, 0, #red, #thick, 'FRAMA(Close,20,4.6)');
ROCPane:=CreatePane(75,true,true);
PlotSeriesLabel(R, ROCPane, #red, #thin,'ROC(FRAMA,5)');
for Bar := 20 to BarCount - 1 do
begin
  if not LastPositionActive then
    begin
    if @R[Bar] > 0.5 then BuyAtMarket(Bar+1, 'entry signal');
    end
  else
    begin
    if @R[Bar] < 0 then SellAtMarket(Bar+1, LastPosition, 'exit signal');
    end;
end;