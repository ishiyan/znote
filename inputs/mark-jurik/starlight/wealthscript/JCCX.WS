// Created by Starlight (extesy@yandex.ru). Don't remove this line even if you do conversion to EL,MQL etc!

function JCCXSeries(Series: Integer; Len: Integer): integer;
begin
  var Bar: integer;
  var sName: string;
  var Value: float;

  sName := 'JCCX(' + GetDescription(Series) + ',' + IntToStr(Len) + ')';
  Result := FindNamedSeries(sName);
  if Result >= 0 then Exit;
  Result := CreateNamedSeries(sName);

  var k, abars, ser, diff: integer;
  var md: float;

  diff := SubtractSeries(JJMASeries(Series, 4, 0), JJMASeries(Series, Len, 0));

  for Bar := 1 to BarCount() - 1 do
  begin
    if (Bar < 3*Len) then abars := Bar else abars := 3*Len;
    md := 0;
    for k := 0 to abars-1 do
      md := md + abs(@diff[Bar-k]);
    md := md * 1.5 / abars;
    if (md > 0.00001) then Value := @diff[Bar] / md else Value := 0;
    @Result[Bar] := Value;
  end;
end;

function JCCX(Bar: integer; Series: Integer; Len: Integer): float;
begin
  Result := GetSeriesValue(Bar, JCCXSeries(Series, Len));
end;
