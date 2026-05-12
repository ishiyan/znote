// Created by Starlight (extesy@yandex.ru). Don't remove this line even if you do conversion to EL,MQL etc!

function JRSXSeries(Series: integer; Len: integer) : integer;
begin
  var Bar: integer;
  var sName: string;
  var Value: float;
  var f0, f88, f90: integer;
  var f8, f10, f18, f20, f28, f30, f38, f40, f48, f50, f58, f60, f68, f70, f78, f80: float;
  var v4, v8, vC, v10, v14, v18, v1C, v20: float;

  sName := 'JRSX(' + GetDescription(Series) + ',' + FloatToStr(Len) + ')';
  Result := FindNamedSeries(sName);
  if Result >= 0 then Exit;
  Result := CreateNamedSeries(sName);

  for Bar := 0 to BarCount() - 1 do
  begin
    if (f90 = 0) then begin
      f90 := 1;
      f0 := 0;
      if (Len-1 >= 5) then f88 := Len-1 else f88 := 5;
      f8 := 100*@Series[Bar];
      f18 := 3 / (Len + 2);
      f20 := 1 - f18;
    end else begin
      if (f88 <= f90) then f90 := f88 + 1 else f90 := f90 + 1;
      f10 := f8;
      f8 := 100*@Series[Bar];
      v8 := f8 - f10;
      f28 := f20 * f28 + f18 * v8;
      f30 := f18 * f28 + f20 * f30;
      vC := f28 * 1.5 - f30 * 0.5;
      f38 := f20 * f38 + f18 * vC;
      f40 := f18 * f38 + f20 * f40;
      v10 := f38 * 1.5 - f40 * 0.5;
      f48 := f20 * f48 + f18 * v10;
      f50 := f18 * f48 + f20 * f50;
      v14 := f48 * 1.5 - f50 * 0.5;
      f58 := f20 * f58 + f18 * abs(v8);
      f60 := f18 * f58 + f20 * f60;
      v18 := f58 * 1.5 - f60 * 0.5;
      f68 := f20 * f68 + f18 * v18;
      f70 := f18 * f68 + f20 * f70;
      v1C := f68 * 1.5 - f70 * 0.5;
      f78 := f20 * f78 + f18 * v1C;
      f80 := f18 * f78 + f20 * f80;
      v20 := f78 * 1.5 - f80 * 0.5;
      if ((f88 >= f90) and (f8 <> f10)) then f0 := 1;
      if ((f88 = f90) and (f0 = 0)) then f90 := 0;
    end;
    if ((f88 < f90) and (v20 > 1.0e-10)) then begin
      v4 := (v14 / v20 + 1) * 50;
      if (v4 > 100) then v4 := 100;
      if (v4 < 0) then v4 := 0;
    end else
      v4 := 50;
    Value := v4;
    @Result[Bar] := Value;
  end;
end;

function JRSX(Bar: integer; Series: integer; Len: integer): float;
begin
  Result := GetSeriesValue(Bar, JRSXSeries(Series, Len));
end;
