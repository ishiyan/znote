// Created by Starlight (extesy@yandex.ru). Don't remove this line even if you do conversion to EL,MQL etc!

function JDMXplusSeries(Series: Integer; Len: Integer): integer;
begin
  var upward, numer, denom, Bar: integer;
  var sName: string;
  var v1, v2, Value: float;

  sName := 'JDMXplus(' + GetDescription(Series) + ',' + IntToStr(Len) + ')';
  Result := FindNamedSeries(sName);
  if Result >= 0 then Exit;
  Result := CreateNamedSeries(sName);

  upward := CreateSeries;
  for Bar := 1 to BarCount() - 1 do begin
    v1 := 100 * (PriceHigh(Bar) - PriceHigh(Bar-1));
    v2 := 100 * (PriceLow(Bar-1) - PriceLow(Bar));
    if ((v1 > v2) and (v1 > 0)) then @upward[Bar] := v1 else @upward[Bar] := 0;
  end;

  numer := JJMASeries(upward, Len, -100);
  denom := JJMASeries(TrueRangeSeries, Len, -100);

  for Bar := 0 to BarCount() - 1 do
  begin
    if (@denom[Bar] > 0.00001) and (Bar > 40) then Value := 100 * @numer[Bar] / @denom[Bar]
    else Value := 0;
    @Result[Bar] := Value;
  end;
end;

function JDMXminusSeries(Series: Integer; Len: Integer): integer;
begin
  var downward, numer, denom, Bar: integer;
  var sName: string;
  var v1, v2, Value: float;

  sName := 'JDMXminus(' + GetDescription(Series) + ',' + IntToStr(Len) + ')';
  Result := FindNamedSeries(sName);
  if Result >= 0 then Exit;
  Result := CreateNamedSeries(sName);

  downward := CreateSeries;
  for Bar := 1 to BarCount() - 1 do begin
    v1 := 100 * (PriceHigh(Bar) - PriceHigh(Bar-1));
    v2 := 100 * (PriceLow(Bar-1) - PriceLow(Bar));
    if ((v2 > v1) and (v2 > 0)) then @downward[Bar] := v2 else @downward[Bar] := 0;
  end;

  numer := JJMASeries(downward, Len, -100);
  denom := JJMASeries(TrueRangeSeries, Len, -100);

  for Bar := 0 to BarCount() - 1 do
  begin
    if (@denom[Bar] > 0.00001) and (Bar > 40) then Value := 100 * @numer[Bar] / @denom[Bar]
    else Value := 0;
    @Result[Bar] := Value;
  end;
end;

function JDMXSeries(Series: Integer; Len: Integer): integer;
begin
  var DMXplus, DMXminus, Bar: integer;
  var sName: string;
  var Value: float;

  sName := 'JDMX(' + GetDescription(Series) + ',' + IntToStr(Len) + ')';
  Result := FindNamedSeries(sName);
  if Result >= 0 then Exit;
  Result := CreateNamedSeries(sName);

  DMXplus := JDMXplusSeries(Series, Len);
  DMXminus := JDMXminusSeries(Series, Len);

  for Bar := 0 to BarCount() - 1 do
  begin
    if (@DMXplus[Bar] + @DMXminus[Bar] > 0.00001) then
      Value := 100 * (@DMXplus[Bar] - @DMXminus[Bar]) / (@DMXplus[Bar] + @DMXminus[Bar])
    else Value := 0;
    @Result[Bar] := Value;
  end;
end;

function JDMX(Bar: integer; Series: Integer; Len: Integer): float;
begin
  Result := GetSeriesValue(Bar, JDMXSeries(Series, Len));
end;
