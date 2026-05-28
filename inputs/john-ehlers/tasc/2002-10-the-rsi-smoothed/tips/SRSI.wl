var i, Bar, CU, CD, CUSmooth, CDSMooth, MyRSI, SRSI, RSPane: integer;

var x, sumup, sumdown, Diff: float;

{ Create our Price Series }

CU := CreateSeries;

CD := CreateSeries;

MyRSI := CreateSeries;

SRSI := CreateSeries;

const PERIOD = 14;

{ Accumulate the "up" and "down" differences }

for Bar := PERIOD + 1 to BarCount - 1 do

begin

  sumup := 0;

  sumdown := 0;

  for i := 0 to PERIOD - 1 do

  begin

    Diff := PriceClose( Bar - i ) - PriceClose( Bar - i - 1 );

    if Diff > 0 then

      sumup := sumup + Diff

    else

      sumdown := sumdown + ( -Diff );

  end;

  @CU[Bar] := sumup;

  @CD[Bar] := sumdown;

end;

{ Smooth differences with the FIR filter }

CDSmooth := FIRSeries( CD, '1,2,2,1' );

CUSmooth := FIRSeries( CU, '1,2,2,1' );

{ Construct Unsmoothed and Smoothed RSI }

for Bar := PERIOD + 1 to BarCount - 1 do

begin

  x := @CU[Bar] / @CD[Bar];

  x := 100 - ( 100 / ( 1 + x ) );

  @MyRSI[Bar] := x;

  x := @CUSmooth[Bar] / @CDSmooth[Bar];

  x := 100 - ( 100 / ( 1 + x ) );

  @SRSI[Bar] := x;

end;

{ Plot Classic, Non-Exponential and Smoothed RSI }

RSPane := CreatePane( 200, true, true );

PlotSeries( RSISeries( #Close, 14 ), RSPane, 558, #Thin );

DrawText( 'Classic Wilder RSI', RSPane, 4, 4, 558, 12 );

PlotSeries( MyRSI, RSPane, 855, #Thin );

DrawText( 'Non-Exponential RSI', RSPane, 4, 24, 855, 12 );

PlotSeries( SRSI, RSPane, #Black, #Thick );

DrawText( 'SRSI', RSPane, 4, 44, #Black, 12 );
Three Bar: '1,1,1'

Four Bar: '1,2,2,1'

Six Bar: '1,2,3,3,2,1'