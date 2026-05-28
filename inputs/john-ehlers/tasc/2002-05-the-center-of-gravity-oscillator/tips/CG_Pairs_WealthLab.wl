var BESTSYMBOL, PRIMARY, SECONDARY: string;
var CORR, BESTCORR: float;
var I: integer;
BestCorr := 0;
BestSymbol := 'None';
Primary := GetSymbol;
for i := 0 to WatchListCount - 1 do
begin
  Secondary := WatchListSymbol( i );
  if Primary <> Secondary then
  begin
    Corr := Correlation( #Close, GetExternalSeries( Secondary, #Close ), 0,
BarCount - 1 );
    if Corr > BestCorr then
    begin
      BestCorr := Corr;
      BestSymbol := Secondary;
    end;
  end;
end;
DrawLabel( 'Best Correlated: ' + BestSymbol, 0 );
DrawLabel( '30 Day Correlation: ' + FormatFloat( '#0.00', BestCorr ), 0 );
DrawLabel( '30 Day HV ' + GetSymbol + ': ' + FormatFloat( '#0.00', HV(
BarCount - 1, #Close, 30 ) ), 0 );
SetPrimarySeries( BestSymbol );
DrawLabel( '30 Day HV ' + BestSymbol + ': ' + FormatFloat( '#0.00', HV(
BarCount - 1, #Close, 30 ) ), 0 );

var SYM2: string;
var CORR, LAST, LAST2, CLOSE, CLOSE2, X, XHV1, XHV2, XR, VB: float;
var SPREAD, VBSERIES, C1, C2, CORRSERIES, BAR, HV1, HV2, VBNEG, SPREADPANE,
HVPANE: integer;
Sym2 := 'EBAY';
Spread := CreateSeries;
VBSeries := CreateSeries;
{ 30 Day HV and Correleation }
SetScaleDaily;
C1 := OffsetSeries( #Close, -1 );
SetPrimarySeries( Sym2 );
C2 := OffsetSeries( #Close, -1 );
CorrSeries := CreateSeries;
for Bar := 30 to BarCount - 1 do
begin
  corr := Correlation( C1, C2, Bar - 30, Bar );
  SetSeriesValue( Bar, CorrSeries, corr );
end;
HV1 := IntradayFromDaily( HVSeries( C1, 30 ) );
HV2 := IntradayFromDaily( HVSeries( C2, 30 ) );
CorrSeries := IntradayFromDaily( CorrSeries );
RestorePrimarySeries;
{ Calculate Spread and VB }
Last := 0.0;
Last2 := 0.0;
for Bar := 20 to BarCount - 1 do
begin
  if Last > 0 then
  begin
    Close := PriceClose( Bar );
    SetPrimarySeries( Sym2 );
    Close2 := PriceClose( Bar );
    RestorePrimarySeries;
    x := ( Last / Close ) - ( Last2 / Close2 );
    SetSeriesValue( Bar, Spread, x );
  end;
  if LastBar( Bar ) then
  begin
    Last := PriceClose( Bar );
    SetPrimarySeries( Sym2 );
    Last2 := PriceClose( Bar );
    RestorePrimarySeries;
  end;
  xHV1 := GetSeriesValue( Bar, HV1 );
  xHV2 := GetSeriesValue( Bar, HV2 );
  xR := GetSeriesValue( Bar, CorrSeries );
  VB := ( xHV1 + xHV2 ) * Sqrt( 1 / 252 ) * ( 1 - xR );
  VB := VB * 1.5;
  SetSeriesValue( Bar, VBSeries, VB );
end;
VBNeg := MultiplySeriesValue( VBSeries, -1 );
{ Trading Rules }
for Bar := 725 to BarCount - 1 do
begin
  if LastPositionActive then
  begin
    if LastBar( Bar ) then
    begin
      SellAtClose( Bar, LastPosition, '' );
      SellAtClose( Bar, LastPosition - 1, '' );
    end;
  end
  else
  begin
    if CrossOver( Bar, Spread, VBSeries ) then
    begin
      BuyAtMarket( Bar + 1, '' );
      SetPrimarySeries( Sym2 );
      ShortAtMarket( Bar + 1, '' );
      RestorePrimarySeries;
    end
    else if CrossUnder( Bar, Spread, VBNeg ) then
    begin
      ShortAtMarket( Bar + 1, '' );
      SetPrimarySeries( Sym2 );
      BuyAtMarket( Bar + 1, '' );
      RestorePrimarySeries;
    end;
  end;
end;
{ Plot Spread }
SpreadPane := CreatePane( 75, false, true );
PlotSeries( Spread, SpreadPane, 202, #Thick );
DrawLabel( 'Spread', SpreadPane );
PlotSeries( VBSeries, SpreadPane, #Silver, #Thin );
PlotSeries( VBNeg, SpreadPane, #Silver, #Thin );
{ Plot HV }
HVPane := CreatePane( 75, false, true );
PlotSeries( HV1, HVPane, #Black, #Thick );
DrawText( 'HV ' + GetSymbol, HVPane, 4, 4, #Black, 8 );
DrawText( 'HV ' + Sym2, HVPane, 54, 4, #Red, 8 );
DrawText( 'Correlation', HVPane, 104, 4, #Green, 8 );
PlotSeries( HV2, HVPane, #Red, #Thick );
PlotSeries( CorrSeries, HVPane, #Green, #Thick );
