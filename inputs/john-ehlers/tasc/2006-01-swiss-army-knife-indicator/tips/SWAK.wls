WealthScript code:
{$I 'SWAK'}
var Bar, CSW, CSWPane, SPane, OPane, bc, n, hBS, hBP, hGauss, hDiff: integer;
var t, StartFrq, Rate: float;
SetColorScheme( #Green, #Red, #Blue, #Black, #Black, #White );
bc := BarCount;
StartFrq := Trunc( bc / 100 );
Rate := Trunc( bc / 25 );
{* Create and plot a chirped sine wave, decreasing frequency *}
CSW := CreateSeries;
n := bc - 1;
for Bar := 0 to bc - 1 do
begin
  t := Bar / bc;
  @CSW[n] := Sin( 360 * ( StartFrq + t * Rate ) * t );
  Dec( n );
end;
CSWPane := CreatePane( 100, true, true );
PlotSeriesLabel( CSW, CSWPane, #Lime, #Thin, 'Chirped Sine' );
{* Run the Chirped signal through the filters and plot *}
SPane := CreatePane( 100, true, true );
hBS := SWAKSeries( CSW, 21, 'BS' );
PlotSeriesLabel( hBS, SPane, #Red, #Thin, 'SWAK BandStop(21)' );
hBP := SWAKSeries( CSW, 21, 'BP' );
PlotSeriesLabel( hBP, SPane, #Yellow, #Dotted, 'SWAK BandPass(21)' );
{* Predictive oscillator *}
OPane := CreatePane( 100, false, false );
hDiff := SubtractSeries( SWAKSeries( #Close, 19, 'BP' ), SWAKSeries( #Close, 21, 'BP' ) );
PlotSeriesLabel( hDiff, OPane, #Lime, #Histogram, 'SWAK BP(19)-BP(21)' );
{* Plot the SWAK Gaussian of the #Close series *}
hGauss := SWAKSeries( #Close, 50, 'Gauss' );
PlotSeriesLabel( hGauss, 0, #Yellow, #Thin, 'SWAK Gauss(50)' );
HideVolume;