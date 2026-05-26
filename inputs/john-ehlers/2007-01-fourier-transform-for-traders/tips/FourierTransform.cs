const Window = 50;
// Transformed Discrete Fourier Transform -- Dominant Cycle
function TDFT_DCSeries(Series: integer; BuildHeatMap: boolean): integer;
begin
  var Name: string = 'TDFT_DC(' + GetDescription(Series) + ')';
  Result := FindNamedSeries(Name);
  if (Result >= 0) and
    (not BuildHeatMap or (FindNamedSeries(Name + '.8') >= 0)) then exit;
  if Result < 0 then Result := CreateNamedSeries(Name);
  var Period, n, Bar: integer;
  var C, S, DominantCycle: float;
  var HeatMap: array[8..Window] of integer;
  if BuildHeatMap then for Period := 8 to Window do begin
    HeatMap[Period] := AddSeriesValue(CreateNamedSeries(''), Period);
    SetDescription(HeatMap[Period], Name + '.' + IntToStr(Period));
  end;
  // Convert Decibels to RGB Color to Display
  var Color: array[0..18] of integer;
  for n := 0 to 9 do Color[n] := 990 - 10 * n; // yellow to red
  for n := 10 to 18 do Color[n] := 1800 - 100 * n; // red to black
  // Get detrended data by High Pass Filtering with a 40 Period cutoff
  var Alpha: float = (1 - Sin(360 / 40)) / Cos(360 / 40);
  var HP: integer = CreateSeries;
  for Bar := 1 to BarCount - 1 do
    @HP[Bar] := Alpha * @HP[Bar - 1] + Momentum(Bar, Series, 1) * (1 + Alpha) / 2;
  var CleanedData: integer = FIRSeries(HP, '1,2,3,3,2,1');
  // Prepare convolution series for DFT
  var CConv, SConv: array[8..Window] of integer;
  var CSum, SSum: array[8..Window] of float;
  for Period := 8 to Window do begin
    var CW: string = '';
    var SW: string = '';
    CSum[Period] := 1;
    SSum[Period] := 1;
    for n := 0 to Window - 1 do begin
      C := Round(Cos(360 * n / Period) * 100000);
      S := Round(Sin(360 * n / Period) * 100000);
      CW := CW + FloatToStr(C) + ',';
      SW := SW + FloatToStr(S) + ',';
      CSum[Period] := CSum[Period] + C;
      SSum[Period] := SSum[Period] + S;
    end;
    CConv[Period] := FIRSeries(CleanedData, CW + '1');
    SConv[Period] := FIRSeries(CleanedData, SW + '1');
  end;
  for Bar := Window + 4 to BarCount - 1 do begin
    // This is the DFT
    var MaxPwr: float = 0;
    var Pwr: array[8..Window] of float;
    for Period := 8 to Window do begin
      C := GetSeriesValue(Bar, CConv[Period]) * CSum[Period];
      S := GetSeriesValue(Bar, SConv[Period]) * SSum[Period];
      Pwr[Period] := C * C + S * S;
      // Find Maximum Power Level for Normalization
      MaxPwr := max(MaxPwr, Pwr[Period]);
    end;
    // Find Dominant Cycle using CG algorithm
    var Num: float = 0;
    var Den: float = 0;
    for Period := 8 to Window do if (Pwr[Period] > 0) then begin
      // Normalize Power Levels and Convert to Decibels
      var DB: float = 20 + 10 * Log10(1 - 0.99 * Pwr[Period] / MaxPwr);
