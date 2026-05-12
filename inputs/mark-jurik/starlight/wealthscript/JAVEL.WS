// Created by Starlight (extesy@yandex.ru). Don't remove this line even if you do conversion to EL,MQL etc!

function JAVELSeries(Series: integer; LoLen: integer; HiLen: integer; Sensitivity: float; Period: float): integer;
begin
  var Bar, j, k: integer;
  var sName: string;
  var avg1, avg2, value2, value3: float;
  var eps: float;
  var value1, value4: integer;

  sName := 'JAVEL(' + GetDescription(Series) + ',' + FloatToStr(LoLen) + ',' + FloatToStr(HiLen) + ',' + FloatToStr(Sensitivity) + ')';
  Result := FindNamedSeries(sName);
  if Result >= 0 then Exit;
  Result := CreateNamedSeries(sName);

  eps := 0.001;
  value1 := CreateSeries;
  for Bar := 1 to BarCount() - 1 do
     @value1[Bar] := abs(@Series[Bar] - @Series[Bar-1]);
  value4 := CreateSeries;

  for Bar := 0 to BarCount() - 1 do
  begin
    avg1 := 0;
    if (Bar < 99) then k := Bar else k := 99;
    for j := 0 to k do
       avg1 := avg1 + @value1[Bar-j];
    avg1 := avg1 / (k+1);

    avg2 := 0;
    if (Bar < 9) then k := Bar else k := 9;
    for j := 0 to k do
       avg2 := avg2 + @value1[Bar-j];
    avg2 := avg2 / (k+1);

    value2 := Sensitivity * ln((eps+avg1) / (eps+avg2));
    value3 := value2 / (1 + abs(value2));
    @value4[Bar] := LoLen + (HiLen-LoLen) * (1+value3) / 2;
  end;

  for Bar := 0 to BarCount() - 1 do
    @Result[Bar] := GetSeriesValue(Bar, JXVELaux3(JXVELaux1(Series, value4), Period));
end;

function JAVEL(Bar: integer; Series: integer; LoLen: integer; HiLen: integer; Sensitivity: float; Period: float): float;
begin
  Result := GetSeriesValue(Bar, JAVELSeries(Series, LoLen, HiLen, Sensitivity, Period));
end;
